#!/usr/bin/env bash
# Full run of PEMA v3.0.0 on the 93 Turkish pond eDNA runs (12S-V5 vertebrate marker) of ENA project PRJNA1495761
# (PONDERFUL; Cuenca-Cambronero et al. 2026, Nature Ecology & Evolution, doi:10.1038/s41559-026-03197-w;
# Turkish fieldwork METU Limnology Laboratory / EKOSAM).
# Same settings as the 3-run test (pema_test.yaml): Swarm, RDP classifier with the 12S_v200 database, rootless Podman.
# 1. downloads the reads (about 4.4 GB) into reads_all/, skipping files already there and checking each file's MD5;
# 2. runs PEMA; output in results_all/ (main table rdp_assignment/tax_assigned_table.tsv); log in all_run.log.
# Safe to run again: downloads skip finished files and Nextflow resumes finished steps.
# Usage: bash run_pema_all.sh [all|download|pema]   (Snakefile calls the two stages separately)
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # this repository
cd "$D"
STAGE="${1:-all}"
df -h "$D" | tail -1

if [ "$STAGE" != pema ]; then
python3 -I - <<'EOF'
import csv, hashlib, json, os, time, urllib.request
os.makedirs("reads_all", exist_ok=True)
url = ("https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA1495761&result=read_run"
       "&fields=run_accession,sample_alias,country,fastq_ftp,fastq_md5&format=json")
runs = [r for r in json.load(urllib.request.urlopen(url)) if r["country"].startswith("Turkey")]
print(f"{len(runs)} Turkish runs")
def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
# Some ENA paths answer with an empty directory listing instead of the file (seen for SRR39644106 read 2):
# each file is tried twice; a run whose files cannot be fetched intact is listed in failed_runs.tsv and its
# files are removed, since PEMA refuses a sample with one mate only. Such runs can be fetched later from NCBI SRA.
failed = []
for n, r in enumerate(runs, 1):
    outs = []
    ok = True
    for i, (ftp, m) in enumerate(zip(r["fastq_ftp"].split(";"), r["fastq_md5"].split(";")), 1):
        out = f"reads_all/{r['sample_alias']}_{r['run_accession']}_{i}.fastq.gz"
        outs.append(out)
        if os.path.exists(out) and md5(out) == m:
            continue
        for attempt in (1, 2, 3, 4):
            time.sleep(2)                      # ENA answers 403 to bursts of downloads
            try:
                urllib.request.urlretrieve("https://" + ftp, out + ".part")
            except OSError as e:
                print(f"  download error {out}: {e}; waiting {60 * attempt} s", flush=True)
                time.sleep(60 * attempt)
                continue
            if md5(out + ".part") == m:
                os.replace(out + ".part", out)
                break
        else:
            ok = False
            break
    if not ok:
        for f in outs + [o + ".part" for o in outs]:
            if os.path.exists(f):
                os.remove(f)
        failed.append(r)
        print(f"[{n}/{len(runs)}] {r['sample_alias']} {r['run_accession']} FAILED (MD5), skipped", flush=True)
        continue
    print(f"[{n}/{len(runs)}] {r['sample_alias']} {r['run_accession']} {r['country']}", flush=True)
with open("reads_all/failed_runs.tsv", "w") as f:
    f.write("sample_alias\trun_accession\tcountry\n")
    for r in failed:
        f.write(f"{r['sample_alias']}\t{r['run_accession']}\t{r['country']}\n")
print(f"{len(runs) - len(failed)} runs downloaded, {len(failed)} skipped (reads_all/failed_runs.tsv)", flush=True)
with open("reads_all/runs_turkey.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["sample_alias", "run_accession", "country"])
    for r in runs:
        w.writerow([r["sample_alias"], r["run_accession"], r["country"]])
EOF
fi
df -h "$D" | tail -1

if [ "$STAGE" != download ]; then
mkdir -p work_all && sed "s|__REPO__|$D|g" pema_all.yaml > work_all/params.yaml
cd pema
pixi run --manifest-path ../pixi.toml nextflow -log ../work_all.nextflow.log run pema.nf \
  -ansi-log false \
  --params-file ../work_all/params.yaml \
  -profile podman,reports \
  -c ../podman.config \
  -work-dir ../work_all \
  -resume 2>&1 | tee ../all_run.log
df -h "$D" | tail -1
fi

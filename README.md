# ankara-ponds-edna (prototype)

Test of LifeWatch ERIC's metabarcoding pipeline PEMA on public eDNA data from Türkiye: 93 runs (29 ponds, 6 sites west of
Ankara, May–June 2022, 12S-V5 vertebrate marker) sampled by METU (Beklioğlu, Avcı) for PONDERFUL
(Cuenca-Cambronero et al. 2026, *Nature Ecology & Evolution*, doi:10.1038/s41559-026-03197-w; reads ENA PRJNA1495761).
Our analysis of public data, open to correction by the METU team. The field observations of the same ponds are restricted until
15 January 2027.

Site: <https://annefou.github.io/ankara-ponds-edna/>. Installation and running: see **Install and run** below.

## Steps

1. `run_pema_all.sh` (started with `start_full_run.sh`): downloads the 93 runs from ENA (MD5-checked, retries on 403)
   and runs PEMA v3.0.0 (Swarm, RDP classifier with the 12S_v200 database, rootless Podman, `podman.config`).
   Output: `results_all/rdp_assignment/tax_assigned_table.tsv`.
2. `scripts/blast_check.py`: the main ASV of each taxon (101 ASVs) BLAST-searched against NCBI core_nt;
   `analysis/blast_check.tsv`. PEMA's 12S reference lacks several Anatolian amphibians (Triturus, Ommatotriton,
   Pelobates, Bufotes, Emys), which BLAST resolves at 98–100 % identity.
3. `pixi run python scripts/pond_summary.py`: per-pond groups (`analysis/pond_table.tsv`) and
   `figures/ponds_edna_map.png`.

## Main results (30 October 2026)

- Water frogs (Pelophylax, genus level) in 26 ponds; crested newts (Triturus) 15; banded newt (Ommatotriton) 13;
  toads 7; tree frog 7; spadefoot (Pelobates) 6; European pond turtle (Emys orbicularis) 4.
- Fish in 23 of 29 ponds; topmouth gudgeon (Pseudorasbora parva, non-native, FishBase) in 19; Carassius 16; carp 11.
- Ponds without fish: 3.7 amphibian groups on average; with fish: 2.7.
- Human DNA 20 % of reads (handling); livestock above 1 % of non-human reads in 8 ponds.

## Nanopublication chain (draft)

A FORRT chain is drafted in `nanopubs/drafts/` (`nanopubs/chain-draft.json`, `pixi run build-chain-draft`): the
claim that amphibian species and fish presence in the PONDERFUL ponds were identified by eDNA metabarcoding, and
this re-analysis with PEMA as the replication study. The Outcome waits for the paper's per-pond detections, restricted
until 15 January 2027; nothing is published yet. Geographical coverage: `nanopubs/drafts/09_geo_coverage.md`.

## Install and run

You can read the results without installing anything: the PEMA tables are in `results_all/`, the BLAST check and the
pond table in `analysis/`, the map in `figures/`, and the [Jupyter Book](https://annefou.github.io/ankara-ponds-edna/)
shows them. **No account is needed** for any step: the ENA reads, the PEMA containers, the 12S reference and NCBI
BLAST are all public.

### Requirements

- Linux (x86-64): the pixi environment is solved for `linux-64`, and PEMA runs through Nextflow and rootless Podman.
- pixi (<https://pixi.sh>): `curl -fsSL https://pixi.sh/install.sh | bash`.
- Rootless Podman, for PEMA's containers: `sudo apt install podman` on Ubuntu. Apptainer, which PEMA also supports, is
  blocked by AppArmor on recent Ubuntu, so this repository uses Podman (`podman.config` tells Nextflow to look for
  short image names on Docker Hub).
- Disk: about 4.4 GB for the 93 runs, plus PEMA's intermediate files (`work_all/`, several times that). Time: a few
  hours for PEMA on 8 threads (`threads` in `pema_all.yaml`).

### Install

```bash
git clone https://github.com/annefou/ankara-ponds-edna.git
cd ankara-ponds-edna
pixi install
git clone https://github.com/hariszaf/pema.git pema && git -C pema checkout 9b9e649     # PEMA v3.0.0
```

The 12S reference: download `12S_v200.tar.gz` from Zenodo record 23298141
(<https://zenodo.org/records/23298141>) and unpack it into `rdp_databases/`, so that `rdp_databases/12S_v200/`
exists.

### Run

The steps are in `Snakefile`:

```bash
pixi run pema-test                    # optional: PEMA on 3 runs (TR12, TR24, TR26) to check Podman and the reference
pixi run snakemake --cores 1          # ENA download (4.4 GB), PEMA (hours), NCBI BLAST check, pond table and map
pixi run summary                      # only the pond table and map, from the committed PEMA and BLAST tables
pixi run snakemake --cores 1 --dry-run   # what would run, without running it
```

| Rule | What it does | Account |
| --- | --- | --- |
| `reads` | the 93 Turkish runs of ENA PRJNA1495761, checked against ENA's MD5 sums, retried when ENA throttles with HTTP 403 (runs that still fail: `reads_all/failed_runs.tsv`) | none |
| `pema` | PEMA v3.0.0 through Nextflow and rootless Podman; Nextflow resumes finished steps | none |
| `blast` | the main ASV of each taxon against NCBI core_nt (megablast); a few minutes in NCBI's queue | none |
| `pond_summary` | `analysis/pond_table.tsv`, `figures/ponds_edna_map.png` | none |

PEMA is long and writes to the terminal, which pauses a job started in the background; for an unattended run use
`bash start_full_run.sh` (detached; progress in `full_run.log`) and `bash restart_full_run.sh` to restart it. The
paths in `pema_*.yaml` start with `__REPO__`, which the scripts replace with the repository's folder.

### Docker

The image holds the pixi environment, the code and the committed tables:

```bash
docker run --rm ghcr.io/annefou/ankara-ponds-edna:latest          # pixi run summary, inside the image
docker run --rm -v "$PWD/out:/out" ghcr.io/annefou/ankara-ponds-edna:latest \
    sh -c "pixi run summary && cp analysis/pond_table.tsv figures/ponds_edna_map.png /out/"   # keep the outputs
```

The default command is `pixi run summary` (pond table and map). PEMA is not run inside the image: it starts its own containers through
Nextflow, so run the full Snakefile on the host. The image is published on GitHub's container registry with each
release.

### What is not in git

The reads, PEMA, the 12S database, the pixi environment and PEMA's intermediate files (see `.gitignore`).

### Caveats

Read counts are not abundances; primers were left in the reads; 12S cannot separate Anatolian water frogs or
*Carassius* species; no field validation yet.

"""Independent check of PEMA's 12S assignments: the main ASV of each taxon is BLAST-searched against NCBI nt.

For every taxon name in PEMA's table (results_all/rdp_assignment/tax_assigned_table.tsv) the ASV with the most reads
is selected, plus the 10 most abundant ASVs that PEMA could not resolve below phylum. The sequences go to NCBI's
public BLAST URL API (megablast, core_nt, 10 hits) in one query; no account or e-mail is sent. Writes
analysis/blast_check.tsv: ASV, reads, PEMA name, best NCBI hit (species, % identity, query coverage), the
species of all hits within 0.5 % of the best identity, and whether PEMA and NCBI agree at genus level.

Usage: python3 scripts/blast_check.py   (from ankara-ponds-edna/; takes a few minutes, NCBI queues the search)
"""
import csv
import json
import time
import urllib.parse
import urllib.request

TAB = "results_all/rdp_assignment/tax_assigned_table.tsv"
FASTA = "results_all/asvs_representatives.fa"
HASH = "results_all/asvs_contingency_hash.tsv"
URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

rows = list(csv.reader(open(TAB), delimiter="\t"))
header, rows = rows[0], rows[1:]
reads = {r[0]: sum(int(v) for v in r[1:-1]) for r in rows}
tax = {r[0]: r[-1] for r in rows}
seed = {r[0]: r[1] for r in csv.reader(open(HASH), delimiter="\t") if r[0] != "ASV"}
seqs, h = {}, None
for line in open(FASTA):
    line = line.strip()
    if line.startswith(">"):
        h = line[1:].split()[0]
    elif h:
        seqs[h] = seqs.get(h, "") + line

best = {}
for asv, t in tax.items():
    name = t.split("; ")[-1]
    if name not in best or reads[asv] > reads[best[name]]:
        best[name] = asv
picked = set(best.values())
unresolved = [a for a in sorted(tax, key=lambda a: -reads[a]) if len(tax[a].split("; ")) <= 3][:10]
picked |= set(unresolved)
picked = sorted(picked, key=lambda a: -reads[a])
query = "".join(f">{a}\n{seqs[seed[a]]}\n" for a in picked if seed.get(a) in seqs)
print(f"{len(picked)} ASVs sent to NCBI BLAST")


def call(params):
    data = urllib.parse.urlencode(params).encode()
    return urllib.request.urlopen(urllib.request.Request(URL, data=data), timeout=300).read().decode()


put = call({"CMD": "Put", "PROGRAM": "blastn", "MEGABLAST": "on", "DATABASE": "core_nt", "QUERY": query,
            "HITLIST_SIZE": 10, "TOOL": "pema-12s-check"})
rid = put.split("RID = ")[1].split()[0]
print("RID", rid, flush=True)
while True:
    time.sleep(60)
    info = call({"CMD": "Get", "FORMAT_OBJECT": "SearchInfo", "RID": rid})
    if "Status=READY" in info:
        break
    if "Status=FAILED" in info or "Status=UNKNOWN" in info:
        raise SystemExit("BLAST search failed")
    print("waiting...", flush=True)
res = call({"CMD": "Get", "FORMAT_TYPE": "JSON2_S", "RID": rid})
json.dump(json.loads(res), open("analysis/blast_raw.json", "w"))
out = []
for rep in json.loads(res)["BlastOutput2"]:
    s = rep["report"]["results"]["search"]
    asv = s["query_title"].split()[0]
    qlen = s["query_len"]
    hits = []
    for hit in s.get("hits", []):
        hsp = hit["hsps"][0]
        hits.append((100 * hsp["identity"] / hsp["align_len"], 100 * hsp["align_len"] / qlen,
                     hit["description"][0].get("sciname", "?")))
    if not hits:
        out.append([asv, reads[asv], tax[asv], "no hit", "", "", "", ""])
        continue
    top = max(h[0] for h in hits)
    near = sorted({h[2] for h in hits if h[0] >= top - 0.5})
    b = max(hits, key=lambda h: (h[0], h[1]))
    pema_genus = tax[asv].split("; ")[-1].split()[0]
    agree = "yes" if any(n.split()[0] == pema_genus for n in near) else "no"
    out.append([asv, reads[asv], tax[asv], b[2], f"{b[0]:.1f}", f"{b[1]:.0f}", "; ".join(near), agree])
with open("analysis/blast_check.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["ASV", "reads", "PEMA_taxonomy", "NCBI_best", "identity_pct", "coverage_pct", "NCBI_within_0.5pct",
                "genus_agrees"])
    w.writerows(out)
print("written analysis/blast_check.tsv")

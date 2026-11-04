"""Per-pond summary of the 12S eDNA results (29 ponds, 93 runs, PONDERFUL Türkiye) and a map.

Each ASV gets a label from PEMA's taxonomy, replaced by the NCBI BLAST check (analysis/blast_check.tsv) where that
check found >= 97 % identity over >= 95 % of the sequence (PEMA's 12S reference lacks several Anatolian amphibians).
Labels are grouped into taxa that 12S resolves reliably (genus level for water frogs, newts, toads). A group is
present in a pond when its replicate runs together hold >= 10 reads and >= 0.01 % of the pond's reads.
Status: only Pseudorasbora parva is marked non-native (FishBase: native to East Asia, introduced in Europe and Asia);
other fish are not given a status here.
Writes analysis/pond_table.tsv and figures/ponds_edna_map.png.
Usage: pixi run python scripts/pond_summary.py   (from ankara-ponds-edna/)
"""
import collections
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TAB = "results_all/rdp_assignment/tax_assigned_table.tsv"
os.makedirs("figures", exist_ok=True)

runs = {r["run_accession"]: r for r in csv.DictReader(open("runs_all.tsv"), delimiter="\t")
        if r["country"].startswith("Turkey")}
blast = {r["ASV"]: r for r in csv.DictReader(open("analysis/blast_check.tsv"), delimiter="\t")}

GROUPS = [  # (group, kind, keywords matched in the label)
    ("Water frogs (Pelophylax)", "amphibian", ["Pelophylax", "Ranidae"]),
    ("Tree frog (Hyla)", "amphibian", ["Hyla", "Hylidae"]),
    ("Toads (Bufotes / Bufonidae)", "amphibian", ["Bufotes", "Bufonidae"]),
    ("Spadefoot (Pelobates)", "amphibian", ["Pelobates"]),
    ("Crested newts (Triturus)", "amphibian", ["Triturus"]),
    ("Banded newt (Ommatotriton)", "amphibian", ["Ommatotriton"]),
    ("Other newts (Lissotriton, Caudata)", "amphibian", ["Lissotriton", "Caudata", "Salamandridae"]),
    ("Pond turtle (Emys orbicularis)", "reptile", ["Emys", "Testudines", "Geoemydidae"]),
    ("Topmouth gudgeon (P. parva, non-native)", "fish", ["Pseudorasbora"]),
    ("Goldfish / Prussian carp (Carassius)", "fish", ["Carassius"]),
    ("Common carp (Cyprinus carpio)", "fish", ["Cyprinus"]),
    ("Pike (Esox)", "fish", ["Esox"]),
    ("Tench (Tinca tinca)", "fish", ["Tinca"]),
    ("Sand smelt (Atherina boyeri)", "fish", ["Atherina"]),
    ("Other fish", "fish", ["Actinopteri", "Cypriniformes", "Cyprinidae", "Cobitis", "Rhodeus", "Silurus", "Ponticola",
                            "Nemacheilidae", "Perca", "Sander", "Leuciscidae", "Gobionidae", "Acheilognathidae"]),
    ("Livestock (cattle, sheep, goat, donkey, buffalo)", "livestock", ["Bos", "Ovis", "Capra", "Equus", "Bubalus",
                                                                       "Bovidae"]),
    ("Human", "human", ["Homo sapiens"]),
]


def group_of(label):
    for g, kind, keys in GROUPS:
        if any(k in label for k in keys):
            return g, kind
    return None, None


rows = list(csv.reader(open(TAB), delimiter="\t"))
header, rows = rows[0], rows[1:]
samples = header[1:-1]
pond_of = {s: runs[s.split("_")[-1]]["sample_alias"] for s in samples}
reads = collections.defaultdict(lambda: collections.Counter())
total = collections.Counter()
for r in rows:
    asv, label = r[0], r[-1]
    b = blast.get(asv)
    if b and b["identity_pct"] and float(b["identity_pct"]) >= 97 and float(b["coverage_pct"] or 0) >= 95:
        label = label + "; " + b["NCBI_within_0.5pct"]
    g, _ = group_of(label)
    for s, v in zip(samples, r[1:-1]):
        v = int(v)
        total[pond_of[s]] += v
        if g:
            reads[pond_of[s]][g] += v

ponds = sorted(total, key=lambda p: int(p[2:]))
info = {}
for acc, r in runs.items():
    p = r["sample_alias"]
    info.setdefault(p, {"site": r["country"].split(": ")[1], "lat": [], "lon": [], "runs": 0})
    info[p]["lat"].append(float(r["lat"]))
    info[p]["lon"].append(float(r["lon"]))
    info[p]["runs"] += 1

out = []
for p in ponds:
    present = {g for g, v in reads[p].items() if v >= 10 and v >= 1e-4 * total[p]}
    amph = sorted(g for g in present if dict((x[0], x[1]) for x in GROUPS)[g] == "amphibian")
    fish = sorted(g for g in present if dict((x[0], x[1]) for x in GROUPS)[g] == "fish")
    nonhuman = total[p] - reads[p]["Human"]
    live = reads[p]["Livestock (cattle, sheep, goat, donkey, buffalo)"] / nonhuman if nonhuman else 0
    i = info[p]
    out.append({"pond": p, "site": i["site"], "lat": round(sum(i["lat"]) / len(i["lat"]), 5),
                "lon": round(sum(i["lon"]) / len(i["lon"]), 5), "runs": i["runs"], "reads": total[p],
                "amphibian_groups": len(amph), "amphibians": "; ".join(amph),
                "pond_turtle": "yes" if "Pond turtle (Emys orbicularis)" in present else "",
                "fish_groups": len(fish), "fish": "; ".join(fish),
                "topmouth_gudgeon": "yes" if any("Topmouth" in f for f in fish) else "",
                "livestock_share_nonhuman_pct": round(100 * live, 1),
                "human_share_pct": round(100 * reads[p]["Human"] / total[p], 1)})
with open("analysis/pond_table.tsv", "w") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]), delimiter="\t")
    w.writeheader()
    w.writerows(out)

# summary printed for the report
nofish = [o for o in out if o["fish_groups"] == 0]
withfish = [o for o in out if o["fish_groups"] > 0]
mean = lambda xs: sum(xs) / len(xs) if xs else float("nan")
print(f"{len(out)} ponds; fish detected in {len(withfish)}, none in {len(nofish)}")
print(f"amphibian groups per pond: without fish {mean([o['amphibian_groups'] for o in nofish]):.1f}, "
      f"with fish {mean([o['amphibian_groups'] for o in withfish]):.1f}")
print(f"topmouth gudgeon in {sum(o['topmouth_gudgeon'] == 'yes' for o in out)} ponds; "
      f"pond turtle in {sum(o['pond_turtle'] == 'yes' for o in out)} ponds")
for g, kind, _ in GROUPS:
    if kind in ("amphibian", "reptile", "fish"):
        n = sum(1 for o in out if g in (o["amphibians"] + "; " + o["fish"]) or (kind == "reptile" and o["pond_turtle"]))
        print(f"  {g}: {n} ponds")

# figure: (a) map of ponds, colour = fish detected or not, size = amphibian groups; (b) amphibian groups vs fish
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.6, 1]})
for o in out:
    c = "#c0392b" if o["fish_groups"] else "#2471a3"
    ax[0].scatter(o["lon"], o["lat"], s=30 + 45 * o["amphibian_groups"], color=c, alpha=0.75, edgecolor="white")
for s in sorted({o["site"] for o in out}):
    xs = [o["lon"] for o in out if o["site"] == s]
    ys = [o["lat"] for o in out if o["site"] == s]
    ax[0].annotate(s.replace("Karacaoren", "Karacaören").replace("Akbas", "Akbaş").replace("Imrendi", "İmrendi")
                   .replace("Ayas Yolu", "Ayaş Yolu"), (sum(xs) / len(xs), max(ys) + 0.012), ha="center", fontsize=8)
ax[0].set_xlabel("Longitude (°E)")
ax[0].set_ylabel("Latitude (°N)")
ax[0].set_title("29 ponds west of Ankara (eDNA, 12S, 2022)", fontsize=10)
for n, lab, c in [(1, "1 amphibian group", "0.5"), (4, "4 groups", "0.5")]:
    ax[0].scatter([], [], s=30 + 45 * n, color=c, label=lab)
ax[0].scatter([], [], s=60, color="#c0392b", label="fish detected")
ax[0].scatter([], [], s=60, color="#2471a3", label="no fish detected")
ax[0].legend(fontsize=7, loc="lower left", frameon=False)
data = [[o["amphibian_groups"] for o in nofish], [o["amphibian_groups"] for o in withfish]]
for i, d in enumerate(data):
    ax[1].scatter([i + (j % 5 - 2) * 0.04 for j in range(len(d))], d, color=["#2471a3", "#c0392b"][i], alpha=0.7)
    ax[1].hlines(mean(d), i - 0.25, i + 0.25, color="k")
ax[1].set_xticks([0, 1], [f"no fish (n={len(data[0])})", f"fish (n={len(data[1])})"])
ax[1].set_ylabel("Amphibian groups detected per pond")
ax[1].set_title("Amphibians and fish", fontsize=10)
fig.text(0.01, 0.01, "Data: PONDERFUL eDNA reads, ENA PRJNA1495761 (METU, Cuenca-Cambronero et al. 2026); "
         "analysis: PEMA v3.0.0 + NCBI BLAST check. Prototype, open to correction.", fontsize=6.5, color="0.4")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("figures/ponds_edna_map.png", dpi=180)
print("written analysis/pond_table.tsv, figures/ponds_edna_map.png")

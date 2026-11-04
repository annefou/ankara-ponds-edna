# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 03 — BLAST check and per-pond results
#
# PEMA's 12S reference lacks several Anatolian amphibians. `scripts/blast_check.py` sent the main ASV of each taxon
# (plus the 10 most abundant unresolved ASVs) to NCBI BLAST (megablast, core_nt). In `scripts/pond_summary.py` a
# BLAST hit replaces PEMA's label at ≥ 97 % identity over ≥ 95 % of the sequence. A group is present in a pond when
# its replicate runs together hold ≥ 10 reads and ≥ 0.01 % of the pond's reads.

# %%
from pathlib import Path

import pandas as pd

A = Path("../analysis")
bl = pd.read_csv(A / "blast_check.tsv", sep="\t")
print(f"{len(bl)} ASVs checked; genus agrees with PEMA for {(bl.genus_agrees == 'yes').sum()}")
bl[bl.genus_agrees == "no"][["ASV", "reads", "PEMA_taxonomy", "NCBI_best", "identity_pct", "coverage_pct"]].head(25)

# %%
pt = pd.read_csv(A / "pond_table.tsv", sep="\t")
nofish, fish = pt[pt.fish_groups == 0], pt[pt.fish_groups > 0]
print(f"{len(pt)} ponds; fish detected in {len(fish)}, none in {len(nofish)}")
print(f"amphibian groups per pond: without fish {nofish.amphibian_groups.mean():.1f}, with fish {fish.amphibian_groups.mean():.1f}")
print(f"topmouth gudgeon (Pseudorasbora parva, non-native, FishBase) in {(pt.topmouth_gudgeon == 'yes').sum()} ponds; "
      f"European pond turtle in {(pt.pond_turtle == 'yes').sum()}")
print(f"livestock above 1 % of non-human reads in {(pt.livestock_share_nonhuman_pct > 1).sum()} ponds")
groups = pd.concat([pt.amphibians, pt.fish]).dropna().str.split("; ").explode()
groups[groups != ""].value_counts().rename("ponds")

# %%
pt.drop(columns=["lat", "lon"])

# %% [markdown]
# Caveats: read counts are not abundances; 12S cannot separate Anatolian water frogs or *Carassius* species; human
# DNA (20 % of reads) comes from handling; no field validation yet. Only *P. parva* is marked non-native.

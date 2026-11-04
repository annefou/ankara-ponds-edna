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
# # 02 — PEMA v3.0.0
#
# PEMA (LifeWatch ERIC's metabarcoding pipeline, [github.com/hariszaf/pema](https://github.com/hariszaf/pema), commit
# 9b9e649) run with Nextflow and rootless Podman (`pema_all.yaml`, `podman.config`): marker 12S, Swarm clustering,
# RDP classifier with the 12S_v200 reference (Zenodo record 23298141). Primers were left in the reads.

# %%
from pathlib import Path

import pandas as pd

R = Path("../results_all")
tab = pd.read_csv(R / "rdp_assignment/tax_assigned_table.tsv", sep="\t")
samples = tab.columns[1:-1]
tab["reads"] = tab[samples].sum(axis=1)
tab["depth"] = tab.iloc[:, -2].astype(str).str.count(";") + 1
print(f"{len(tab)} ASVs, {len(samples)} runs, {tab.reads.sum():,} reads")
level = {1: "domain", 2: "kingdom", 3: "phylum"}
tab["resolved"] = tab.depth.map(lambda d: level.get(d, "class or below"))
tab.groupby("resolved").reads.sum().div(tab.reads.sum()).mul(100).round(1).rename("% of reads")

# %%
tab.sort_values("reads", ascending=False)[[tab.columns[0], tab.columns[-4], "reads"]].head(15)

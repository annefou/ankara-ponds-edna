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
# # 01 — Data
#
# **Prototype, open to correction by the METU team.** Public eDNA reads sampled by METU (Beklioğlu, Avcı) for
# PONDERFUL: Cuenca-Cambronero et al. 2026, *Nature Ecology & Evolution*,
# [doi:10.1038/s41559-026-03197-w](https://doi.org/10.1038/s41559-026-03197-w); reads in ENA
# [PRJNA1495761](https://www.ebi.ac.uk/ena/browser/view/PRJNA1495761). The field observations of the same ponds are
# restricted until 15 January 2027 and are not used here.
#
# `run_pema_all.sh` downloads the Turkish runs from ENA (MD5-checked, retries when ENA throttles with HTTP 403). This
# book does **not** rerun it: the reads are not in git, and PEMA takes hours. These pages read the committed PEMA
# outputs (`results_all/`), the BLAST check and the per-pond table (`analysis/`) and the figure (`figures/`).

# %%
import pandas as pd

runs = pd.read_csv("../runs_all.tsv", sep="\t")
tr = runs[runs.country.str.startswith("Turkey")].copy()
tr["site"] = tr.country.str.split(": ").str[1]
print(f"ENA project: {len(runs)} runs in all countries; Türkiye: {len(tr)} runs, "
      f"{tr.sample_alias.nunique()} ponds, {tr.site.nunique()} sites")
print("library / layout / instrument:", *[", ".join(map(str, tr[c].unique())) for c in ["library_strategy", "library_layout", "instrument_model"]], sep=" | ")
print("collection dates:", tr.collection_date.min(), "to", tr.collection_date.max())
tr.groupby("site").agg(ponds=("sample_alias", "nunique"), runs=("run_accession", "count"),
                       reads=("read_count", "sum"))

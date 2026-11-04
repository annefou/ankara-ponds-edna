# 03 — FORRT Claim

**Form heading:** *"FORRT Claim — Declare an original claim according to FORRT, linking it to an AIDA sentence with a specific FORRT type."*

## Field-by-field draft

<!-- field: claim -->
### Short URI suffix as claim ID (text input, required)

```
ponderful-edna-amphibian-fish-detections-claim
```

<!-- field: label -->
### Label of the claim, to find it later (text input, required)

```
Amphibian species and fish presence in PONDERFUL ponds identified by eDNA metabarcoding (Cuenca-Cambronero et al. 2026)
```

<!-- field: aida -->
### Search for an AIDA sentence (search/select, required)

```
«URI of step 02 (AIDA), filled by the chain wizard»
```

<!-- field: forrtType -->
### Type of FORRT claim (dropdown, required)

From `vocabulary("claim_type")` (live, 2026-11-04): which taxa occur in which ponds, a distribution.

- [ ] computational performance (Computational & Performance)
- [ ] data governance (access control, licensing, FAIR compliance)
- [ ] data quality (preprocessing, validation, normalization)
- [x] descriptive pattern (distribution, trend, proportion)
- [ ] model performance (accuracy, F1 score, evaluation metrics)
- [ ] scalability (Computational & Performance)
- [ ] statistical significance (significant difference, relationship, or effect)

<!-- field: source -->
### Source URI (text input, optional)

```
https://doi.org/10.1038/s41559-026-03197-w
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 03.

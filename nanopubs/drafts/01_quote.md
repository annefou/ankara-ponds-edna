# 01 — Quote-with-comment (paper-rooted chains)

**Form heading:** *"Annotate a paper quotation — Annotating a paper quotation with personal interpretation"*

## Field-by-field draft

<!-- field: paper -->
### Cited DOI (text input, required)

Resolved with `resolve_doi` (2026-11-04): Cuenca-Cambronero et al. 2026, *Nature Ecology & Evolution*.

```
10.1038/s41559-026-03197-w
```

### Quote mode (radio button)

The preprint's line numbers sit inside the sentence, so the passage is quoted by its start and end (each verified on
its own).

- [ ] **Quote whole text (less than 500 characters)**
- [x] Quote start/end *(use this if the quote exceeds 500 chars)*

<!-- field: quotation -->
### The exact quotation from the paper (max. 500 characters) (textarea, required)

Verified with `verify_quote` on `paper/cuenca-cambronero-2026-preprint.pdf`: page 10, characters 1813–1866, match
"exact". **Recheck against the published version.**

```
For amphibian taxonomy, species were identified using
```

<!-- field: quotation-end -->
### End of quotation (optional - use when quoting beginning and end of a longer passage, max. 500 characters) (textarea, optional)

Verified with `verify_quote`: page 10, characters 2213–2288, match "exact".

```
zooplankton, 148 genera of macroinvertebrates and 39 species of amphibians.
```

<!-- field: comment -->
### Our interpretation and explanation of why this quotation is relevant (max. 800 characters) (textarea, required)

```
The amphibian richness that enters the paper's biodiversity index, and the fish presence used as a model factor (Methods: "fish presence was determined using eDNA metabarcoding"), come from eDNA metabarcoding of pond water. The reads are public (ENA PRJNA1495761), so the detections can be re-derived independently. This chain re-derives them for the 29 ponds in Türkiye with LifeWatch ERIC's PEMA pipeline and an NCBI BLAST check, as a test of how far the species list depends on the bioinformatic pipeline and its reference database.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 01.

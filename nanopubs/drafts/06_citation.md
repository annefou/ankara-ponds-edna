# 06 — CiTO Citation

> **PENDING with step 05.** The citation type follows the Outcome's validation status, which waits for the
> release of the paper's per-pond detections (15 January 2027).

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Description:** *"Declare citations between papers or other works, using Citation Typing Ontology"*

## Field-by-field draft

<!-- field: work -->
### Identifier for the citing creative work (text input, required)

URI of the Outcome published in step 05. Pull from `nanopubs/PUBLISHED.md`.

```

```

### List citations (repeatable group, required ≥1)

#### Citation 1 — back to the original paper

##### Citation Type (dropdown)

Choose based on the Outcome's validation status:

- Validated → `confirms`
- PartiallySupported → `qualifies`
- Contradicted → `disputes`

For question-rooted chains where there is no original paper to confirm/dispute, use `usesMethodIn` or `citesAsAuthority` for the methodology paper(s).

Write the chosen type in the block below (a vocabulary label such as `cites as authority`, or `citesAsAuthority`). `build-chain-draft` uses it as written; leave the block empty to have the type derived from the Outcome's validation status, which is right for paper-rooted chains only.

> **Note:** `replicates` is NOT in the Science Live dropdown (despite existing in upstream CiTO). When citing a notebook/tutorial that was directly reused, use **`credits`** instead.

```

```

##### DOI or other URL of the cited work (text input)

Must be a DOI (`https://doi.org/...`): the first citation is the work the chain is about. Leave the placeholder to use the paper in `CITATION.cff`. Links to other works, such as another chain's nanopublication, go under *Additional citations* below.

```
https://doi.org/10.1038/s41559-026-03197-w
```

#### Additional citations (optional)

If the Outcome cites methods papers, related replications, or upstream tools, add them here.

One line per further citation, in this exact form (each becomes a pre-filled row):

Checked with `vocabulary("cito_relation")` and `resolve_doi` (2026-11-04).

- _Type: uses data from → URL: https://www.ebi.ac.uk/ena/browser/view/PRJNA1495761
- _Type: uses method in → URL: https://doi.org/10.1093/gigascience/giaa022

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 06.

This completes the six-step FORRT chain. Optional next layers:

- **Research Software** (`drafts/07_research_software.md`) — if the repo *produces* a reusable software artefact.
- **Research Synthesis** (`drafts/08_synthesis.md`) — if this chain is one of several testing facets of a shared property.

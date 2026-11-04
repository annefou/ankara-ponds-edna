# 05 — FORRT Replication Outcome

> **PENDING — do not publish before the comparison.** The paper's per-pond eDNA detections are in the PONDERFUL
> database, restricted until 15 January 2027. Our side of the comparison is done (below, from
> `analysis/pond_table.tsv` and `analysis/blast_check.tsv`, 2026-11-04); the validation status, confidence level and
> conclusion are left empty on purpose until the two can be compared pond by pond.

## Our detections, for the comparison

- 29 ponds, 93 runs, 3,851 ASVs, 70.3 million reads (PEMA v3.0.0).
- Fish in 23 of 29 ponds; topmouth gudgeon (*Pseudorasbora parva*, non-native, FishBase) in 19.
- Amphibians (ponds with the group): water frogs (*Pelophylax*) 26, crested newts (*Triturus*) 15, banded newt
  (*Ommatotriton*) 13, other newts (*Lissotriton*, Caudata) 9, toads (*Bufotes*/Bufonidae) 7, tree frog (*Hyla*) 7,
  spadefoot (*Pelobates*) 6. European pond turtle (*Emys orbicularis*) in 4.
- PEMA's 12S_v200 reference has no *Triturus*, *Ommatotriton*, *Pelobates*, *Bufotes*, *Lissotriton* or *Emys*
  (none in its taxonomy tree, `rdp_databases/12S_v200/bergeyTrainingTree.xml`); these are found only through the
  BLAST check (98.4-100 % identity for the main ASVs).
- Of the 101 ASVs checked with BLAST, 46 agree with PEMA at genus level, 53 do not and 2 have no hit. Of the 53, PEMA
  stopped above genus for 50 (BLAST then names the genus); 3 are bird species where NCBI's best hit at 100 % is
  another species (*Anas crecca* → *Histrionicus histrionicus*, *Cygnus atratus* → *Anser anser*, *Alectoris rufa* →
  *Chrysococcyx minutillus*), so bird labels are not used.
- Amphibian groups per pond: 3.7 without fish (6 ponds), 2.7 with fish (23 ponds).

To compare when the data are released: fish presence per pond (paper's model factor), amphibian species per pond, and
the paper's total of 39 amphibian species (all seven countries; the Turkish subset is not given in the text).

## Field-by-field draft

<!-- field: outcome -->
### Short URI suffix for outcome ID (text input, required)

Slug. Use kebab-case.

```

```

<!-- field: label -->
### Plain-text label for the outcome (text input, required)

Descriptive title.

```

```

<!-- field: study -->
### Choose study (search/select, required)

URI of the Replication Study published in step 04. Pull from `nanopubs/PUBLISHED.md`.

```

```

<!-- field: repo -->
### Repository URL (text input, required)

Use the Zenodo **version DOI** URL for the release the results came from — not a
bare branch URL, and not the concept DOI.

> **Why not the bare repo URL.** `https://github.com/ORG/REPO` names a *moving
> branch*. This Outcome asserts "this code produced this number", in a signed,
> immutable record. A branch URL means that assertion points at whatever `main`
> happens to be years from now — code that may never have produced the number
> above. A concept DOI has the same flaw: it resolves to the latest version.
> The version DOI pins the exact release. `docs/chain-decision-tree.md` § Anchor
> ranks the options: SWHID > Zenodo DOI > repo URL > Wayback.
>
> Both DOIs and the SWHID are in `CITATION.cff` under `identifiers:`, recorded
> automatically at release by `.github/workflows/release-identifiers.yml`. Take
> the one described as *"Version DOI"*.

```
https://doi.org/{{ZENODO_VERSION_DOI}}
```

<!-- field: date -->
### Choose completion date (text input, required)

```
{{RELEASE_DATE}}
```

<!-- field: validationStatus -->
### Choose validation status (dropdown, required)


This dropdown maps to the CiTO intention in step 06: Validated → `confirms`, PartiallySupported → `qualifies`, Contradicted → `disputes`.

- [ ] contradicted
- [ ] inconclusive
- [ ] not tested
- [ ] partially supported
- [ ] validated

<!-- field: confidenceLevel -->
### Choose confidence level (dropdown, required)

_Vocabulary not yet captured._

```

```

- [ ] high - Strong evidence, mostly agrees with original
- [ ] low - Limited evidence, significant disagreement
- [ ] moderate - Adequate evidence, partial agreement
- [ ] very high - Extensive evidence, high agreement with original
- [ ] very low - Minimal evidence, major disagreement

<!-- field: conclusion -->
### Describe the overall conclusion about the original claim (textarea, required)

Substantive interpretation. Headline comparison: replication's number vs the paper's number, sign + significance.

```

```

<!-- field: evidence -->
### Describe the evidence that supports your conclusion (textarea, required)

Numerical results, test statistics, model coefficients. Read directly from `results/`.

```

```

<!-- field: limitations -->
### Describe what limits the conclusions of the study (textarea, optional)

Honest caveats. If the result is partial or contradicted, say so plainly. Don't overclaim.

```

```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.

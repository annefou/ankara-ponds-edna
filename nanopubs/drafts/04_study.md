# 04 — FORRT Replication Study

Method read from `Snakefile`, `run_pema_all.sh`, `pema_all.yaml`, `scripts/blast_check.py` and
`scripts/pond_summary.py` (2026-11-04).

## Field-by-field draft

<!-- field: study -->
### Short URI suffix for study ID (text input, required)

```
ponderful-turkiye-edna-pema-replication-study
```

<!-- field: label -->
### Label/name of replication study (text input, required)

```
Independent re-analysis of the PONDERFUL eDNA reads of 29 ponds in Türkiye with PEMA and an NCBI BLAST check
```

<!-- field: type -->
### Choose the study type (dropdown, required)

Same reads, different bioinformatic pipeline and reference database (`vocabulary("study_type")`, live, 2026-11-04).

- [x] Replication Study - replication with different methodology or conditions
- [ ] Reproduction/Replication Study - study that is both, reproduction and replication
- [ ] Reproduction Study - direct reproduction: same methodology, same tools

<!-- field: claim -->
### Choose FORRT claim (search/select, required)

```
«URI of step 03 (FORRT Claim), filled by the chain wizard»
```

<!-- field: scope -->
### Describe what part of the claim is reproduced/replicated. (textarea, required)

```
The eDNA detections of amphibians and fish in the 29 ponds sampled in Türkiye (six sites west of Ankara, May-June 2022): which amphibian taxa are found in each pond and whether fish are present. In scope: the list of taxa per pond, the number of ponds with fish, and the taxa the reference database misses. Out of scope: the other five countries, macrophytes, zooplankton and macroinvertebrates, the ecosystem functions and the biodiversity-multifunctionality models.
```

<!-- field: methodology -->
### Describe how the claim is reproduced/replicated. (textarea, required)

```
The 93 public runs of the 29 Turkish ponds (ENA PRJNA1495761, 12S vertebrate marker, paired-end Illumina, three runs per pond, six for two ponds) are downloaded with MD5 checks and processed with LifeWatch ERIC's PEMA v3.0.0 (Nextflow, rootless Podman): quality trimming, Swarm clustering into ASVs and taxonomy with the RDP classifier on PEMA's 12S_v200 reference (3,851 ASVs, 70.3 million reads). The most abundant ASV of each assigned taxon and the 10 most abundant unresolved ASVs (101 in all) are checked against NCBI core_nt with megablast; a BLAST hit replaces PEMA's label at 97% identity or more over 95% of the sequence. A taxon is present in a pond when its replicate runs together hold at least 10 reads and 0.01% of the pond's reads. Amphibians are grouped at the genus level that 12S resolves.
```

<!-- field: deviation -->
### Describe any deviations from original methodology. (textarea, optional)

```
A different bioinformatic pipeline and reference database from the paper's (INBO eDNA laboratories; details in the paper's supplementary methods, not read); primers left in the reads; a fixed read threshold for presence; amphibians resolved to genus where 12S cannot separate species (Anatolian water frogs); only the Turkish ponds.
```

<!-- field: keyword -->
### Search keywords (Wikidata) (search/select, optional)

Checked with `wikidata_lookup` (2026-11-04).

- environmental DNA (Q25098939)
- metabarcoding (Q51237016)
- Amphibia (Q10908)

<!-- field: discipline -->
### Search discipline (Wikidata) (search/select, optional)

Checked with `wikidata_lookup` (expected type academic discipline, 2026-11-04).

- ecology (Q7150)

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.

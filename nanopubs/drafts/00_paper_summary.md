# Paper summary

> Working scratchpad for the paper-analysis phase; not a nanopub.

**Reference paper:** Biodiversity enhances pond ecosystem multifunctionality across Europe

**DOI:** 10.1038/s41559-026-03197-w (resolved with `resolve_doi`, 2026-11-04)

**Authors:** Cuenca-Cambronero, Delgado-Baquerizo, Anton-Pardo, Avci, Bartrons, Beklioglu, Biggs, Boix, Bucak,
Davidson, De Meester, Fahy, Greaves, Lemmens, Levi, Martin, Mehner, Oertli, Patmore, Sayer, Trochine, von Plüskow,
Wijns, Williams, Brucet

**Year:** 2026 (*Nature Ecology & Evolution*)

**Text used:** the open submitted preprint (RIUVic, hdl:10854/181494), `paper/cuenca-cambronero-2026-preprint.pdf`
(not in git), SHA-256 d3a7de2a…f584aee. The published version is paywalled. **Every quotation below must be
rechecked against the published article before publishing.**

## Headline claim of the paper

Pond biodiversity (macrophytes, zooplankton, macroinvertebrates, amphibians) is positively associated with ecosystem
multifunctionality across 206 ponds in six European countries and Türkiye; fish presence is negatively correlated
with multifunctionality. We cannot test this: the function measurements and the per-pond richness are in the PONDERFUL
database, restricted until 15 January 2027.

## The part of the paper this chain tests

The biodiversity input that comes from eDNA: amphibian species and fish presence in each pond were identified by eDNA
metabarcoding (INBO eDNA laboratories, Geraardsbergen), 39 amphibian species in total. The raw reads are public
(ENA PRJNA1495761), so the Turkish detections can be re-derived with an independent pipeline (LifeWatch ERIC's
PEMA) and compared with the paper's per-pond detections once these are released.

## Methodology summary (paper)

- 206 ponds: Belgium, Denmark, Germany, Spain, Switzerland, the UK, and 29 ponds in Türkiye (METU; fieldwork
  coordinated by Beklioğlu and Avcı). One visit per pond.
- eDNA: DNA extracted with Qiagen DNeasy Blood and Tissue, purified with the Qiagen DNAeasy Power Cleanup Kit (paper's wording); vertebrate metabarcoding
  at INBO; details in the supplementary methods (not in the preprint).
- Fish richness excluded from the diversity index; fish presence/absence used as a model factor.

## Replication design choice

Same data (the public reads of the 29 Turkish ponds), different methodology (PEMA v3.0.0 with Swarm and the RDP
classifier on the 12S_v200 reference, plus an NCBI BLAST check): **Replication Study** in the FORRT vocabulary.
Outcome pending the release of the paper's per-pond detections.

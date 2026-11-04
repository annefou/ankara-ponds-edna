# ankara-ponds-edna (prototype)

Test of LifeWatch ERIC's metabarcoding pipeline PEMA on public eDNA data from Türkiye: 93 runs (29 ponds, 6 sites west of
Ankara, May–June 2022, 12S-V5 vertebrate marker) sampled by METU (Beklioğlu, Avcı) for PONDERFUL
(Cuenca-Cambronero et al. 2026, *Nature Ecology & Evolution*, doi:10.1038/s41559-026-03197-w; reads ENA PRJNA1495761).
Our analysis of public data, open to correction by the METU team. The field observations of the same ponds are restricted until
15 January 2027.

Site: <https://annefou.github.io/ankara-ponds-edna/> (pages read the committed tables; nothing is rerun).
Container: `docker run --rm ghcr.io/annefou/ankara-ponds-edna:latest` rebuilds the pond table and map from the
committed PEMA and BLAST tables (PEMA itself needs Nextflow and Podman on the host).

## Steps

1. `run_pema_all.sh` (started with `start_full_run.sh`): downloads the 93 runs from ENA (MD5-checked, retries on 403)
   and runs PEMA v3.0.0 (Swarm, RDP classifier with the 12S_v200 database, rootless Podman, `podman.config`).
   Output: `results_all/rdp_assignment/tax_assigned_table.tsv`.
2. `scripts/blast_check.py`: the main ASV of each taxon (101 ASVs) BLAST-searched against NCBI core_nt;
   `analysis/blast_check.tsv`. PEMA's 12S reference lacks several Anatolian amphibians (Triturus, Ommatotriton,
   Pelobates, Bufotes, Emys), which BLAST resolves at 98–100 % identity.
3. `pixi run python scripts/pond_summary.py`: per-pond groups (`analysis/pond_table.tsv`) and
   `figures/ponds_edna_map.png`.

## Main results (30 October 2026)

- Water frogs (Pelophylax, genus level) in 26 ponds; crested newts (Triturus) 15; banded newt (Ommatotriton) 13;
  toads 7; tree frog 7; spadefoot (Pelobates) 6; European pond turtle (Emys orbicularis) 4.
- Fish in 23 of 29 ponds; topmouth gudgeon (Pseudorasbora parva, non-native, FishBase) in 19; Carassius 16; carp 11.
- Ponds without fish: 3.7 amphibian groups on average; with fish: 2.7.
- Human DNA 20 % of reads (handling); livestock above 1 % of non-human reads in 8 ponds.

## Reproduce

Not in git (see `.gitignore`): the reads (downloaded by `run_pema_all.sh` from ENA), PEMA (`git clone
https://github.com/hariszaf/pema.git pema`, commit 9b9e649, v3.0.0), the 12S_v200 RDP database (Zenodo record
23298141, unpacked in `rdp_databases/`), the pixi environment (`pixi install`) and PEMA's intermediate files.
Requirements: pixi, rootless Podman (`sudo apt install podman` on Ubuntu). Then `bash start_full_run.sh`,
`python3 scripts/blast_check.py`, `pixi run python scripts/pond_summary.py`.

Caveats: read counts are not abundances; primers left in the reads; 12S cannot separate Anatolian water frogs or
Carassius species; no field validation yet.

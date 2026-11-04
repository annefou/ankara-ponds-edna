# ankara-ponds-edna: PEMA v3.0.0 (12S) on the PONDERFUL eDNA reads of 29 ponds west of Ankara, then an NCBI BLAST
# check and the per-pond summary. No account is needed for any step.
#
#   pixi run snakemake --cores 1                 everything: ENA download (4.4 GB), PEMA (hours), BLAST, pond table
#   pixi run snakemake --cores 1 summary         only BLAST check + pond table and map, from the committed PEMA tables
#   pixi run land-cover                          land cover around each pond (ESA WorldCover 2021), no account
#
# PEMA runs its own containers through Nextflow and rootless Podman (podman.config); needs pema/ (v3.0.0) and the
# 12S_v200 reference in rdp_databases/ (README, "Install").

PEMA_TABLE = "results_all/rdp_assignment/tax_assigned_table.tsv"
PEMA_OUT = [PEMA_TABLE, "results_all/asvs_representatives.fa", "results_all/asvs_contingency_hash.tsv"]


rule all:
    input: "analysis/pond_table.tsv", "figures/ponds_edna_map.png", "analysis/landcover_vs_edna.json",
           "analysis/osm_vs_edna.json", "analysis/s2_visibility.tsv"


rule summary:                    # from the committed PEMA tables: no download, no PEMA
    input: "analysis/pond_table.tsv", "figures/ponds_edna_map.png"


rule reads:                      # the 93 Turkish runs of ENA PRJNA1495761, MD5-checked, retried on HTTP 403
    output: "reads_all/runs_turkey.tsv"
    shell: "bash run_pema_all.sh download"


rule pema:                       # Swarm clustering, RDP classifier with 12S_v200; Nextflow resumes finished steps
    input: ancient("reads_all/runs_turkey.tsv"), "pema/pema.nf", "rdp_databases/12S_v200", "pema_all.yaml"
    output: PEMA_OUT
    shell: "bash run_pema_all.sh pema"


rule blast:                      # NCBI BLAST (megablast, core_nt), anonymous; a few minutes in NCBI's queue
    input: PEMA_OUT
    output: "analysis/blast_check.tsv", "analysis/blast_raw.json"
    shell: "python scripts/blast_check.py"


rule pond_summary:
    input: PEMA_TABLE, "analysis/blast_check.tsv", "runs_all.tsv"
    output: "analysis/pond_table.tsv", "figures/ponds_edna_map.png"
    shell: "python scripts/pond_summary.py"


rule land_cover:                 # ESA WorldCover 2021 (10 m, anonymous, Planetary Computer) on HEALPix depth 18 cells
    input: "analysis/pond_table.tsv"
    output: "analysis/pond_landcover.tsv", "analysis/landcover_vs_edna.json"
    shell: "python scripts/land_cover.py"


rule osm_context:                # distances to streams, water, roads, villages (OpenStreetMap, Overpass API, no account)
    input: "analysis/pond_table.tsv"
    output: "analysis/pond_osm.tsv", "analysis/osm_vs_edna.json"
    shell: "python scripts/osm_context.py"


rule s2_visibility:              # can Sentinel-2 see the ponds at their public coordinates? (no account)
    input: "analysis/pond_table.tsv"
    output: "analysis/s2_visibility.tsv"
    shell: "python scripts/sentinel2_visibility.py"

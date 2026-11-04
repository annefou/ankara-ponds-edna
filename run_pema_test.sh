#!/usr/bin/env bash
# Test run of PEMA v3.0.0 (https://github.com/hariszaf/pema, commit 9b9e649) on 3 Turkish pond eDNA runs
# (12S-V5 vertebrate marker, ENA project PRJNA1495761; samples TR12 Akbas, TR24 and TR26 Karacaoren).
# Clustering: Swarm; taxonomy: RDP classifier with the PEMA 12S_v200 database (from Zenodo record 23298141,
# unpacked in rdp_databases/). Containers are pulled by Nextflow with rootless Podman.
# Output: results_test/ (main table: rdp_assignment/tax_assigned_table.tsv); log: test_run.log.
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # this repository
mkdir -p "$D/work_test" && sed "s|__REPO__|$D|g" "$D/pema_test.yaml" > "$D/work_test/params.yaml"
cd "$D/pema"
pixi run --manifest-path ../pixi.toml nextflow run pema.nf \
  --params-file ../work_test/params.yaml \
  -profile podman,reports \
  -c ../podman.config \
  -work-dir ../work_test \
  -resume 2>&1 | tee ../test_run.log
df -h "$D" | tail -1

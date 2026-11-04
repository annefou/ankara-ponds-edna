FROM ghcr.io/prefix-dev/pixi:0.68.1

LABEL org.opencontainers.image.source="https://github.com/annefou/ankara-ponds-edna"
LABEL org.opencontainers.image.description="ankara-ponds-edna: per-pond summary of PEMA 12S results (PONDERFUL, Türkiye)"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pixi.toml pixi.lock /app/
RUN pixi install --locked
COPY . /app

# `pixi run summary` (Snakemake target `summary`) rebuilds analysis/pond_table.tsv and figures/ponds_edna_map.png from the committed PEMA and BLAST tables.
# PEMA itself runs in its own container (hariszaf/pema v3.0.0) through Nextflow and rootless Podman on the
# host: see run_pema_all.sh and the README.
CMD ["pixi", "run", "summary"]

"""Land cover around each of the 29 ponds (ESA WorldCover 2021, 10 m) on HEALPix cells, against the eDNA results.

Source: ESA WorldCover 10 m 2021 v200 (Zanaga et al. 2022, doi:10.5281/zenodo.7254221, CC BY 4.0), tile N39E030,
read anonymously from Microsoft Planetary Computer (collection esa-worldcover).
Grid: HEALPix depth 18 (~25 m cells), healpix-geo WGS84 ellipsoid, NESTED. The 10 m pixels (EPSG:4326, so already
geodetic WGS84 lon/lat) are binned into the cells with healpix-resample's ConservativeResampler, each class carried
as pixel area (m2, from the pixel's latitude), so class areas add up exactly; a cell's class shares are its class
areas over its total. Area around a pond: the cells whose centre lies within 100 m of the pond coordinates (the
PONDERFUL paper's radius), and 250 m as a sensitivity check. Equal-area cells: shares are plain means over cells.
Pond coordinates: mean of the ENA sample coordinates of its runs (analysis/pond_table.tsv).

The paper's land-use variable is improved grassland plus arable land within 100 m, from field estimates and Google
Earth. WorldCover's cropland class is arable land; its grassland class cannot separate improved from natural
grassland, so both are reported separately and neither is the paper's variable.
With 29 ponds at six sites the comparison with fish and amphibians is descriptive (rank correlation, rank-sum test),
not a causal test.

Usage: pixi run land-cover   (from ankara-ponds-edna/). Writes analysis/pond_landcover.tsv and
analysis/landcover_vs_edna.json.
"""
import json

import numpy as np
import pandas as pd
import planetary_computer
import pystac_client
import rasterio
from rasterio.windows import from_bounds
import healpix_geo.nested as hn
from healpix_resample import ConservativeResampler
from pyproj import Geod
from scipy import stats

DEPTH = 18
ELLIPSOID = "WGS84"
RADII = (100, 250)
CLASSES = {10: "tree", 20: "shrubland", 30: "grassland", 40: "cropland", 50: "built_up", 60: "bare",
           80: "water", 90: "herbaceous_wetland"}
GEOD = Geod(ellps="WGS84")
R_EARTH = 6371008.8


def worldcover_href():
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                                    modifier=planetary_computer.sign_inplace)
    it = cat.get_collection("esa-worldcover").get_item("ESA_WorldCover_10m_2021_v200_N39E030")
    return it.assets["map"].href


def disc_cells(lon, lat, radius):
    """Depth-18 cells whose centre lies within `radius` m (geodesic) of the pond."""
    d = radius + 60
    lons, lats, _ = GEOD.fwd([lon] * 4, [lat] * 4, [0, 90, 180, 270], [d] * 4)
    ring = np.array([[min(lons), min(lats)], [max(lons), min(lats)], [max(lons), max(lats)], [min(lons), max(lats)]])
    ids, _, _ = hn.polygon_coverage(ring, DEPTH, ellipsoid=ELLIPSOID, flat=True)
    ids = np.unique(np.asarray(ids, np.uint64))
    clon, clat = hn.healpix_to_lonlat(ids, DEPTH, ellipsoid=ELLIPSOID)
    _, _, dist = GEOD.inv(np.full(ids.size, lon), np.full(ids.size, lat), np.asarray(clon), np.asarray(clat))
    return ids[dist <= radius]


def pond_shares(src, lon, lat):
    d = max(RADII) + 150
    lons, lats, _ = GEOD.fwd([lon] * 4, [lat] * 4, [0, 90, 180, 270], [d] * 4)
    w = from_bounds(min(lons), min(lats), max(lons), max(lats), src.transform).round_offsets().round_lengths()
    a = src.read(1, window=w)
    tr = src.window_transform(w)
    rows, cols = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    plon, plat = rasterio.transform.xy(tr, rows.ravel(), cols.ravel())
    plon, plat = np.asarray(plon), np.asarray(plat)
    res = abs(tr.a)
    px_m2 = (np.radians(res) * R_EARTH) ** 2 * np.cos(np.radians(plat))
    cls = a.ravel()
    op = ConservativeResampler(lon_deg=plon, lat_deg=plat, level=DEPTH, nest=True, ellipsoid=ELLIPSOID, verbose=False)
    tot = op.resample(px_m2)
    cid = np.asarray(tot.cell_ids, np.uint64)
    area = {"total": np.asarray(tot.cell_data, float)}
    for c, name in CLASSES.items():
        area[name] = np.asarray(op.resample(np.where(cls == c, px_m2, 0.0)).cell_data, float)
    cells = pd.DataFrame(area, index=cid)
    out = {}
    for r in RADII:
        ids = disc_cells(lon, lat, r)
        sub = cells.reindex(ids)
        if sub.total.isna().any():
            raise RuntimeError(f"{sub.total.isna().sum()} cells of the {r} m disc have no WorldCover pixel")
        share = sub[list(CLASSES.values())].div(sub.total, axis=0).mean()      # equal-area cells: plain mean
        out[r] = {"cells": int(len(ids)), **{k: round(100 * float(v), 1) for k, v in share.items()}}
        land = 100 - out[r]["water"] - out[r]["herbaceous_wetland"]
        out[r]["cropland_of_land"] = round(100 * out[r]["cropland"] / land, 1) if land > 0 else None
    return out


def main():
    ponds = pd.read_csv("analysis/pond_table.tsv", sep="\t")
    rows = []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"), rasterio.open(worldcover_href()) as src:
        for p in ponds.itertuples():
            sh = pond_shares(src, p.lon, p.lat)
            row = {"pond": p.pond, "site": p.site}
            for r, v in sh.items():
                row.update({f"{k}_{r}m": x for k, x in v.items()})
            rows.append(row)
            print(p.pond, p.site, "cropland 100 m:", sh[100]["cropland"], "% | grassland:", sh[100]["grassland"], "%", flush=True)
    lc = pd.DataFrame(rows)
    lc.to_csv("analysis/pond_landcover.tsv", sep="\t", index=False)
    m = ponds.merge(lc, on=["pond", "site"])
    m["fish"] = m.fish_groups > 0
    res = {"source": "ESA WorldCover 10 m 2021 v200, tile N39E030 (CC BY 4.0), Planetary Computer",
           "grid": f"HEALPix depth {DEPTH} (~25 m), healpix-geo WGS84 NESTED, healpix-resample ConservativeResampler",
           "ponds": int(len(m)), "by_radius": {}}
    for r in RADII:
        crop, grass = m[f"cropland_{r}m"], m[f"grassland_{r}m"]
        rho_c = stats.spearmanr(crop, m.amphibian_groups)
        rho_g = stats.spearmanr(grass, m.amphibian_groups)
        mw = stats.mannwhitneyu(crop[m.fish], crop[~m.fish], alternative="two-sided")
        res["by_radius"][f"{r} m"] = {
            "cells_per_pond_median": int(m[f"cells_{r}m"].median()),
            "cropland_pct": {"median": float(crop.median()), "min": float(crop.min()), "max": float(crop.max())},
            "grassland_pct": {"median": float(grass.median()), "min": float(grass.min()), "max": float(grass.max())},
            "ponds_with_cropland_over_25pct": int((crop > 25).sum()),
            "spearman_cropland_vs_amphibian_groups": {"rho": round(float(rho_c.statistic), 2), "p": round(float(rho_c.pvalue), 3)},
            "spearman_grassland_vs_amphibian_groups": {"rho": round(float(rho_g.statistic), 2), "p": round(float(rho_g.pvalue), 3)},
            "cropland_median_fish_vs_no_fish": [float(crop[m.fish].median()), float(crop[~m.fish].median())],
            "mannwhitney_cropland_fish_vs_no_fish_p": round(float(mw.pvalue), 3)}
    res["cropland_100m_by_site_median"] = {k: float(v) for k, v in m.groupby("site")["cropland_100m"].median().items()}
    json.dump(res, open("analysis/landcover_vs_edna.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

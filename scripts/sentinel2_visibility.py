"""Can Sentinel-2 see the 29 ponds at their public coordinates? A check before any permanence analysis.

Every pond held water when METU sampled it (10 May - 10 June 2022, ENA collection dates). Two clear Sentinel-2 L2A
scenes of that period (tile 36TVK, 26 and 31 May 2022, processing baseline 05.10, read anonymously from Microsoft
Planetary Computer) are read around each pond's coordinates (mean of its ENA sample coordinates); the offset of
baseline >= 04.00 is removed (reflectance = (DN - 1000) / 10000). Counted: 10 m pixels within 30 m of the point
with NDWI = (B03 - B08) / (B03 + B08) > 0, and with MNDWI = (B03 - B11) / (B03 + B11) > 0 (B11 at 20 m, nearest
neighbour onto the 10 m pixels). A pond is visible on a date when at least 3 such pixels lie within 30 m.
Native pixels on purpose: the question is whether the open water is there at all, before any grid.

Result (4 November 2026): 6 ponds (31 May) and 7 (26 May) are visible with NDWI, 2-4 with MNDWI, and none of the 6
ponds without fish. The ponds are small, partly under vegetation, or the coordinates miss the open water (TR2 and
TR5: nearest open water 150-180 m away, possibly another pond), so no permanence value is derived; it needs the
pond outlines or exact coordinates (PONDERFUL database, 15 January 2027).

Usage: pixi run s2-visibility   (from ankara-ponds-edna/). Writes analysis/s2_visibility.tsv.
"""
import numpy as np
import pandas as pd
import planetary_computer
import pystac_client
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
from pyproj import Geod, Transformer

SCENES = ["S2B_MSIL2A_20220526T083559_R064_T36TVK_20240614T013102",
          "S2A_MSIL2A_20220531T083611_R064_T36TVK_20240615T123859"]
RADIUS, MIN_PX = 30, 3
GEOD = Geod(ellps="WGS84")


def main():
    pt = pd.read_csv("analysis/pond_table.tsv", sep="\t")
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    items = sorted(cat.search(collections=["sentinel-2-l2a"], ids=SCENES).items(), key=lambda i: i.datetime)
    rows = []
    for r in pt.itertuples():
        rec = {"pond": r.pond, "site": r.site, "fish": bool(r.fish_groups > 0)}
        for it in items:
            off = 1000 if float(it.properties["s2:processing_baseline"]) >= 4 else 0
            h = {k: planetary_computer.sign(it.assets[k].href) for k in ("B03", "B08", "B11")}
            with rasterio.open(h["B03"]) as s:
                tr4326 = Transformer.from_crs(4326, s.crs, always_xy=True)
                lons, lats, _ = GEOD.fwd([r.lon] * 4, [r.lat] * 4, [0, 90, 180, 270], [RADIUS + 30] * 4)
                xs, ys = tr4326.transform(lons, lats)
                w = from_bounds(min(xs), min(ys), max(xs), max(ys), s.transform).round_offsets().round_lengths()
                g = s.read(1, window=w).astype(float) - off
                tr, bounds = s.window_transform(w), rasterio.windows.bounds(w, s.transform)
            with rasterio.open(h["B08"]) as s:
                n = s.read(1, window=w).astype(float) - off
            with rasterio.open(h["B11"]) as s:
                sw = s.read(1, window=from_bounds(*bounds, s.transform), out_shape=g.shape,
                            resampling=Resampling.nearest).astype(float) - off
            rr, cc = np.mgrid[0:g.shape[0], 0:g.shape[1]]
            x, y = rasterio.transform.xy(tr, rr.ravel(), cc.ravel())
            px, py = tr4326.transform(r.lon, r.lat)
            m = np.hypot(np.asarray(x) - px, np.asarray(y) - py) <= RADIUS
            with np.errstate(invalid="ignore", divide="ignore"):
                ndwi = ((g - n) / (g + n)).ravel()[m]
                mndwi = ((g - sw) / (g + sw)).ravel()[m]
            d = f"{it.datetime:%Y-%m-%d}"
            rec[f"ndwi_water_px_{d}"] = int((ndwi > 0).sum())
            rec[f"mndwi_water_px_{d}"] = int((mndwi > 0).sum())
        rows.append(rec)
    df = pd.DataFrame(rows)
    df.to_csv("analysis/s2_visibility.tsv", sep="\t", index=False)
    print(df.to_string(index=False))
    for c in [c for c in df.columns if "_px_" in c]:
        print(c, "visible:", int((df[c] >= MIN_PX).sum()), "of", len(df), "| without fish:", int((df[c][~df.fish] >= MIN_PX).sum()))


if __name__ == "__main__":
    main()

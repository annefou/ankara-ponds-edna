"""Distance from each pond to streams, other water, roads and villages (OpenStreetMap), against the eDNA results.

Source: OpenStreetMap (ODbL), read with the Overpass API (one query, bbox 40.05-40.45 N, 32.10-32.82 E, saved in
work_osm/overpass.json with its OSM timestamp; not committed): waterways river, stream, canal, ditch, drain;
water bodies (natural=water); roads (highway motorway ... residential, and track); places city, town, village,
hamlet. Distances in metres in UTM zone 36N (EPSG:32636; scale error < 0.1 % here) from the pond coordinates
(mean of the ENA sample coordinates). The pond itself: a mapped water body within 50 m of the point is taken to be
the pond and is not counted as "other water".

Position uncertainty: Sentinel-2 shows that the public coordinates miss the open water of most ponds, by up to
~200 m (README), so only differences of several hundred metres are read as meaningful.
Tests (29 ponds, descriptive): fish present vs absent, and topmouth gudgeon present vs absent, rank-sum tests on
each distance. Not a causal test; OSM completeness for small streams and tracks is not known.

Usage: pixi run osm-context   (from ankara-ponds-edna/). Writes analysis/pond_osm.tsv, analysis/osm_vs_edna.json.
"""
import json
import os
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
import shapely
from pyproj import Transformer
from scipy import stats

BBOX = "40.05,32.10,40.45,32.82"
CACHE = "work_osm/overpass.json"
QUERY = f"""[out:json][timeout:180];
(
  way["waterway"~"^(river|stream|canal|ditch|drain)$"]({BBOX});
  way["natural"="water"]({BBOX}); relation["natural"="water"]({BBOX});
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|track)$"]({BBOX});
  node["place"~"^(city|town|village|hamlet)$"]({BBOX});
);
out geom;"""
TO_UTM = Transformer.from_crs(4326, 32636, always_xy=True)
SELF_WATER_M = 50


def overpass():
    if not os.path.exists(CACHE):
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                                     data=urllib.parse.urlencode({"data": QUERY}).encode(),
                                     headers={"User-Agent": "ankara-ponds-edna (LifeWatch ERIC prototype)"})
        json.dump(json.load(urllib.request.urlopen(req, timeout=300)), open(CACHE, "w"))
    return json.load(open(CACHE))


def utm_line(geom):
    x, y = TO_UTM.transform([p["lon"] for p in geom], [p["lat"] for p in geom])
    return np.column_stack([x, y])


def layers(osm):
    out = {"stream": [], "road": [], "track": [], "water": [], "village": []}
    for e in osm["elements"]:
        t = e.get("tags", {})
        if e["type"] == "node":
            out["village"].append(shapely.Point(*TO_UTM.transform(e["lon"], e["lat"])))
        elif "waterway" in t and e.get("geometry"):
            out["stream"].append(shapely.LineString(utm_line(e["geometry"])))
        elif "highway" in t and e.get("geometry"):
            out["track" if t["highway"] == "track" else "road"].append(shapely.LineString(utm_line(e["geometry"])))
        elif t.get("natural") == "water":
            rings = [utm_line(e["geometry"])] if e.get("geometry") else [utm_line(m["geometry"]) for m in e.get("members", [])
                                                                          if m.get("role") == "outer" and m.get("geometry")]
            for r in rings:
                if len(r) >= 4:
                    out["water"].append(shapely.Polygon(r).buffer(0))
    return {k: np.array(v, dtype=object) for k, v in out.items()}


def nearest(pt, geoms):
    return float(shapely.distance(pt, geoms).min()) if len(geoms) else np.nan


def main():
    osm = overpass()
    stamp = osm.get("osm3s", {}).get("timestamp_osm_base")
    L = layers(osm)
    ponds = pd.read_csv("analysis/pond_table.tsv", sep="\t")
    rows = []
    for p in ponds.itertuples():
        pt = shapely.Point(*TO_UTM.transform(p.lon, p.lat))
        dw = shapely.distance(pt, L["water"]) if len(L["water"]) else np.array([])
        own = dw <= SELF_WATER_M
        rows.append({"pond": p.pond, "site": p.site,
                     "osm_maps_the_pond": bool(own.any()),
                     "dist_stream_m": round(nearest(pt, L["stream"])),
                     "dist_other_water_m": round(float(dw[~own].min())) if (~own).any() else None,
                     "dist_road_m": round(nearest(pt, L["road"])),
                     "dist_track_m": round(nearest(pt, L["track"])),
                     "dist_village_m": round(nearest(pt, L["village"]))})
    o = pd.DataFrame(rows)
    o.to_csv("analysis/pond_osm.tsv", sep="\t", index=False)
    m = ponds.merge(o, on=["pond", "site"])
    fish = m.fish_groups > 0
    pp = m.topmouth_gudgeon.fillna("") == "yes"
    res = {"source": f"OpenStreetMap (ODbL), Overpass API, OSM base {stamp}", "ponds": int(len(m)),
           "ponds_mapped_in_osm": int(o.osm_maps_the_pond.sum()),
           "position_uncertainty_note": "public coordinates miss the open water of most ponds by up to ~200 m",
           "fish_present": int(fish.sum()), "topmouth_gudgeon_present": int(pp.sum()), "tests": {}}
    for col in ["dist_stream_m", "dist_other_water_m", "dist_road_m", "dist_track_m", "dist_village_m"]:
        v = m[col].astype(float)
        t = {"median_all": float(v.median()), "min": float(v.min()), "max": float(v.max())}
        for name, g in (("fish", fish), ("topmouth_gudgeon", pp)):
            a, b = v[g].dropna(), v[~g].dropna()
            t[f"median_{name}_present"] = float(a.median()); t[f"median_{name}_absent"] = float(b.median())
            t[f"mannwhitney_p_{name}"] = round(float(stats.mannwhitneyu(a, b, alternative="two-sided").pvalue), 3)
        res["tests"][col] = t
    json.dump(res, open("analysis/osm_vs_edna.json", "w"), indent=1)
    print(o.to_string(index=False))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

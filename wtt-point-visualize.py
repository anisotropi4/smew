#!/usr/bin/env python3
"""wtt-visualize.py: visualize working timetable data as GIF animation"""

import datetime as dt
import io
import os
import sys

import geopandas as gp
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from imageio import mimwrite
from imageio.v3 import imread, imwrite
from shapely.geometry import box

CRS = "EPSG:27700"
# k = pl.read_ipc("output/timetable-2026-03-*.arrow")
# s.select(["start TIPLOC", "end TIPLOC"]).unique().sink_csv("TIPLOC-leg.csv")


def get_tiploc_location():
    """get_tiploc_location:"""
    r = pl.read_csv("data/TIPLOC-Locations-2026-08-18.csv")
    p = gp.points_from_xy(*r.select(["Longitude", "Latitude"]).to_numpy().T)
    rename = {
        "ID": "id",
        "Tiploc": "TIPLOC",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "GB_Location": "in GB",
        "NLCCapts-Ident": "Capitals Identification",
        "NLCLocationCode": "NLC",
        "NLCCheckChar": "NLC check char",
        "NLCDescription": "NLCDescription",
        "NLCCapriDesc": "CAPRI",
        "NLCCrsCode": "CRS",
        "NLCTiplocOwner": "Owner",
        "NLCEuroLocation": "NLCEuroLocation",
        "NLCStanoxCode": "STANOX",
        "NLCPoMcpCode": "PO MCP",
        "InCorpus": "in CORPUS",
        "InSchedule": "in SCHEDULE",
    }
    r = r.rename(rename).with_columns(pl.col("TIPLOC").str.pad_end(7))
    return gp.GeoDataFrame(r.to_pandas(), geometry=p, crs="WGS84").to_crs(CRS)


def animate_frame(gf, key, bbox, title=True, font_size=4):
    """output_animation:"""
    matplotlib.rc("font", size=font_size)
    matplotlib.rc("axes", titlesize=font_size)
    frame = []
    line = (gf["geometry"].type == "LineString").all()
    point = (gf["geometry"].type == "Point").all()
    if not (line or point):
        print("error: no geometry")
        return None
    for k, v in gf.groupby(key):
        print(k, end=" ")
        fig, ax = plt.subplots(dpi=300.0, layout="constrained")
        fig.set_figheight(3.0)
        fig.set_figwidth(1.8)
        bbox.plot(ax=ax, color="white")
        ax.axis("off")
        if title:
            ax.set_title(k, y=1.0, x=1.0, pad=0, loc="right")
        if line:
            v.plot(ax=ax, linewidth=v["count"] / 8.0, color="#ff7f00")
        else:
            v.plot(ax=ax, markersize=np.sqrt(v["count"]) / 8, color="#ff7f00")
        # else:
        #     v.plot(ax=ax, linewidth=0.0, color="#ff7f00")
        iobuffer = io.BytesIO()
        plt.savefig(iobuffer, bbox_inches="tight", pil_kwargs={"optimize": True})
        iobuffer.seek(0)
        frame.append(imread(iobuffer))
        # plt.savefig(f"image/{k}.png", bbox_inches="tight", pil_kwargs={"optimize": True})
        plt.close()
    return np.stack(frame)


def main():
    """main: main code execution block"""
    start_date = dt.datetime(2026, 5, 11)
    end_date = start_date + dt.timedelta(weeks=4)
    service = "passenger"
    fps = 6.0

    timetable = pl.scan_ipc("output/timetable-2026-0*.arrow")
    column = (
        """identity,UID,Power type,Timing load,Speed,Identity,Service code,Category,STP,ATOC,"""
        """TIPLOC,repeat,public schedule,Platform,Line,Activity,event,Path,CRS,duration,"""
        """departure,is_freight,date,schedule_t"""
    ).split(",")

    ## filter date
    timetable = timetable.filter(
        (pl.col("date") >= start_date) & (pl.col("date") < end_date)
    )
    df = (
        timetable.select(column)
        .sort(["departure", "UID", "duration"])
        .unique(["UID", "date", "duration"], keep="first", maintain_order=True)
        .with_columns(date_dt=(pl.col("date").dt.combine(pl.col("schedule_t"))))
        .with_columns(bucket_10m=pl.col("date_dt").dt.truncate("10m"))
        .group_by(["bucket_10m", "TIPLOC", "is_freight"])
        .len("count")
        .sort(["bucket_10m", "TIPLOC"])
    )
    df = df.collect().to_pandas()
    if df.empty:
        print("ERROR: empty dataframe", file=sys.stderr)
        sys.exit(1)
    tiploc_location = get_tiploc_location()
    tiploc_location = (
        tiploc_location[["TIPLOC", "geometry"]].set_index("TIPLOC").squeeze()
    )
    df = df.join(tiploc_location, on="TIPLOC")
    if not os.path.isdir("image"):
        os.mkdir("image")
    for service, is_freight in [
        ("passenger", False),
        ("freight", True),
    ]:
        print(service)
        gf = gp.GeoDataFrame(df)
        gf = gf[gf["is_freight"] == is_freight].dropna()
        bbox = gp.GeoSeries(box(*gf.total_bounds))
        frame = animate_frame(gf, "bucket_10m", bbox, title=True)
        key = str(10).zfill(2)
        speed = str(int(fps)).zfill(2)
        outstub = f"image/{start_date.date()}-{key}-{service}-{speed}"
        mimwrite(f"{outstub}.gif", frame, fps=fps, loop=0)
        imwrite(f"{outstub}.mp4", frame, fps=fps)


if __name__ == "__main__":
    main()

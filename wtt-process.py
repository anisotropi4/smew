#!/usr/bin/env python3
"""wtt-process: generate a week of timetable paths"""

import argparse
import datetime as dt

import numpy as np
import polars as pl

# START_DATE = "2025-06-08"
# START_DATE = "2025-08-04"
# START_DATE = "2026-03-06"

def _pp(df):
    """pp: pretty print polar frame for debug"""
    with pl.Config(set_tbl_cols=-1, set_tbl_hide_dataframe_shape=True):
        try:
            r = df.collect()
        except AttributeError:
            r = df
        column = r.columns
        for i in range(0, len(column), 15):
            chunk = r.columns[i : i + 15]
            print(r[chunk])
    print(r.shape)


def log_event(update, key="", start=dt.datetime.now()):
    """log_event:"""
    now = dt.datetime.now()
    if key:
        print(f"{key.ljust(12)}\t{now - start} {now - update}")
        return
    print(f"{now - start} {now - update}")


def get_current_tt(date, calendar, path):
    """get_current_tt:"""
    column = ["from", "to", "days"]
    s = calendar.filter(pl.col("date") == date)
    r = path.join(s, on=column, how="semi")
    r = r.with_columns(
        departure=pl.lit(date),
        departure_dt=pl.lit(date).cast(pl.Datetime) + pl.col("schedule_dt"),
    )
    return r


def get_wtt(date, calendar, path, path_filter=True):
    """get_wtt:"""
    day = dt.timedelta(days=1)
    working_day = date
    r = get_current_tt(working_day - day, calendar, path)
    s = get_current_tt(working_day, calendar, path)
    r = pl.concat([r, s])
    r = r.filter(pl.col("departure_dt").cast(pl.Date) == working_day)
    if path_filter:
        column = ["UID", "departure", "STP"]
        ipath = r.sort(column).select(column).unique(subset=column[:2], keep="last")
        r = r.join(ipath, on=column, how="semi")
    return r


def get_path():
    """get_path:"""
    r = pl.scan_ipc("output/wtt-path.arrow", memory_map=False)
    r = r.sort("index").with_row_index(name="ix")
    duration = get_duration(r)
    column = ["ix", "duration", "schedule_dt"]
    r = r.join(duration.rename({"end": "schedule_dt"}).select(column), on="ix")
    return r


def get_week(date):
    """get_week:"""
    start = dt.date.fromisoformat(date)
    week = pl.duration(weeks=1) - pl.duration(hours=1)
    return pl.date_range(start, start + week, interval="1d", eager=True)


def get_time(df, key):
    """get_time:"""
    r = df.with_columns(
        (
            pl.col(key).str.replace(" ", "0").str.replace("H", "3") + pl.lit("0")
        ).str.to_time(format="%H%M%S")
    )
    return r


def get_duration(path):
    """get_duration2:"""
    zero = pl.duration(seconds=0.0)
    day = pl.duration(days=1)
    t = path.select(["ix", "identity", "schedule"])
    t = get_time(t, "schedule")
    t = t.with_columns(
        start=(
            pl.when(pl.col("identity") == "LO")
            .then(pl.col("schedule"))
            .otherwise(pl.lit(None))
            .fill_null(strategy="forward")
        )
    )
    t = t.with_columns(duration=(pl.col("schedule") - pl.col("start")))
    t = t.with_columns(
        duration=pl.when(pl.col("duration") < zero)
        .then(pl.col("duration") + day)
        .otherwise(pl.col("duration"))
    )
    t = t.with_columns(end=(pl.col("start").cast(pl.Duration) + pl.col("duration")))
    return t.drop("identity")


def get_date(df):
    """get_date: where Monday = 1"""
    week = pl.duration(weeks=1)
    column = ["index", "UID", "from", "to", "days"]
    r = df.select(column)
    r = r.with_columns(
        start=pl.col("from").str.to_date(format="%y%m%d").dt.truncate("1w"),
        end=(pl.col("to").str.to_date(format="%y%m%d") + week).dt.truncate("1w"),
    )
    return r.rename({"index": "path"})


def get_calendar(df):
    """get_calendar2:"""
    r = df.filter(pl.col("identity") == "LO")
    s = get_date(r)
    column = ["path", "from", "to", "start", "end", "days"]
    r = s.select(column).unique(column[1:]).sort("path")
    r = r.with_columns(
        date=pl.date_ranges("start", "end", interval="1d", closed="left")
    ).explode("date")
    r = (
        r.with_columns(
            days_bitmap=pl.col("days").str.to_integer(base=2),
            date_bitmap=np.right_shift(64, pl.col("date").dt.weekday() - 1).cast(
                pl.Int64
            ),
        )
        .filter(pl.col("days_bitmap") & pl.col("date_bitmap") > 0)
        .drop(["path", "days_bitmap", "date_bitmap"])
    )
    column = "from,to,start,end,days,date".split(",")
    return r.sort(column).with_row_index(name="index")


def get_wtt_week(start_date, calendar, path):
    """get_wtt_week:"""
    s = []
    for date in iter(get_week(start_date)):
        update = dt.datetime.now()
        print(date)
        k = get_wtt(date, calendar, path)
        k = k.with_columns(
            is_freight=pl.when(pl.col("ATOC") == "ZZ").then(True).otherwise(False),
            date=pl.col("departure_dt").dt.truncate("1d"),
            schedule_t=pl.col("departure_dt").dt.time(),
        ).sort(["departure_dt", "UID"])
        s.append(k)
        log_event(update)
        update = dt.datetime.now()
        k.sink_ipc(f"output/timetable-{date}.arrow")
        log_event(update)
    # r = pl.collect_all(s)
    return s


def main(start_date):
    """main: core execution function"""
    update = dt.datetime.now()
    path = get_path()
    log_event(update)
    update = dt.datetime.now()
    calendar = get_calendar(path)
    log_event(update)
    update = dt.datetime.now()
    _ = get_wtt_week(start_date, calendar, path)
    log_event(update)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="generate a week of timetable paths"
    )
    default = "2026-03-06"
    parser.add_argument(
        "startdate",
        type=str,
        help=f"first day of week to process (default {default})",
        nargs="?",
        default=default,
    )
    args = parser.parse_args()
    main(args.startdate)

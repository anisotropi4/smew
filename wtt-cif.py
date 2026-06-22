#!/usr/bin/env python3
"""wtt-cif: convert GB CIF file to arrow files"""

import datetime as dt
import lzma
import os
from itertools import accumulate

import polars as pl
import pyarrow as pa

FILEPATH = "data/CIF_ALL_FULL_DAILY_toc-full-20260311.CIF.gz"


def log_event(update, key="", start=dt.datetime.now()):
    """log_event:"""
    now = dt.datetime.now()
    if key:
        print(f"{key.ljust(6)}\t{now - start} {now - update}")
        return
    print(f"{now - start} {now - update}")


def get_cif():
    """get_cif: return CIF data if xz compressed or otherwise"""
    if FILEPATH[-3:] == ".xz":
        with lzma.open(FILEPATH, "rb") as fin:
            return read_cif(fin)
    with open(FILEPATH, "rb") as fin:
        return read_cif(fin)


def read_cif(fin):
    """read_df:"""
    schema = {"full": pl.String}
    r = pl.scan_csv(
        fin,
        has_header=False,
        separator="\n",
        quote_char=None,
        schema=schema,
        infer_schema_length=0,
    ).with_row_index()
    r = r.with_columns(
        pl.col("index").alias("ix"),
        pl.col("full").str.slice(0, length=2).alias("identity"),
    )
    return r


def get_col(s):
    """get_col:"""
    return list(map(int, s.split(",")))


def get_slice(df, col, column):
    """get_slice:"""
    zlist = zip(accumulate(col[1:-1]), col[2:], column[1:])
    s = [pl.col("full").str.slice(int(n), m).alias(name) for n, m, name in zlist]
    return df.with_columns(s)


def get_record_line(df, key, col, column):
    """get_record:"""
    r = get_slice(df.filter(pl.col("identity") == key), col, column)
    return r


def get_hd(df):
    """get_hd: col holds column width, column field names"""
    # HD = get_record(record_id, "HD", [0, 2, 20, 6, 4, 7, 7, 1, 1, 6, 6])
    col = get_col("0,2,20,6,4,7,7,1,1,6,6")
    column = (
        """identity,Mainframe identity,Extract date,Extract time,Current reference,"""
        """Last reference,Indicator,Version,Start,End"""
    ).split(",")
    update = dt.datetime.now()
    hd_data = get_record_line(df, "HD", col, column)
    log_event(update, "HD")
    return hd_data.drop("full")


def get_ti(df):
    """get_ti: TIPLOC record"""
    update = dt.datetime.now()
    col = get_col("0,2,7,2,6,1,26,5,4,3,16")
    column = (
        """identity,TIPLOC,Capitals Identification,NALCO,NLC check character,TPS description,"""
        """STANOX,PO MCP,CRS,CAPRI"""
    ).split(",")
    ti_data = get_record_line(df, "TI", col, column)
    log_event(update, "TI")
    return ti_data.drop("full")


def get_aa(df):
    """get_aa: association record"""
    update = dt.datetime.now()
    col = get_col("0,2,1,6,6,6,6,7,2,1,7,1,1,1,1,31,1")
    column = (
        """identity,Transaction,UID,Associated UID,Start date,End date,days,Category,"""
        """Date indicator,TIPLOC,Base suffix,Association suffix,Diagram,Association,Spare,"""
        """STP indicator"""
    ).split(",")
    aa_data = get_record_line(df, "AA", col, column)
    log_event(update, "AA")
    return aa_data.drop("full")


def get_cr(df):
    """get_cr: change en route record"""
    update = dt.datetime.now()
    col = get_col("0,2,7,1,2,4,4,1,8,1,3,4,3,6,1,1,1,1,4,4,4,5,8")
    column = (
        """identity,TIPLOC,repeat,Category,Identity,Headcode,Course indicator,Service code,"""
        """Portion ID,Power type,Timing load,Speed,Operating,Seating class,Sleepers,Reservations,"""
        """Connection,Catering,Branding,Traction,UIC Code,RSID"""
    ).split(",")
    cr_data = get_record_line(df, "CR", col, column)
    log_event(update, "CR")
    return cr_data.drop("full")


def get_bs(df):
    """get_bs: basic schedule"""
    update = dt.datetime.now()
    col = get_col("0,2,1,6,6,6,7,1,1,2,4,4,1,8,1,3,4,3,6,1,1,1,1,4,4,1,1")
    column = (
        """identity,Transaction,UID,from,to,days,Bank Holiday,Status,Category,Identity,Headcode,"""
        """Course indicator,Service code,Portion ID,Power type,Timing load,Speed,Operating,"""
        """Seating class,Sleepers,Reservations,Connection,Catering,Branding,Spare,STP"""
    ).split(",")
    bs_data = get_record_line(df, "BS", col, column)
    log_event(update, "BS")
    return bs_data.drop("full")


def get_bx(df):
    """get_bx: extra schedule record"""
    update = dt.datetime.now()
    col = get_col("0,2,4,5,2,1,8,1")
    column = (
        """identity,Traction class,UIC code,ATOC,Applicable timetable,RSID,Data source"""
    ).split(",")
    bx_data = get_record_line(df, "BX", col, column)
    log_event(update, "BX")
    return bx_data.drop("full")


def get_lo(df):
    """get_lo: origin record"""
    update = dt.datetime.now()
    col = get_col("0,2,7,1,5,4,3,3,2,2,12,2,3")
    column = (
        """identity,TIPLOC,repeat,schedule,public schedule,Platform,Line,Engineering allowance,"""
        """Pathing allowance,Activity,Performance allowance,Thameslink"""
    ).split(",")
    lo_data = get_record_line(df, "LO", col, column)
    log_event(update, "LO")
    return lo_data.drop("full")


def get_li(df):
    """get_li: intermediate record"""
    update = dt.datetime.now()
    col = get_col("0,2,7,1,5,5,5,4,4,3,3,3,12,2,2,2,5")
    column = (
        """identity,TIPLOC,repeat,Arrival,Departure,Pass,Public arrival,Public departure,"""
        """Platform,Line,Path,Activity,Engineering allowance,Pathing allowance,"""
        """Performance allowance,Thameslink"""
    ).split(",")
    li_data = get_record_line(df, "LI", col, column)
    log_event(update, "LI")
    return li_data.drop("full")


def get_lt(df):
    """get_lt: terminate record"""
    update = dt.datetime.now()
    col = get_col("0,2,7,1,5,4,3,3,12,3")
    column = (
        """identity,TIPLOC,repeat,schedule,public schedule,Platform,Path,Activity,Thameslink"""
    ).split(",")
    lt_data = get_record_line(df, "LT", col, column)
    log_event(update, "LT")
    return lt_data.drop("full")


def get_zz(df):
    """get_zz: end record"""
    update = dt.datetime.now()
    column = ["identity"]
    zz_data = get_record_line(df, "ZZ", [0, 2], column)
    log_event(update, "ZZ")
    return zz_data.drop("full")


def get_basic_schedule(bs_data, bx_data):
    """get_basic_schedule: combine schedule and extra data"""
    column = (
        """index,identity,Transaction,UID,from,to,days,Power type,Timing load,Speed,Identity,"""
        """Headcode,Service code,Status,Category,STP"""
    ).split(",")
    r = bs_data.select(column)
    s = bx_data.select(["index", "ATOC"])
    s = s.with_columns(index=pl.col("index") - 1)
    r = r.join(s, on="index", how="full", coalesce=True).fill_null("")
    return r.sort("index")


def get_basic_path(df):
    """get_path:"""
    update = dt.datetime.now()
    lo_data = get_lo(df)
    li_data = get_li(df)
    lt_data = get_lt(df)
    origin = lo_data.with_columns(pl.lit("O").alias("event"))
    terminate = lt_data.with_columns(pl.lit("T").alias("event"))
    column = (
        """index,identity,TIPLOC,Pass,Public arrival,Platform,Line,Engineering allowance,"""
        """Pathing allowance,Activity,Performance allowance,Thameslink"""
    ).split(",")
    service = li_data.filter(pl.col("Pass").str.strip_chars() != "").select(column)
    service = service.rename({"Pass": "schedule", "Public arrival": "public schedule"})
    service = service.with_columns(pl.lit("P").alias("event"))
    column = (
        """index,identity,TIPLOC,Arrival,Public arrival,Platform,Line,Engineering allowance,"""
        """Pathing allowance,Activity,Performance allowance,Thameslink"""
    ).split(",")
    arrive = li_data.filter(pl.col("Pass").str.strip_chars() == "").select(column)
    arrive = arrive.rename({"Arrival": "schedule", "Public arrival": "public schedule"})
    arrive = arrive.with_columns(pl.lit("A").alias("event"))
    column = (
        """index,identity,TIPLOC,Departure,Public departure,Platform,Line,Engineering allowance,"""
        """Pathing allowance,Activity,Performance allowance,Thameslink"""
    ).split(",")
    depart = li_data.filter(pl.col("Pass").str.strip_chars() == "").select(column)
    depart = depart.rename(
        {"Departure": "schedule", "Public departure": "public schedule"}
    )
    depart = depart.with_columns(pl.lit("D").alias("event"))
    r = pl.concat(
        [origin, service, arrive, depart, terminate], how="diagonal"
    ).fill_null("")
    log_event(update)
    return r


def get_path(basic_schedule, base_change, base_path):
    """get_path:"""
    r = pl.concat([basic_schedule, base_change, base_path], how="diagonal")
    r = r.sort("index").fill_null(strategy="forward")
    return r


def batch_ipc(lf, outpath, chunk=1_024):
    """batch_ipc:"""
    writer = None
    option = pa.ipc.IpcWriteOptions(compression="zstd")
    try:
        for df in lf.collect_batches(chunk_size=chunk):
            arrow_table = df.to_arrow()
            if writer is None:
                writer = pa.ipc.new_file(
                    outpath,
                    arrow_table.schema,
                    options=option,
                )
            writer.write_table(arrow_table)
    except StopIteration:
        if writer:
            writer.close()
    finally:
        if writer:
            writer.close()


def main():
    """main:"""
    update = dt.datetime.now()
    df = get_cif()
    if not os.path.exists("output"):
        os.makedirs("output")
    hd = get_hd(df).collect()
    hd_date = str(dt.date.strptime(hd["Start"][0], "%d%m%y"))
    print(f"HD{" "*6}{hd_date}")
    aa_data = get_aa(df)
    aa_data.sink_ipc("output/aa_data.arrow", compression="zstd")
    log_event(update)
    bs_data = get_bs(df)
    bx_data = get_bx(df)
    basic_schedule = get_basic_schedule(bs_data, bx_data)
    basic_schedule.sink_ipc("output/bs_data.arrow", compression="zstd")
    base_path = get_basic_path(df)
    cr_data = get_cr(df)
    column = (
        """index,identity,TIPLOC,Category,Power type,Timing load,Speed,Identity,Headcode,"""
        """Service code"""
    ).split(",")
    base_change = cr_data.select(column)
    path = get_path(basic_schedule, base_change, base_path)
    path = path.filter(~pl.col("identity").is_in(["BS", "CR"])).drop(
        ["Thameslink", "ix"]
    )
    ti_data = get_ti(df)
    ti_data.sink_ipc("output/ti_data.arrow", compression="zstd")
    path = path.join(ti_data.select(["TIPLOC", "CRS"]), on="TIPLOC")
    log_event(update, "TT")
    update = dt.datetime.now()
    path.sink_ipc("output/wtt-path.arrow", compression="zstd")
    log_event(update, "WTT")


if __name__ == "__main__":
    main()

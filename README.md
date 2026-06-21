# smew
This is another script to process the British railway Common Interface File (CIF) timetable. This is named after a species Northern European and Asian duck.

This implementation uses `python polars` converts the CIF timetable into a bespoke timetable arrow file in the `output/wtt-path.arrow` that can then be used for further analysis.

## Configuration

These scripts require a working [`python3`](https://www.python.org/) and tested using a virtual environment is used to manage dependencies with [`uv`](https://docs.astral.sh/uv/). As follows:

```
$ uv venv venv
$ uv pip install --upgrade -r requirements.txt
$ source venv/bin/activate
```

## Convert CIF to arrow

The `wtt-cif.py` script convert the CIF file in the `data` directory and output a series of arrow files in `output`.

```
$ ./wtt-cif.py
HD    	0:00:00.000565 0:00:00.000145
HD      2026-03-06
AA    	0:00:00.539526 0:00:00.000121
0:00:00.995235 0:00:00.995227
BS    	0:00:00.995516 0:00:00.000244
BX    	0:00:00.995585 0:00:00.000044
LO    	0:00:01.542706 0:00:00.000160
LI    	0:00:01.542880 0:00:00.000129
LT    	0:00:01.542980 0:00:00.000077
0:00:01.543199 0:00:00.000658
CR    	0:00:01.543331 0:00:00.000123
TI    	0:00:01.543582 0:00:00.000063
TT    	0:00:01.978676 0:00:01.978668
WTT   	0:00:06.916996 0:00:04.938287
```

## Generate a daily working timetable for a week

The `wtt-process.py` script convert the `wtt-path.arrow` file in the `output` directory and output a week of daily working timetable arrow files `timetable-YYYY-MM-DD.arrow` in `output`.

```
$ ./wtt-process.py
0:00:00.000564 0:00:00.000559
0:00:00.000765 0:00:00.000182
2026-03-06
0:00:00.003343 0:00:00.000162
0:00:07.216509 0:00:07.213159
2026-03-07
0:00:07.216861 0:00:00.000308
0:00:14.228062 0:00:07.011193
2026-03-08
0:00:14.228386 0:00:00.000284
0:00:21.008922 0:00:06.780529
2026-03-09
0:00:21.009191 0:00:00.000229
0:00:28.025732 0:00:07.016536
2026-03-10
0:00:28.026015 0:00:00.000241
0:00:35.093771 0:00:07.067750
2026-03-11
0:00:35.094020 0:00:00.000213
0:00:42.185818 0:00:07.091793
2026-03-12
0:00:42.186071 0:00:00.000217
0:00:49.332315 0:00:07.146239
0:00:49.332358 0:00:49.331585
```

### `START_DATE` constant
Change the value of the `START_DATE` parameter in the `wtt-process.py` script to vary the start date. It is currently:

```
START_DATE = "2026-03-06"
```
## Attribution

The published CIF timetable data is a point-in-time copy of the Network Rail Schedule (NWR Schedule) CIF file from the [Rail Data Marketplace (RDM)](https://raildata.org.uk/dataProduct/P-dbd92416-2f09-4f72-ad42-d53bbfec50f3/overview), licensed under the [Open Government (OGL3) license](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

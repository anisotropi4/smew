# smew
This is another script to process the British railway Common Interface File (CIF) timetable. This is named after a species Northern European and Asian duck.

This implementation uses 

* [`python polars`](https://pypi.org/project/polars/) converts the CIF timetable into a bespoke timetable arrow file in the `output/wtt-path.arrow` that can then be used for further analysis. 
* [`python geopandas`](https://geopandas.org/) to render the arrow file in the `output/wtt-path.arrow` into a geospatial representation that can be drawn using [`matplotlib`](https://matplotlib.org/). 
* [`python imageio`](https://pypi.org/project/ImageIO/) to render animagted geospatial frames.

## Configuration

These scripts require a working [`python3`](https://www.python.org/) and tested using a virtual environment is used to manage dependencies with [`uv`](https://docs.astral.sh/uv/). As follows:

```
$ uv venv venv
$ uv pip install --upgrade -r requirements.txt
$ source venv/bin/activate
```

The `mp4` animation requires `ffmpeg` to be installed.

## Convert CIF to arrow

The `wtt-cif.py` script convert the CIF file in the `data` directory and output a series of arrow files in `output`.

```
$ ./wtt-cif.py
HD    	0:00:00.002265 0:00:00.000165
HD      2026-05-08
AA    	0:00:00.492446 0:00:00.000136
0:00:00.906209 0:00:00.904629
BS    	0:00:00.906440 0:00:00.000195
BX    	0:00:00.906509 0:00:00.000043
LO    	0:00:01.390110 0:00:00.000133
LI    	0:00:01.390219 0:00:00.000065
LT    	0:00:01.390267 0:00:00.000038
0:00:01.390445 0:00:00.000472
CR    	0:00:01.390540 0:00:00.000087
TI    	0:00:01.390733 0:00:00.000043
TT    	0:00:01.801581 0:00:01.800001
WTT   	0:00:05.241852 0:00:03.440238
```

## Generate a daily working timetable for a week

The `wtt-process.py` script convert the `wtt-path.arrow` file in the `output` directory and output a week of daily working timetable arrow files `timetable-YYYY-MM-DD.arrow` in `output`.

```
$ ./wtt-process.py
0:00:00.002315 0:00:00.000556
0:00:00.002508 0:00:00.000175
2026-05-11
0:00:00.005022 0:00:00.000169
0:00:06.061140 0:00:06.056111
2026-05-12
0:00:06.061438 0:00:00.000259
0:00:12.009841 0:00:05.948396
2026-05-13
0:00:12.010110 0:00:00.000235
0:00:17.970767 0:00:05.960651
2026-05-14
0:00:17.971097 0:00:00.000289
0:00:23.936202 0:00:05.965097
2026-05-15
0:00:23.936502 0:00:00.000257
0:00:29.970415 0:00:06.033907
2026-05-16
0:00:29.970725 0:00:00.000275
0:00:35.823897 0:00:05.853164
2026-05-17
0:00:35.824166 0:00:00.000232
0:00:41.534204 0:00:05.710033
0:00:41.534245 0:00:41.531730
```

## Generate a working timetable point visualization
The `wtt-point-visualize.py` script convert the `timetable-<yyyy-mm-dd>.arrow` files in the `output` directory and output an animated service-count `gif` and `mp4` for TIPLOC point location in the `images` directory agregated in 10 minute slices at six frames-per-second .

```
$ ./wtt-point-visualize.py
IMAGEIO FFMPEG_WRITER WARNING: input image is not divisible by macro_block_size=16, 
resizing from (574, 877) to (576, 880) to ensure video compatibility with most codecs 
and players. To prevent resizing, make your input image divisible by the macro_block_
size or set the macro_block_size to 1 (risking incompatibility).
2026-05-11 00:00:00 2026-05-11 00:10:00 2026-05-11 00:20:00 2026-05-11 00:30:00 
2026-05-11 00:40:00 2026-05-11 00:50:00 2026-05-11 01:00:00 2026-05-11 01:10:00 
2026-05-11 01:20:00 2026-05-11 01:30:00 2026-05-11 01:40:00 2026-05-11 01:50:00 
2026-05-11 02:00:00 2026-05-11 02:10:00 2026-05-11 02:20:00 2026-05-11 02:30:00 
2026-05-11 02:40:00 2026-05-11 02:50:00 2026-05-11 03:00:00 2026-05-11 03:10:00 
...
```

### imageio FFMPEG warning
The `imageio` uses `ffmpeg` to create the `mp4` output. For compatability it issues a warning about the input image size which should be ignored.

### `START_DATE` constant
Change the value of the `START_DATE` parameter in the `wtt-process.py` script to vary the start date. It is currently:

```
START_DATE = "2026-05-11"
```

## Attribution

The published CIF timetable data is a point-in-time copy of the Network Rail Schedule (NWR Schedule) CIF file from the [Rail Data Marketplace (RDM)](https://raildata.org.uk/dataProduct/P-dbd92416-2f09-4f72-ad42-d53bbfec50f3/overview), licensed under the [Open Government (OGL3) license](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). Other data is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The project [Apache 2.0 license is here](LICENSE).

## Thanks to
[Squingo44](https://github.com/squingo44) for the suggested improvement.

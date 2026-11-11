# UCI SECOM Data Dictionary

## 1. Documented Fields (`secom_labels.data`)

| Field Name | Source File | Col (1-based) | Type | Values / Format | Missing | Unique | Notes |
|---|---|---:|---|---|---:|---:|---|
| `target_label` | `secom_labels.data` | 1 | int64 (categorical binary) | -1 = Pass, 1 = Fail (in-house line testing) | 0 (0.0%) | 2 | Official UCI API/web summary defines -1 = Pass and 1 = Fail (104 fails, 1463 passes). Note: secom.names line 46 has a known '.1' typo for '-1'. |
| `timestamp_raw` | `secom_labels.data` | 2 | string -> datetime64[ns] | DD/MM/YYYY HH:MM:SS (test point timestamp; no timezone specified) | 0 (0.0%) | 1534 | Timestamp associated with the specific in-house line test point; raw file is monotonically non-decreasing (0 backward steps) but has 32 repeated timestamps. |

## 2. Anonymous Sensor / Process Signal Fields (`secom.data`)

- **Total anonymous sensor columns:** 590 (`sensor_000` to `sensor_589`)
- **Provenance & Naming Status:** The original UCI SECOM release provides **no physical sensor names, engineering units, tool IDs, or process-stage descriptions** for the 590 columns in `secom.data`. All columns are strictly anonymous real-valued process signals/measurement points (`NaN` for missing).
- **Constant (zero-variance) sensors:** 116
- **Sensors with >50% missing values:** 28

The full machine-readable dictionary for all 592 fields (`2` documented + `590` anonymous) is saved in [`docs/data_dictionary.csv`](data_dictionary.csv).

### Full Anonymous Sensor Table (`sensor_000` – `sensor_589`)

| Field Name | 0-Based Idx | 1-Based Col | Status | Missing Count (%) | Unique Non-Null | Min | Max | Mean | Std | Notes |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| `sensor_000` | 0 | 1 | Anonymous | 6 (0.3829%) | 1520 | 2743 | 3356 | 3014 | 73.62 | Active anonymous numeric sensor/signal |
| `sensor_001` | 1 | 2 | Anonymous | 7 (0.4467%) | 1504 | 2159 | 2846 | 2496 | 80.41 | Active anonymous numeric sensor/signal |
| `sensor_002` | 2 | 3 | Anonymous | 14 (0.8934%) | 507 | 2061 | 2315 | 2201 | 29.51 | Active anonymous numeric sensor/signal |
| `sensor_003` | 3 | 4 | Anonymous | 14 (0.8934%) | 518 | 0 | 3715 | 1396 | 441.7 | Active anonymous numeric sensor/signal |
| `sensor_004` | 4 | 5 | Anonymous | 14 (0.8934%) | 503 | 0.6815 | 1115 | 4.197 | 56.36 | Active anonymous numeric sensor/signal |
| `sensor_005` | 5 | 6 | Anonymous | 14 (0.8934%) | 1 | 100 | 100 | 100 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_006` | 6 | 7 | Anonymous | 14 (0.8934%) | 510 | 82.13 | 129.3 | 101.1 | 6.237 | Active anonymous numeric sensor/signal |
| `sensor_007` | 7 | 8 | Anonymous | 9 (0.5743%) | 89 | 0 | 0.1286 | 0.1218 | 0.008961 | Active anonymous numeric sensor/signal |
| `sensor_008` | 8 | 9 | Anonymous | 2 (0.1276%) | 1208 | 1.191 | 1.656 | 1.463 | 0.0739 | Active anonymous numeric sensor/signal |
| `sensor_009` | 9 | 10 | Anonymous | 2 (0.1276%) | 568 | -0.0534 | 0.0749 | -0.000841 | 0.01512 | Active anonymous numeric sensor/signal |
| `sensor_010` | 10 | 11 | Anonymous | 2 (0.1276%) | 392 | -0.0349 | 0.053 | 0.000146 | 0.009302 | Active anonymous numeric sensor/signal |
| `sensor_011` | 11 | 12 | Anonymous | 2 (0.1276%) | 378 | 0.6554 | 0.9848 | 0.9644 | 0.01245 | Active anonymous numeric sensor/signal |
| `sensor_012` | 12 | 13 | Anonymous | 2 (0.1276%) | 1547 | 182.1 | 272 | 200 | 3.257 | Active anonymous numeric sensor/signal |
| `sensor_013` | 13 | 14 | Anonymous | 3 (0.1914%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_014` | 14 | 15 | Anonymous | 3 (0.1914%) | 1555 | 2.249 | 19.55 | 9.005 | 2.797 | Active anonymous numeric sensor/signal |
| `sensor_015` | 15 | 16 | Anonymous | 3 (0.1914%) | 1561 | 333.4 | 824.9 | 413.1 | 17.22 | Active anonymous numeric sensor/signal |
| `sensor_016` | 16 | 17 | Anonymous | 3 (0.1914%) | 1477 | 4.47 | 102.9 | 9.908 | 2.404 | Active anonymous numeric sensor/signal |
| `sensor_017` | 17 | 18 | Anonymous | 3 (0.1914%) | 281 | 0.5794 | 0.9848 | 0.9714 | 0.01206 | Active anonymous numeric sensor/signal |
| `sensor_018` | 18 | 19 | Anonymous | 3 (0.1914%) | 1548 | 169.2 | 215.6 | 190 | 2.781 | Active anonymous numeric sensor/signal |
| `sensor_019` | 19 | 20 | Anonymous | 10 (0.6382%) | 361 | 9.877 | 12.99 | 12.48 | 0.218 | Active anonymous numeric sensor/signal |
| `sensor_020` | 20 | 21 | Anonymous | 0 (0.0%) | 552 | 1.18 | 1.453 | 1.405 | 0.01674 | Active anonymous numeric sensor/signal |
| `sensor_021` | 21 | 22 | Anonymous | 2 (0.1276%) | 1295 | -7150 | 0 | -5618 | 626.8 | Active anonymous numeric sensor/signal |
| `sensor_022` | 22 | 23 | Anonymous | 2 (0.1276%) | 1176 | 0 | 3656 | 2699 | 295.5 | Active anonymous numeric sensor/signal |
| `sensor_023` | 23 | 24 | Anonymous | 2 (0.1276%) | 1480 | -9987 | 2363 | -3806 | 1380 | Active anonymous numeric sensor/signal |
| `sensor_024` | 24 | 25 | Anonymous | 2 (0.1276%) | 1494 | -1.48e+04 | 1.411e+04 | -298.6 | 2903 | Active anonymous numeric sensor/signal |
| `sensor_025` | 25 | 26 | Anonymous | 2 (0.1276%) | 704 | 0 | 1.383 | 1.204 | 0.1776 | Active anonymous numeric sensor/signal |
| `sensor_026` | 26 | 27 | Anonymous | 2 (0.1276%) | 624 | 0 | 2.053 | 1.938 | 0.1895 | Active anonymous numeric sensor/signal |
| `sensor_027` | 27 | 28 | Anonymous | 2 (0.1276%) | 1148 | 0 | 7.659 | 6.639 | 1.244 | Active anonymous numeric sensor/signal |
| `sensor_028` | 28 | 29 | Anonymous | 2 (0.1276%) | 869 | 59.4 | 77.9 | 69.5 | 3.461 | Active anonymous numeric sensor/signal |
| `sensor_029` | 29 | 30 | Anonymous | 2 (0.1276%) | 188 | 0.6667 | 3.511 | 2.366 | 0.4087 | Active anonymous numeric sensor/signal |
| `sensor_030` | 30 | 31 | Anonymous | 2 (0.1276%) | 842 | 0.0341 | 0.2851 | 0.1842 | 0.03294 | Active anonymous numeric sensor/signal |
| `sensor_031` | 31 | 32 | Anonymous | 2 (0.1276%) | 1275 | 2.07 | 4.804 | 3.673 | 0.5353 | Active anonymous numeric sensor/signal |
| `sensor_032` | 32 | 33 | Anonymous | 1 (0.0638%) | 338 | 83.18 | 105.6 | 85.34 | 2.027 | Active anonymous numeric sensor/signal |
| `sensor_033` | 33 | 34 | Anonymous | 1 (0.0638%) | 330 | 7.603 | 23.35 | 8.96 | 1.344 | Active anonymous numeric sensor/signal |
| `sensor_034` | 34 | 35 | Anonymous | 1 (0.0638%) | 329 | 49.83 | 59.77 | 50.58 | 1.183 | Active anonymous numeric sensor/signal |
| `sensor_035` | 35 | 36 | Anonymous | 1 (0.0638%) | 331 | 63.68 | 94.26 | 64.56 | 2.575 | Active anonymous numeric sensor/signal |
| `sensor_036` | 36 | 37 | Anonymous | 1 (0.0638%) | 330 | 40.23 | 50.17 | 49.42 | 1.183 | Active anonymous numeric sensor/signal |
| `sensor_037` | 37 | 38 | Anonymous | 1 (0.0638%) | 325 | 64.92 | 67.96 | 66.22 | 0.3041 | Active anonymous numeric sensor/signal |
| `sensor_038` | 38 | 39 | Anonymous | 1 (0.0638%) | 329 | 84.73 | 88.42 | 86.84 | 0.4468 | Active anonymous numeric sensor/signal |
| `sensor_039` | 39 | 40 | Anonymous | 1 (0.0638%) | 333 | 111.7 | 133.4 | 118.7 | 1.807 | Active anonymous numeric sensor/signal |
| `sensor_040` | 40 | 41 | Anonymous | 24 (1.5316%) | 291 | 1.434 | 86.12 | 67.9 | 24.06 | Active anonymous numeric sensor/signal |
| `sensor_041` | 41 | 42 | Anonymous | 24 (1.5316%) | 315 | -0.0759 | 37.88 | 3.353 | 2.36 | Active anonymous numeric sensor/signal |
| `sensor_042` | 42 | 43 | Anonymous | 1 (0.0638%) | 1 | 70 | 70 | 70 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_043` | 43 | 44 | Anonymous | 1 (0.0638%) | 1523 | 342.8 | 377.3 | 355.5 | 6.235 | Active anonymous numeric sensor/signal |
| `sensor_044` | 44 | 45 | Anonymous | 1 (0.0638%) | 1376 | 9.464 | 11.05 | 10.03 | 0.175 | Active anonymous numeric sensor/signal |
| `sensor_045` | 45 | 46 | Anonymous | 1 (0.0638%) | 1520 | 108.8 | 176.3 | 136.7 | 7.849 | Active anonymous numeric sensor/signal |
| `sensor_046` | 46 | 47 | Anonymous | 1 (0.0638%) | 1562 | 699.8 | 789.8 | 733.7 | 12.17 | Active anonymous numeric sensor/signal |
| `sensor_047` | 47 | 48 | Anonymous | 1 (0.0638%) | 1341 | 0.4967 | 1.511 | 1.178 | 0.1896 | Active anonymous numeric sensor/signal |
| `sensor_048` | 48 | 49 | Anonymous | 1 (0.0638%) | 1486 | 125.8 | 163.3 | 140 | 4.524 | Active anonymous numeric sensor/signal |
| `sensor_049` | 49 | 50 | Anonymous | 1 (0.0638%) | 1 | 1 | 1 | 1 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_050` | 50 | 51 | Anonymous | 1 (0.0638%) | 1520 | 607.4 | 667.7 | 632.3 | 8.644 | Active anonymous numeric sensor/signal |
| `sensor_051` | 51 | 52 | Anonymous | 1 (0.0638%) | 1562 | 40.26 | 258.5 | 157.4 | 60.93 | Active anonymous numeric sensor/signal |
| `sensor_052` | 52 | 53 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_053` | 53 | 54 | Anonymous | 4 (0.2553%) | 153 | 3.706 | 4.764 | 4.593 | 0.05495 | Active anonymous numeric sensor/signal |
| `sensor_054` | 54 | 55 | Anonymous | 4 (0.2553%) | 169 | 3.932 | 5.011 | 4.839 | 0.05958 | Active anonymous numeric sensor/signal |
| `sensor_055` | 55 | 56 | Anonymous | 4 (0.2553%) | 107 | 2801 | 2936 | 2856 | 25.75 | Active anonymous numeric sensor/signal |
| `sensor_056` | 56 | 57 | Anonymous | 4 (0.2553%) | 187 | 0.8755 | 0.9378 | 0.9288 | 0.006807 | Active anonymous numeric sensor/signal |
| `sensor_057` | 57 | 58 | Anonymous | 4 (0.2553%) | 159 | 0.9319 | 0.9598 | 0.9492 | 0.004176 | Active anonymous numeric sensor/signal |
| `sensor_058` | 58 | 59 | Anonymous | 4 (0.2553%) | 382 | 4.22 | 4.848 | 4.593 | 0.0851 | Active anonymous numeric sensor/signal |
| `sensor_059` | 59 | 60 | Anonymous | 7 (0.4467%) | 1500 | -28.99 | 168.1 | 2.96 | 9.532 | Active anonymous numeric sensor/signal |
| `sensor_060` | 60 | 61 | Anonymous | 6 (0.3829%) | 1498 | 324.7 | 373.9 | 355.2 | 6.028 | Active anonymous numeric sensor/signal |
| `sensor_061` | 61 | 62 | Anonymous | 6 (0.3829%) | 1418 | 9.461 | 11.78 | 10.42 | 0.2749 | Active anonymous numeric sensor/signal |
| `sensor_062` | 62 | 63 | Anonymous | 6 (0.3829%) | 1518 | 81.49 | 287.2 | 116.5 | 8.629 | Active anonymous numeric sensor/signal |
| `sensor_063` | 63 | 64 | Anonymous | 7 (0.4467%) | 1534 | 1.659 | 188.1 | 13.99 | 7.12 | Active anonymous numeric sensor/signal |
| `sensor_064` | 64 | 65 | Anonymous | 7 (0.4467%) | 1496 | 6.448 | 48.99 | 20.54 | 4.977 | Active anonymous numeric sensor/signal |
| `sensor_065` | 65 | 66 | Anonymous | 7 (0.4467%) | 1550 | 4.308 | 118.1 | 27.13 | 7.122 | Active anonymous numeric sensor/signal |
| `sensor_066` | 66 | 67 | Anonymous | 6 (0.3829%) | 1559 | 632.4 | 770.6 | 706.7 | 11.62 | Active anonymous numeric sensor/signal |
| `sensor_067` | 67 | 68 | Anonymous | 6 (0.3829%) | 1306 | 0.4137 | 7273 | 16.72 | 307.5 | Active anonymous numeric sensor/signal |
| `sensor_068` | 68 | 69 | Anonymous | 6 (0.3829%) | 1479 | 87.03 | 167.8 | 147.4 | 4.24 | Active anonymous numeric sensor/signal |
| `sensor_069` | 69 | 70 | Anonymous | 6 (0.3829%) | 1 | 1 | 1 | 1 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_070` | 70 | 71 | Anonymous | 6 (0.3829%) | 1533 | 581.8 | 722.6 | 619.1 | 9.539 | Active anonymous numeric sensor/signal |
| `sensor_071` | 71 | 72 | Anonymous | 6 (0.3829%) | 1557 | 21.43 | 238.5 | 104.3 | 31.65 | Active anonymous numeric sensor/signal |
| `sensor_072` | 72 | 73 | Anonymous | 794 (50.6701%) | 773 | -59.48 | 175.4 | 150.4 | 18.39 | High missingness (>50% NaN) |
| `sensor_073` | 73 | 74 | Anonymous | 794 (50.6701%) | 770 | 456 | 692.4 | 468 | 17.63 | High missingness (>50% NaN) |
| `sensor_074` | 74 | 75 | Anonymous | 6 (0.3829%) | 2 | 0 | 4.196 | 0.002688 | 0.1062 | Active anonymous numeric sensor/signal |
| `sensor_075` | 75 | 76 | Anonymous | 24 (1.5316%) | 675 | -0.1049 | 0.2315 | -0.006903 | 0.02229 | Active anonymous numeric sensor/signal |
| `sensor_076` | 76 | 77 | Anonymous | 24 (1.5316%) | 891 | -0.1862 | 0.0723 | -0.02939 | 0.0332 | Active anonymous numeric sensor/signal |
| `sensor_077` | 77 | 78 | Anonymous | 24 (1.5316%) | 842 | -0.1046 | 0.1331 | -0.007041 | 0.03137 | Active anonymous numeric sensor/signal |
| `sensor_078` | 78 | 79 | Anonymous | 24 (1.5316%) | 995 | -0.3482 | 0.2492 | -0.01364 | 0.04787 | Active anonymous numeric sensor/signal |
| `sensor_079` | 79 | 80 | Anonymous | 24 (1.5316%) | 691 | -0.0568 | 0.1013 | 0.003458 | 0.02308 | Active anonymous numeric sensor/signal |
| `sensor_080` | 80 | 81 | Anonymous | 24 (1.5316%) | 922 | -0.1437 | 0.1186 | -0.01853 | 0.04923 | Active anonymous numeric sensor/signal |
| `sensor_081` | 81 | 82 | Anonymous | 24 (1.5316%) | 580 | -0.0982 | 0.0584 | -0.02115 | 0.01702 | Active anonymous numeric sensor/signal |
| `sensor_082` | 82 | 83 | Anonymous | 24 (1.5316%) | 888 | -0.2129 | 0.1437 | 0.006055 | 0.03607 | Active anonymous numeric sensor/signal |
| `sensor_083` | 83 | 84 | Anonymous | 1 (0.0638%) | 1506 | 5.826 | 8.99 | 7.452 | 0.5163 | Active anonymous numeric sensor/signal |
| `sensor_084` | 84 | 85 | Anonymous | 12 (0.7658%) | 180 | 0.1174 | 0.1505 | 0.1331 | 0.005051 | Active anonymous numeric sensor/signal |
| `sensor_085` | 85 | 86 | Anonymous | 1341 (85.5775%) | 97 | 0.1053 | 0.1184 | 0.1128 | 0.002928 | High missingness (>50% NaN) |
| `sensor_086` | 86 | 87 | Anonymous | 0 (0.0%) | 472 | 2.243 | 2.555 | 2.402 | 0.03733 | Active anonymous numeric sensor/signal |
| `sensor_087` | 87 | 88 | Anonymous | 0 (0.0%) | 249 | 0.7749 | 0.9935 | 0.9824 | 0.01285 | Active anonymous numeric sensor/signal |
| `sensor_088` | 88 | 89 | Anonymous | 0 (0.0%) | 973 | 1627 | 2105 | 1808 | 53.54 | Active anonymous numeric sensor/signal |
| `sensor_089` | 89 | 90 | Anonymous | 51 (3.2546%) | 650 | 0.1113 | 1.473 | 0.1887 | 0.05237 | Active anonymous numeric sensor/signal |
| `sensor_090` | 90 | 91 | Anonymous | 51 (3.2546%) | 1513 | 7397 | 1.075e+04 | 8828 | 396.3 | Active anonymous numeric sensor/signal |
| `sensor_091` | 91 | 92 | Anonymous | 6 (0.3829%) | 1191 | -0.357 | 0.3627 | 0.00244 | 0.08768 | Active anonymous numeric sensor/signal |
| `sensor_092` | 92 | 93 | Anonymous | 2 (0.1276%) | 180 | -0.0126 | 0.0281 | 0.000507 | 0.003231 | Active anonymous numeric sensor/signal |
| `sensor_093` | 93 | 94 | Anonymous | 2 (0.1276%) | 174 | -0.0171 | 0.0133 | -0.000541 | 0.00301 | Active anonymous numeric sensor/signal |
| `sensor_094` | 94 | 95 | Anonymous | 6 (0.3829%) | 22 | -0.002 | 0.0011 | -2.9e-05 | 0.000174 | Active anonymous numeric sensor/signal |
| `sensor_095` | 95 | 96 | Anonymous | 6 (0.3829%) | 14 | -0.0009 | 0.0009 | 6e-05 | 0.000104 | Active anonymous numeric sensor/signal |
| `sensor_096` | 96 | 97 | Anonymous | 6 (0.3829%) | 1333 | -1.48 | 2.509 | 0.01713 | 0.2196 | Active anonymous numeric sensor/signal |
| `sensor_097` | 97 | 98 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_098` | 98 | 99 | Anonymous | 6 (0.3829%) | 1420 | -5.272 | 2.57 | -0.01814 | 0.4271 | Active anonymous numeric sensor/signal |
| `sensor_099` | 99 | 100 | Anonymous | 6 (0.3829%) | 272 | -0.5283 | 0.8854 | 0.00154 | 0.06274 | Active anonymous numeric sensor/signal |
| `sensor_100` | 100 | 101 | Anonymous | 6 (0.3829%) | 35 | -0.003 | 0.0023 | -2.1e-05 | 0.000356 | Active anonymous numeric sensor/signal |
| `sensor_101` | 101 | 102 | Anonymous | 6 (0.3829%) | 29 | -0.0024 | 0.0017 | -7e-06 | 0.000221 | Active anonymous numeric sensor/signal |
| `sensor_102` | 102 | 103 | Anonymous | 6 (0.3829%) | 1066 | -0.5353 | 0.2979 | 0.001115 | 0.06297 | Active anonymous numeric sensor/signal |
| `sensor_103` | 103 | 104 | Anonymous | 2 (0.1276%) | 153 | -0.0329 | 0.0203 | -0.009789 | 0.003065 | Active anonymous numeric sensor/signal |
| `sensor_104` | 104 | 105 | Anonymous | 2 (0.1276%) | 55 | -0.0119 | 0.0071 | -1.5e-05 | 0.000851 | Active anonymous numeric sensor/signal |
| `sensor_105` | 105 | 106 | Anonymous | 6 (0.3829%) | 177 | -0.0281 | 0.0127 | -0.000498 | 0.003202 | Active anonymous numeric sensor/signal |
| `sensor_106` | 106 | 107 | Anonymous | 6 (0.3829%) | 180 | -0.0133 | 0.0172 | 0.00054 | 0.002988 | Active anonymous numeric sensor/signal |
| `sensor_107` | 107 | 108 | Anonymous | 6 (0.3829%) | 1159 | -0.5226 | 0.4856 | -0.001766 | 0.08747 | Active anonymous numeric sensor/signal |
| `sensor_108` | 108 | 109 | Anonymous | 6 (0.3829%) | 1183 | -0.3454 | 0.3938 | -0.01079 | 0.08676 | Active anonymous numeric sensor/signal |
| `sensor_109` | 109 | 110 | Anonymous | 1018 (64.9649%) | 96 | 0.7848 | 0.9842 | 0.98 | 0.008695 | High missingness (>50% NaN) |
| `sensor_110` | 110 | 111 | Anonymous | 1018 (64.9649%) | 546 | 88.19 | 106.9 | 101.3 | 1.88 | High missingness (>50% NaN) |
| `sensor_111` | 111 | 112 | Anonymous | 1018 (64.9649%) | 545 | 213 | 237 | 231.8 | 2.105 | High missingness (>50% NaN) |
| `sensor_112` | 112 | 113 | Anonymous | 715 (45.6286%) | 249 | 0 | 0.4885 | 0.4575 | 0.04894 | Active anonymous numeric sensor/signal |
| `sensor_113` | 113 | 114 | Anonymous | 0 (0.0%) | 468 | 0.8534 | 0.9763 | 0.9454 | 0.01213 | Active anonymous numeric sensor/signal |
| `sensor_114` | 114 | 115 | Anonymous | 0 (0.0%) | 20 | 0 | 0.0414 | 0.000123 | 0.001668 | Active anonymous numeric sensor/signal |
| `sensor_115` | 115 | 116 | Anonymous | 0 (0.0%) | 1567 | 544 | 924.5 | 747.4 | 48.95 | Active anonymous numeric sensor/signal |
| `sensor_116` | 116 | 117 | Anonymous | 0 (0.0%) | 136 | 0.89 | 0.9924 | 0.9871 | 0.009497 | Active anonymous numeric sensor/signal |
| `sensor_117` | 117 | 118 | Anonymous | 0 (0.0%) | 1527 | 52.81 | 311.7 | 58.63 | 6.485 | Active anonymous numeric sensor/signal |
| `sensor_118` | 118 | 119 | Anonymous | 24 (1.5316%) | 328 | 0.5274 | 0.6245 | 0.5984 | 0.008102 | Active anonymous numeric sensor/signal |
| `sensor_119` | 119 | 120 | Anonymous | 0 (0.0%) | 249 | 0.8411 | 0.9827 | 0.9708 | 0.008949 | Active anonymous numeric sensor/signal |
| `sensor_120` | 120 | 121 | Anonymous | 0 (0.0%) | 1269 | 5.126 | 7.522 | 6.311 | 0.1243 | Active anonymous numeric sensor/signal |
| `sensor_121` | 121 | 122 | Anonymous | 9 (0.5743%) | 54 | 15.46 | 16.07 | 15.8 | 0.09962 | Active anonymous numeric sensor/signal |
| `sensor_122` | 122 | 123 | Anonymous | 9 (0.5743%) | 309 | 1.671 | 6.889 | 3.898 | 0.9041 | Active anonymous numeric sensor/signal |
| `sensor_123` | 123 | 124 | Anonymous | 9 (0.5743%) | 50 | 15.17 | 16.1 | 15.83 | 0.1083 | Active anonymous numeric sensor/signal |
| `sensor_124` | 124 | 125 | Anonymous | 9 (0.5743%) | 59 | 15.43 | 16.1 | 15.79 | 0.1141 | Active anonymous numeric sensor/signal |
| `sensor_125` | 125 | 126 | Anonymous | 9 (0.5743%) | 155 | 0.3122 | 2.465 | 1.185 | 0.2806 | Active anonymous numeric sensor/signal |
| `sensor_126` | 126 | 127 | Anonymous | 9 (0.5743%) | 273 | 2.34 | 3.991 | 2.751 | 0.2535 | Active anonymous numeric sensor/signal |
| `sensor_127` | 127 | 128 | Anonymous | 9 (0.5743%) | 324 | 0.3161 | 1.175 | 0.6485 | 0.1354 | Active anonymous numeric sensor/signal |
| `sensor_128` | 128 | 129 | Anonymous | 9 (0.5743%) | 268 | 0 | 3.895 | 3.192 | 0.2642 | Active anonymous numeric sensor/signal |
| `sensor_129` | 129 | 130 | Anonymous | 9 (0.5743%) | 93 | -3.779 | 2.458 | -0.5542 | 1.22 | Active anonymous numeric sensor/signal |
| `sensor_130` | 130 | 131 | Anonymous | 9 (0.5743%) | 310 | 0.4199 | 0.8884 | 0.745 | 0.08253 | Active anonymous numeric sensor/signal |
| `sensor_131` | 131 | 132 | Anonymous | 9 (0.5743%) | 68 | 0.9936 | 1.019 | 0.9978 | 0.002251 | Active anonymous numeric sensor/signal |
| `sensor_132` | 132 | 133 | Anonymous | 8 (0.5105%) | 306 | 2.191 | 2.472 | 2.319 | 0.05318 | Active anonymous numeric sensor/signal |
| `sensor_133` | 133 | 134 | Anonymous | 8 (0.5105%) | 336 | 980.5 | 1021 | 1004 | 6.538 | Active anonymous numeric sensor/signal |
| `sensor_134` | 134 | 135 | Anonymous | 8 (0.5105%) | 335 | 33.37 | 64.13 | 39.39 | 2.99 | Active anonymous numeric sensor/signal |
| `sensor_135` | 135 | 136 | Anonymous | 5 (0.3191%) | 134 | 58 | 994 | 118 | 57.54 | Active anonymous numeric sensor/signal |
| `sensor_136` | 136 | 137 | Anonymous | 6 (0.3829%) | 1089 | 36.1 | 295.8 | 138.2 | 53.91 | Active anonymous numeric sensor/signal |
| `sensor_137` | 137 | 138 | Anonymous | 7 (0.4467%) | 1059 | 19.2 | 334.7 | 122.7 | 52.25 | Active anonymous numeric sensor/signal |
| `sensor_138` | 138 | 139 | Anonymous | 14 (0.8934%) | 348 | 19.8 | 141.8 | 57.6 | 12.35 | Active anonymous numeric sensor/signal |
| `sensor_139` | 139 | 140 | Anonymous | 14 (0.8934%) | 518 | 0 | 1771 | 416.8 | 263.3 | Active anonymous numeric sensor/signal |
| `sensor_140` | 140 | 141 | Anonymous | 14 (0.8934%) | 498 | 0.0319 | 9999 | 26.08 | 506.9 | Active anonymous numeric sensor/signal |
| `sensor_141` | 141 | 142 | Anonymous | 14 (0.8934%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_142` | 142 | 143 | Anonymous | 14 (0.8934%) | 374 | 1.74 | 103.4 | 6.642 | 3.552 | Active anonymous numeric sensor/signal |
| `sensor_143` | 143 | 144 | Anonymous | 9 (0.5743%) | 63 | 0 | 0.0121 | 0.004169 | 0.001282 | Active anonymous numeric sensor/signal |
| `sensor_144` | 144 | 145 | Anonymous | 2 (0.1276%) | 961 | 0.0324 | 0.6253 | 0.12 | 0.06134 | Active anonymous numeric sensor/signal |
| `sensor_145` | 145 | 146 | Anonymous | 2 (0.1276%) | 656 | 0.0214 | 0.2507 | 0.06362 | 0.02654 | Active anonymous numeric sensor/signal |
| `sensor_146` | 146 | 147 | Anonymous | 2 (0.1276%) | 579 | 0.0227 | 0.2479 | 0.05501 | 0.02184 | Active anonymous numeric sensor/signal |
| `sensor_147` | 147 | 148 | Anonymous | 2 (0.1276%) | 294 | 0.0043 | 0.9783 | 0.01741 | 0.02712 | Active anonymous numeric sensor/signal |
| `sensor_148` | 148 | 149 | Anonymous | 2 (0.1276%) | 1551 | 1.421 | 742.9 | 8.471 | 18.74 | Active anonymous numeric sensor/signal |
| `sensor_149` | 149 | 150 | Anonymous | 3 (0.1914%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_150` | 150 | 151 | Anonymous | 3 (0.1914%) | 1443 | 1.337 | 22.32 | 6.814 | 3.242 | Active anonymous numeric sensor/signal |
| `sensor_151` | 151 | 152 | Anonymous | 3 (0.1914%) | 1498 | 2.02 | 536.6 | 14.05 | 31 | Active anonymous numeric sensor/signal |
| `sensor_152` | 152 | 153 | Anonymous | 3 (0.1914%) | 1394 | 0.1544 | 924.4 | 1.197 | 23.36 | Active anonymous numeric sensor/signal |
| `sensor_153` | 153 | 154 | Anonymous | 3 (0.1914%) | 219 | 0.0036 | 0.2389 | 0.01193 | 0.009346 | Active anonymous numeric sensor/signal |
| `sensor_154` | 154 | 155 | Anonymous | 3 (0.1914%) | 1551 | 1.244 | 191.5 | 7.698 | 5.239 | Active anonymous numeric sensor/signal |
| `sensor_155` | 155 | 156 | Anonymous | 10 (0.6382%) | 65 | 0.14 | 12.71 | 0.5072 | 1.122 | Active anonymous numeric sensor/signal |
| `sensor_156` | 156 | 157 | Anonymous | 0 (0.0%) | 722 | 0.0111 | 2.202 | 0.05809 | 0.07917 | Active anonymous numeric sensor/signal |
| `sensor_157` | 157 | 158 | Anonymous | 1429 (91.1934%) | 128 | 0.0118 | 0.2876 | 0.0471 | 0.03954 | High missingness (>50% NaN) |
| `sensor_158` | 158 | 159 | Anonymous | 1429 (91.1934%) | 138 | 234.1 | 2505 | 1040 | 406.8 | High missingness (>50% NaN) |
| `sensor_159` | 159 | 160 | Anonymous | 2 (0.1276%) | 954 | 0 | 7791 | 882.7 | 983 | Active anonymous numeric sensor/signal |
| `sensor_160` | 160 | 161 | Anonymous | 2 (0.1276%) | 744 | 0 | 4170 | 555.3 | 574.8 | Active anonymous numeric sensor/signal |
| `sensor_161` | 161 | 162 | Anonymous | 2 (0.1276%) | 1411 | 0 | 3.794e+04 | 4067 | 4239 | Active anonymous numeric sensor/signal |
| `sensor_162` | 162 | 163 | Anonymous | 2 (0.1276%) | 1325 | 0 | 3.687e+04 | 4797 | 6554 | Active anonymous numeric sensor/signal |
| `sensor_163` | 163 | 164 | Anonymous | 2 (0.1276%) | 260 | 0 | 0.957 | 0.1402 | 0.122 | Active anonymous numeric sensor/signal |
| `sensor_164` | 164 | 165 | Anonymous | 2 (0.1276%) | 219 | 0 | 1.817 | 0.1279 | 0.2425 | Active anonymous numeric sensor/signal |
| `sensor_165` | 165 | 166 | Anonymous | 2 (0.1276%) | 404 | 0 | 3.286 | 0.252 | 0.4073 | Active anonymous numeric sensor/signal |
| `sensor_166` | 166 | 167 | Anonymous | 2 (0.1276%) | 62 | 0.8 | 21.1 | 2.789 | 1.12 | Active anonymous numeric sensor/signal |
| `sensor_167` | 167 | 168 | Anonymous | 2 (0.1276%) | 31 | 0.3 | 16.3 | 1.236 | 0.6328 | Active anonymous numeric sensor/signal |
| `sensor_168` | 168 | 169 | Anonymous | 2 (0.1276%) | 207 | 0.033 | 0.725 | 0.1244 | 0.04764 | Active anonymous numeric sensor/signal |
| `sensor_169` | 169 | 170 | Anonymous | 2 (0.1276%) | 652 | 0.046 | 1.143 | 0.4005 | 0.1979 | Active anonymous numeric sensor/signal |
| `sensor_170` | 170 | 171 | Anonymous | 1 (0.0638%) | 331 | 0.2979 | 1.153 | 0.6843 | 0.1575 | Active anonymous numeric sensor/signal |
| `sensor_171` | 171 | 172 | Anonymous | 1 (0.0638%) | 306 | 0.0089 | 0.494 | 0.1201 | 0.06078 | Active anonymous numeric sensor/signal |
| `sensor_172` | 172 | 173 | Anonymous | 1 (0.0638%) | 307 | 0.1287 | 0.5484 | 0.3201 | 0.07124 | Active anonymous numeric sensor/signal |
| `sensor_173` | 173 | 174 | Anonymous | 1 (0.0638%) | 319 | 0.2538 | 0.8643 | 0.5762 | 0.09573 | Active anonymous numeric sensor/signal |
| `sensor_174` | 174 | 175 | Anonymous | 1 (0.0638%) | 308 | 0.1287 | 0.5484 | 0.3201 | 0.07125 | Active anonymous numeric sensor/signal |
| `sensor_175` | 175 | 176 | Anonymous | 1 (0.0638%) | 327 | 0.4616 | 1.172 | 0.778 | 0.1163 | Active anonymous numeric sensor/signal |
| `sensor_176` | 176 | 177 | Anonymous | 1 (0.0638%) | 319 | 0.0735 | 0.4411 | 0.2447 | 0.07492 | Active anonymous numeric sensor/signal |
| `sensor_177` | 177 | 178 | Anonymous | 1 (0.0638%) | 250 | 0.047 | 1.858 | 0.3948 | 0.2829 | Active anonymous numeric sensor/signal |
| `sensor_178` | 178 | 179 | Anonymous | 24 (1.5316%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_179` | 179 | 180 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_180` | 180 | 181 | Anonymous | 1 (0.0638%) | 890 | 9.4 | 48.67 | 19.01 | 3.312 | Active anonymous numeric sensor/signal |
| `sensor_181` | 181 | 182 | Anonymous | 1 (0.0638%) | 687 | 0.093 | 3.573 | 0.5468 | 0.2244 | Active anonymous numeric sensor/signal |
| `sensor_182` | 182 | 183 | Anonymous | 1 (0.0638%) | 905 | 3.17 | 55 | 10.78 | 4.164 | Active anonymous numeric sensor/signal |
| `sensor_183` | 183 | 184 | Anonymous | 1 (0.0638%) | 1508 | 5.014 | 72.95 | 26.66 | 6.836 | Active anonymous numeric sensor/signal |
| `sensor_184` | 184 | 185 | Anonymous | 1 (0.0638%) | 1054 | 0.0297 | 3.228 | 0.1448 | 0.1102 | Active anonymous numeric sensor/signal |
| `sensor_185` | 185 | 186 | Anonymous | 1 (0.0638%) | 739 | 1.94 | 267.9 | 7.366 | 7.189 | Active anonymous numeric sensor/signal |
| `sensor_186` | 186 | 187 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_187` | 187 | 188 | Anonymous | 1 (0.0638%) | 1015 | 6.22 | 307.9 | 17.94 | 8.61 | Active anonymous numeric sensor/signal |
| `sensor_188` | 188 | 189 | Anonymous | 1 (0.0638%) | 1550 | 6.613 | 191.8 | 43.21 | 21.71 | Active anonymous numeric sensor/signal |
| `sensor_189` | 189 | 190 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_190` | 190 | 191 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_191` | 191 | 192 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_192` | 192 | 193 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_193` | 193 | 194 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_194` | 194 | 195 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_195` | 195 | 196 | Anonymous | 4 (0.2553%) | 206 | 0.08 | 4.838 | 0.2871 | 0.3952 | Active anonymous numeric sensor/signal |
| `sensor_196` | 196 | 197 | Anonymous | 7 (0.4467%) | 867 | 1.75 | 396.1 | 8.688 | 15.72 | Active anonymous numeric sensor/signal |
| `sensor_197` | 197 | 198 | Anonymous | 6 (0.3829%) | 898 | 9.22 | 252.9 | 20.09 | 10.55 | Active anonymous numeric sensor/signal |
| `sensor_198` | 198 | 199 | Anonymous | 6 (0.3829%) | 773 | 0.09 | 10.02 | 0.5574 | 0.5377 | Active anonymous numeric sensor/signal |
| `sensor_199` | 199 | 200 | Anonymous | 6 (0.3829%) | 920 | 2.77 | 390.1 | 11.53 | 16.45 | Active anonymous numeric sensor/signal |
| `sensor_200` | 200 | 201 | Anonymous | 7 (0.4467%) | 1008 | 3.21 | 199.6 | 17.6 | 8.691 | Active anonymous numeric sensor/signal |
| `sensor_201` | 201 | 202 | Anonymous | 7 (0.4467%) | 861 | 0 | 126.5 | 7.839 | 5.104 | Active anonymous numeric sensor/signal |
| `sensor_202` | 202 | 203 | Anonymous | 7 (0.4467%) | 1470 | 0 | 490.6 | 10.17 | 14.62 | Active anonymous numeric sensor/signal |
| `sensor_203` | 203 | 204 | Anonymous | 6 (0.3829%) | 1501 | 7.728 | 500.3 | 30.07 | 17.46 | Active anonymous numeric sensor/signal |
| `sensor_204` | 204 | 205 | Anonymous | 6 (0.3829%) | 1210 | 0.0429 | 9998 | 32.22 | 565.1 | Active anonymous numeric sensor/signal |
| `sensor_205` | 205 | 206 | Anonymous | 6 (0.3829%) | 841 | 2.3 | 320.1 | 9.05 | 11.54 | Active anonymous numeric sensor/signal |
| `sensor_206` | 206 | 207 | Anonymous | 6 (0.3829%) | 2 | 0 | 2 | 0.001281 | 0.05062 | Active anonymous numeric sensor/signal |
| `sensor_207` | 207 | 208 | Anonymous | 6 (0.3829%) | 1046 | 4.01 | 457.6 | 20.38 | 17.5 | Active anonymous numeric sensor/signal |
| `sensor_208` | 208 | 209 | Anonymous | 6 (0.3829%) | 1549 | 5.359 | 172.3 | 73.26 | 28.07 | Active anonymous numeric sensor/signal |
| `sensor_209` | 209 | 210 | Anonymous | 6 (0.3829%) | 2 | 0 | 46.15 | 0.02956 | 1.168 | Active anonymous numeric sensor/signal |
| `sensor_210` | 210 | 211 | Anonymous | 24 (1.5316%) | 798 | 0.0319 | 0.5164 | 0.08887 | 0.04206 | Active anonymous numeric sensor/signal |
| `sensor_211` | 211 | 212 | Anonymous | 24 (1.5316%) | 653 | 0.0022 | 0.3227 | 0.05675 | 0.025 | Active anonymous numeric sensor/signal |
| `sensor_212` | 212 | 213 | Anonymous | 24 (1.5316%) | 681 | 0.0071 | 0.5941 | 0.05143 | 0.03158 | Active anonymous numeric sensor/signal |
| `sensor_213` | 213 | 214 | Anonymous | 24 (1.5316%) | 810 | 0.0037 | 1.284 | 0.06035 | 0.05303 | Active anonymous numeric sensor/signal |
| `sensor_214` | 214 | 215 | Anonymous | 24 (1.5316%) | 803 | 0.0193 | 0.7615 | 0.08327 | 0.05646 | Active anonymous numeric sensor/signal |
| `sensor_215` | 215 | 216 | Anonymous | 24 (1.5316%) | 823 | 0.0059 | 0.3429 | 0.08108 | 0.03044 | Active anonymous numeric sensor/signal |
| `sensor_216` | 216 | 217 | Anonymous | 24 (1.5316%) | 728 | 0.0097 | 0.2828 | 0.08348 | 0.02576 | Active anonymous numeric sensor/signal |
| `sensor_217` | 217 | 218 | Anonymous | 24 (1.5316%) | 836 | 0.0079 | 0.6744 | 0.07164 | 0.04628 | Active anonymous numeric sensor/signal |
| `sensor_218` | 218 | 219 | Anonymous | 1 (0.0638%) | 1539 | 1.034 | 8.802 | 3.771 | 1.17 | Active anonymous numeric sensor/signal |
| `sensor_219` | 219 | 220 | Anonymous | 12 (0.7658%) | 64 | 0.0007 | 0.0163 | 0.003254 | 0.001646 | Active anonymous numeric sensor/signal |
| `sensor_220` | 220 | 221 | Anonymous | 1341 (85.5775%) | 69 | 0.0057 | 0.024 | 0.009213 | 0.001989 | High missingness (>50% NaN) |
| `sensor_221` | 221 | 222 | Anonymous | 0 (0.0%) | 408 | 0.02 | 0.2305 | 0.06072 | 0.0233 | Active anonymous numeric sensor/signal |
| `sensor_222` | 222 | 223 | Anonymous | 0 (0.0%) | 178 | 0.0003 | 0.9911 | 0.008821 | 0.05594 | Active anonymous numeric sensor/signal |
| `sensor_223` | 223 | 224 | Anonymous | 0 (0.0%) | 973 | 32.26 | 1769 | 122.8 | 55.16 | Active anonymous numeric sensor/signal |
| `sensor_224` | 224 | 225 | Anonymous | 51 (3.2546%) | 720 | 0.0093 | 1.436 | 0.05937 | 0.07121 | Active anonymous numeric sensor/signal |
| `sensor_225` | 225 | 226 | Anonymous | 51 (3.2546%) | 1472 | 168.8 | 3601 | 1041 | 433.2 | Active anonymous numeric sensor/signal |
| `sensor_226` | 226 | 227 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_227` | 227 | 228 | Anonymous | 2 (0.1276%) | 329 | 0.0062 | 0.1541 | 0.01912 | 0.01076 | Active anonymous numeric sensor/signal |
| `sensor_228` | 228 | 229 | Anonymous | 2 (0.1276%) | 292 | 0.0072 | 0.2133 | 0.01784 | 0.01074 | Active anonymous numeric sensor/signal |
| `sensor_229` | 229 | 230 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_230` | 230 | 231 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_231` | 231 | 232 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_232` | 232 | 233 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_233` | 233 | 234 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_234` | 234 | 235 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_235` | 235 | 236 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_236` | 236 | 237 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_237` | 237 | 238 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_238` | 238 | 239 | Anonymous | 2 (0.1276%) | 93 | 0.0013 | 0.0244 | 0.004791 | 0.001698 | Active anonymous numeric sensor/signal |
| `sensor_239` | 239 | 240 | Anonymous | 2 (0.1276%) | 80 | 0.0014 | 0.0236 | 0.004575 | 0.001441 | Active anonymous numeric sensor/signal |
| `sensor_240` | 240 | 241 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_241` | 241 | 242 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_242` | 242 | 243 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_243` | 243 | 244 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_244` | 244 | 245 | Anonymous | 1018 (64.9649%) | 66 | 0.0003 | 1.984 | 0.005755 | 0.08462 | High missingness (>50% NaN) |
| `sensor_245` | 245 | 246 | Anonymous | 1018 (64.9649%) | 539 | 0.2914 | 99.9 | 1.73 | 4.336 | High missingness (>50% NaN) |
| `sensor_246` | 246 | 247 | Anonymous | 1018 (64.9649%) | 547 | 1.102 | 237.2 | 4.149 | 10.05 | High missingness (>50% NaN) |
| `sensor_247` | 247 | 248 | Anonymous | 715 (45.6286%) | 490 | 0 | 0.4914 | 0.05337 | 0.06688 | Active anonymous numeric sensor/signal |
| `sensor_248` | 248 | 249 | Anonymous | 0 (0.0%) | 426 | 0.003 | 0.9732 | 0.02517 | 0.04924 | Active anonymous numeric sensor/signal |
| `sensor_249` | 249 | 250 | Anonymous | 0 (0.0%) | 23 | 0 | 0.4138 | 0.001065 | 0.01577 | Active anonymous numeric sensor/signal |
| `sensor_250` | 250 | 251 | Anonymous | 0 (0.0%) | 1566 | 21.01 | 1120 | 109.7 | 54.6 | Active anonymous numeric sensor/signal |
| `sensor_251` | 251 | 252 | Anonymous | 0 (0.0%) | 143 | 0.0003 | 0.9909 | 0.004285 | 0.03747 | Active anonymous numeric sensor/signal |
| `sensor_252` | 252 | 253 | Anonymous | 0 (0.0%) | 1533 | 0.7673 | 2550 | 4.645 | 64.35 | Active anonymous numeric sensor/signal |
| `sensor_253` | 253 | 254 | Anonymous | 24 (1.5316%) | 442 | 0.0094 | 0.4517 | 0.03322 | 0.02243 | Active anonymous numeric sensor/signal |
| `sensor_254` | 254 | 255 | Anonymous | 0 (0.0%) | 291 | 0.0017 | 0.0787 | 0.01394 | 0.009132 | Active anonymous numeric sensor/signal |
| `sensor_255` | 255 | 256 | Anonymous | 0 (0.0%) | 1317 | 0.1269 | 0.9255 | 0.4038 | 0.1203 | Active anonymous numeric sensor/signal |
| `sensor_256` | 256 | 257 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_257` | 257 | 258 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_258` | 258 | 259 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_259` | 259 | 260 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_260` | 260 | 261 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_261` | 261 | 262 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_262` | 262 | 263 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_263` | 263 | 264 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_264` | 264 | 265 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_265` | 265 | 266 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_266` | 266 | 267 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_267` | 267 | 268 | Anonymous | 8 (0.5105%) | 291 | 0.0198 | 0.1578 | 0.07059 | 0.02965 | Active anonymous numeric sensor/signal |
| `sensor_268` | 268 | 269 | Anonymous | 8 (0.5105%) | 333 | 6.098 | 40.85 | 19.5 | 7.344 | Active anonymous numeric sensor/signal |
| `sensor_269` | 269 | 270 | Anonymous | 8 (0.5105%) | 330 | 1.302 | 10.15 | 3.778 | 1.152 | Active anonymous numeric sensor/signal |
| `sensor_270` | 270 | 271 | Anonymous | 5 (0.3191%) | 599 | 15.55 | 158.5 | 29.26 | 8.402 | Active anonymous numeric sensor/signal |
| `sensor_271` | 271 | 272 | Anonymous | 6 (0.3829%) | 1559 | 10.4 | 132.6 | 46.06 | 17.87 | Active anonymous numeric sensor/signal |
| `sensor_272` | 272 | 273 | Anonymous | 7 (0.4467%) | 1557 | 6.943 | 122.1 | 41.3 | 17.74 | Active anonymous numeric sensor/signal |
| `sensor_273` | 273 | 274 | Anonymous | 14 (0.8934%) | 518 | 8.651 | 43.57 | 20.18 | 3.83 | Active anonymous numeric sensor/signal |
| `sensor_274` | 274 | 275 | Anonymous | 14 (0.8934%) | 518 | 0 | 659.2 | 136.3 | 85.61 | Active anonymous numeric sensor/signal |
| `sensor_275` | 275 | 276 | Anonymous | 14 (0.8934%) | 458 | 0.0111 | 3333 | 8.693 | 168.9 | Active anonymous numeric sensor/signal |
| `sensor_276` | 276 | 277 | Anonymous | 14 (0.8934%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_277` | 277 | 278 | Anonymous | 14 (0.8934%) | 512 | 0.5615 | 32.17 | 2.211 | 1.196 | Active anonymous numeric sensor/signal |
| `sensor_278` | 278 | 279 | Anonymous | 9 (0.5743%) | 22 | 0 | 0.0034 | 0.001117 | 0.00034 | Active anonymous numeric sensor/signal |
| `sensor_279` | 279 | 280 | Anonymous | 2 (0.1276%) | 541 | 0.0107 | 0.1884 | 0.04106 | 0.02029 | Active anonymous numeric sensor/signal |
| `sensor_280` | 280 | 281 | Anonymous | 2 (0.1276%) | 246 | 0.0073 | 0.0755 | 0.01803 | 0.006483 | Active anonymous numeric sensor/signal |
| `sensor_281` | 281 | 282 | Anonymous | 2 (0.1276%) | 227 | 0.0069 | 0.0597 | 0.01509 | 0.005545 | Active anonymous numeric sensor/signal |
| `sensor_282` | 282 | 283 | Anonymous | 2 (0.1276%) | 114 | 0.0016 | 0.3083 | 0.00577 | 0.00855 | Active anonymous numeric sensor/signal |
| `sensor_283` | 283 | 284 | Anonymous | 2 (0.1276%) | 1515 | 0.505 | 232.8 | 2.804 | 5.864 | Active anonymous numeric sensor/signal |
| `sensor_284` | 284 | 285 | Anonymous | 3 (0.1914%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_285` | 285 | 286 | Anonymous | 3 (0.1914%) | 1527 | 0.4611 | 6.87 | 2.12 | 0.9629 | Active anonymous numeric sensor/signal |
| `sensor_286` | 286 | 287 | Anonymous | 3 (0.1914%) | 1540 | 0.728 | 207 | 4.26 | 9.764 | Active anonymous numeric sensor/signal |
| `sensor_287` | 287 | 288 | Anonymous | 3 (0.1914%) | 1076 | 0.0513 | 292.2 | 0.3675 | 7.386 | Active anonymous numeric sensor/signal |
| `sensor_288` | 288 | 289 | Anonymous | 3 (0.1914%) | 87 | 0.0012 | 0.0749 | 0.003924 | 0.002936 | Active anonymous numeric sensor/signal |
| `sensor_289` | 289 | 290 | Anonymous | 3 (0.1914%) | 1522 | 0.396 | 59.52 | 2.579 | 1.617 | Active anonymous numeric sensor/signal |
| `sensor_290` | 290 | 291 | Anonymous | 10 (0.6382%) | 324 | 0.0416 | 4.42 | 0.1234 | 0.271 | Active anonymous numeric sensor/signal |
| `sensor_291` | 291 | 292 | Anonymous | 0 (0.0%) | 354 | 0.0038 | 0.6915 | 0.01993 | 0.02555 | Active anonymous numeric sensor/signal |
| `sensor_292` | 292 | 293 | Anonymous | 1429 (91.1934%) | 92 | 0.0041 | 0.0831 | 0.01449 | 0.01149 | High missingness (>50% NaN) |
| `sensor_293` | 293 | 294 | Anonymous | 1429 (91.1934%) | 138 | 82.32 | 879.2 | 335.6 | 137.7 | High missingness (>50% NaN) |
| `sensor_294` | 294 | 295 | Anonymous | 2 (0.1276%) | 1562 | 0 | 3934 | 401.8 | 477.1 | Active anonymous numeric sensor/signal |
| `sensor_295` | 295 | 296 | Anonymous | 2 (0.1276%) | 1561 | 0 | 2006 | 253 | 283.5 | Active anonymous numeric sensor/signal |
| `sensor_296` | 296 | 297 | Anonymous | 2 (0.1276%) | 1565 | 0 | 1.556e+04 | 1879 | 1975 | Active anonymous numeric sensor/signal |
| `sensor_297` | 297 | 298 | Anonymous | 2 (0.1276%) | 1559 | 0 | 1.852e+04 | 2343 | 3227 | Active anonymous numeric sensor/signal |
| `sensor_298` | 298 | 299 | Anonymous | 2 (0.1276%) | 725 | 0 | 0.5264 | 0.0638 | 0.06423 | Active anonymous numeric sensor/signal |
| `sensor_299` | 299 | 300 | Anonymous | 2 (0.1276%) | 626 | 0 | 1.031 | 0.06027 | 0.1308 | Active anonymous numeric sensor/signal |
| `sensor_300` | 300 | 301 | Anonymous | 2 (0.1276%) | 967 | 0 | 1.812 | 0.1184 | 0.2191 | Active anonymous numeric sensor/signal |
| `sensor_301` | 301 | 302 | Anonymous | 2 (0.1276%) | 1134 | 0.31 | 5.711 | 0.9101 | 0.332 | Active anonymous numeric sensor/signal |
| `sensor_302` | 302 | 303 | Anonymous | 2 (0.1276%) | 569 | 0.1118 | 5.155 | 0.4033 | 0.1975 | Active anonymous numeric sensor/signal |
| `sensor_303` | 303 | 304 | Anonymous | 2 (0.1276%) | 509 | 0.0108 | 0.2258 | 0.04034 | 0.01451 | Active anonymous numeric sensor/signal |
| `sensor_304` | 304 | 305 | Anonymous | 2 (0.1276%) | 1105 | 0.0138 | 0.3337 | 0.1321 | 0.06487 | Active anonymous numeric sensor/signal |
| `sensor_305` | 305 | 306 | Anonymous | 1 (0.0638%) | 314 | 0.1171 | 0.475 | 0.2649 | 0.05739 | Active anonymous numeric sensor/signal |
| `sensor_306` | 306 | 307 | Anonymous | 1 (0.0638%) | 262 | 0.0034 | 0.2246 | 0.04862 | 0.0254 | Active anonymous numeric sensor/signal |
| `sensor_307` | 307 | 308 | Anonymous | 1 (0.0638%) | 286 | 0.0549 | 0.2112 | 0.1289 | 0.02747 | Active anonymous numeric sensor/signal |
| `sensor_308` | 308 | 309 | Anonymous | 1 (0.0638%) | 293 | 0.0913 | 0.3239 | 0.2184 | 0.03359 | Active anonymous numeric sensor/signal |
| `sensor_309` | 309 | 310 | Anonymous | 1 (0.0638%) | 290 | 0.0549 | 0.2112 | 0.1289 | 0.02747 | Active anonymous numeric sensor/signal |
| `sensor_310` | 310 | 311 | Anonymous | 1 (0.0638%) | 310 | 0.1809 | 0.4438 | 0.3048 | 0.04346 | Active anonymous numeric sensor/signal |
| `sensor_311` | 311 | 312 | Anonymous | 1 (0.0638%) | 276 | 0.0328 | 0.1784 | 0.09734 | 0.0288 | Active anonymous numeric sensor/signal |
| `sensor_312` | 312 | 313 | Anonymous | 1 (0.0638%) | 307 | 0.0224 | 0.7549 | 0.1601 | 0.1173 | Active anonymous numeric sensor/signal |
| `sensor_313` | 313 | 314 | Anonymous | 24 (1.5316%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_314` | 314 | 315 | Anonymous | 24 (1.5316%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_315` | 315 | 316 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_316` | 316 | 317 | Anonymous | 1 (0.0638%) | 1533 | 2.788 | 13.1 | 5.977 | 1.019 | Active anonymous numeric sensor/signal |
| `sensor_317` | 317 | 318 | Anonymous | 1 (0.0638%) | 1160 | 0.0283 | 1.003 | 0.1726 | 0.07239 | Active anonymous numeric sensor/signal |
| `sensor_318` | 318 | 319 | Anonymous | 1 (0.0638%) | 1535 | 0.9848 | 15.89 | 3.189 | 1.216 | Active anonymous numeric sensor/signal |
| `sensor_319` | 319 | 320 | Anonymous | 1 (0.0638%) | 1550 | 1.657 | 20.05 | 7.916 | 2.179 | Active anonymous numeric sensor/signal |
| `sensor_320` | 320 | 321 | Anonymous | 1 (0.0638%) | 550 | 0.0084 | 0.9474 | 0.0431 | 0.03188 | Active anonymous numeric sensor/signal |
| `sensor_321` | 321 | 322 | Anonymous | 1 (0.0638%) | 1511 | 0.6114 | 79.15 | 2.264 | 2.117 | Active anonymous numeric sensor/signal |
| `sensor_322` | 322 | 323 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_323` | 323 | 324 | Anonymous | 1 (0.0638%) | 1536 | 1.71 | 89.19 | 5.393 | 2.519 | Active anonymous numeric sensor/signal |
| `sensor_324` | 324 | 325 | Anonymous | 1 (0.0638%) | 1560 | 2.235 | 51.87 | 13.33 | 6.616 | Active anonymous numeric sensor/signal |
| `sensor_325` | 325 | 326 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_326` | 326 | 327 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_327` | 327 | 328 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_328` | 328 | 329 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_329` | 329 | 330 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_330` | 330 | 331 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_331` | 331 | 332 | Anonymous | 4 (0.2553%) | 313 | 0.0224 | 1.096 | 0.08323 | 0.06342 | Active anonymous numeric sensor/signal |
| `sensor_332` | 332 | 333 | Anonymous | 7 (0.4467%) | 1517 | 0.5373 | 174.9 | 2.593 | 5.645 | Active anonymous numeric sensor/signal |
| `sensor_333` | 333 | 334 | Anonymous | 6 (0.3829%) | 1527 | 2.837 | 90.52 | 6.216 | 3.403 | Active anonymous numeric sensor/signal |
| `sensor_334` | 334 | 335 | Anonymous | 6 (0.3829%) | 1145 | 0.0282 | 3.413 | 0.1684 | 0.1729 | Active anonymous numeric sensor/signal |
| `sensor_335` | 335 | 336 | Anonymous | 6 (0.3829%) | 1526 | 0.7899 | 172.7 | 3.427 | 5.782 | Active anonymous numeric sensor/signal |
| `sensor_336` | 336 | 337 | Anonymous | 7 (0.4467%) | 1532 | 5.215 | 214.9 | 9.736 | 7.556 | Active anonymous numeric sensor/signal |
| `sensor_337` | 337 | 338 | Anonymous | 7 (0.4467%) | 1517 | 0 | 38.9 | 2.327 | 1.699 | Active anonymous numeric sensor/signal |
| `sensor_338` | 338 | 339 | Anonymous | 7 (0.4467%) | 1520 | 0 | 196.7 | 3.038 | 5.645 | Active anonymous numeric sensor/signal |
| `sensor_339` | 339 | 340 | Anonymous | 6 (0.3829%) | 1543 | 2.2 | 197.5 | 9.329 | 6.075 | Active anonymous numeric sensor/signal |
| `sensor_340` | 340 | 341 | Anonymous | 6 (0.3829%) | 761 | 0.0131 | 5044 | 14.67 | 261.7 | Active anonymous numeric sensor/signal |
| `sensor_341` | 341 | 342 | Anonymous | 6 (0.3829%) | 1517 | 0.5741 | 97.71 | 2.732 | 3.668 | Active anonymous numeric sensor/signal |
| `sensor_342` | 342 | 343 | Anonymous | 6 (0.3829%) | 2 | 0 | 0.4472 | 0.000286 | 0.01132 | Active anonymous numeric sensor/signal |
| `sensor_343` | 343 | 344 | Anonymous | 6 (0.3829%) | 1541 | 1.256 | 156.3 | 6.199 | 5.372 | Active anonymous numeric sensor/signal |
| `sensor_344` | 344 | 345 | Anonymous | 6 (0.3829%) | 1551 | 2.056 | 59.32 | 23.22 | 8.895 | Active anonymous numeric sensor/signal |
| `sensor_345` | 345 | 346 | Anonymous | 794 (50.6701%) | 767 | 1.769 | 257 | 7.958 | 17.51 | High missingness (>50% NaN) |
| `sensor_346` | 346 | 347 | Anonymous | 794 (50.6701%) | 762 | 1.018 | 187.8 | 5.77 | 17.08 | High missingness (>50% NaN) |
| `sensor_347` | 347 | 348 | Anonymous | 6 (0.3829%) | 2 | 0 | 13.91 | 0.008914 | 0.3522 | Active anonymous numeric sensor/signal |
| `sensor_348` | 348 | 349 | Anonymous | 24 (1.5316%) | 357 | 0.0103 | 0.22 | 0.02471 | 0.01186 | Active anonymous numeric sensor/signal |
| `sensor_349` | 349 | 350 | Anonymous | 24 (1.5316%) | 373 | 0.001 | 0.1339 | 0.02525 | 0.0106 | Active anonymous numeric sensor/signal |
| `sensor_350` | 350 | 351 | Anonymous | 24 (1.5316%) | 435 | 0.0029 | 0.2914 | 0.0232 | 0.01433 | Active anonymous numeric sensor/signal |
| `sensor_351` | 351 | 352 | Anonymous | 24 (1.5316%) | 499 | 0.002 | 0.6188 | 0.02758 | 0.02456 | Active anonymous numeric sensor/signal |
| `sensor_352` | 352 | 353 | Anonymous | 24 (1.5316%) | 354 | 0.0056 | 0.1429 | 0.02336 | 0.01316 | Active anonymous numeric sensor/signal |
| `sensor_353` | 353 | 354 | Anonymous | 24 (1.5316%) | 563 | 0.0026 | 0.1535 | 0.04033 | 0.0155 | Active anonymous numeric sensor/signal |
| `sensor_354` | 354 | 355 | Anonymous | 24 (1.5316%) | 486 | 0.004 | 0.1344 | 0.04192 | 0.01307 | Active anonymous numeric sensor/signal |
| `sensor_355` | 355 | 356 | Anonymous | 24 (1.5316%) | 572 | 0.0038 | 0.2789 | 0.03454 | 0.02231 | Active anonymous numeric sensor/signal |
| `sensor_356` | 356 | 357 | Anonymous | 1 (0.0638%) | 1473 | 0.3796 | 2.835 | 1.299 | 0.3869 | Active anonymous numeric sensor/signal |
| `sensor_357` | 357 | 358 | Anonymous | 12 (0.7658%) | 28 | 0.0003 | 0.0052 | 0.000999 | 0.000501 | Active anonymous numeric sensor/signal |
| `sensor_358` | 358 | 359 | Anonymous | 1341 (85.5775%) | 20 | 0.0017 | 0.0047 | 0.002443 | 0.000395 | High missingness (>50% NaN) |
| `sensor_359` | 359 | 360 | Anonymous | 0 (0.0%) | 215 | 0.0076 | 0.0888 | 0.01984 | 0.007136 | Active anonymous numeric sensor/signal |
| `sensor_360` | 360 | 361 | Anonymous | 0 (0.0%) | 97 | 0.0001 | 0.409 | 0.002945 | 0.02 | Active anonymous numeric sensor/signal |
| `sensor_361` | 361 | 362 | Anonymous | 0 (0.0%) | 972 | 10.72 | 547.2 | 39.94 | 17.06 | Active anonymous numeric sensor/signal |
| `sensor_362` | 362 | 363 | Anonymous | 51 (3.2546%) | 389 | 0.0028 | 0.4163 | 0.01838 | 0.02164 | Active anonymous numeric sensor/signal |
| `sensor_363` | 363 | 364 | Anonymous | 51 (3.2546%) | 1516 | 60.99 | 1072 | 333.3 | 138.8 | Active anonymous numeric sensor/signal |
| `sensor_364` | 364 | 365 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_365` | 365 | 366 | Anonymous | 2 (0.1276%) | 120 | 0.0017 | 0.0368 | 0.005199 | 0.002656 | Active anonymous numeric sensor/signal |
| `sensor_366` | 366 | 367 | Anonymous | 2 (0.1276%) | 107 | 0.002 | 0.0392 | 0.004814 | 0.002382 | Active anonymous numeric sensor/signal |
| `sensor_367` | 367 | 368 | Anonymous | 6 (0.3829%) | 113 | 0 | 0.0357 | 0.003773 | 0.002699 | Active anonymous numeric sensor/signal |
| `sensor_368` | 368 | 369 | Anonymous | 6 (0.3829%) | 97 | 0 | 0.0334 | 0.003172 | 0.002107 | Active anonymous numeric sensor/signal |
| `sensor_369` | 369 | 370 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_370` | 370 | 371 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_371` | 371 | 372 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_372` | 372 | 373 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_373` | 373 | 374 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_374` | 374 | 375 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_375` | 375 | 376 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_376` | 376 | 377 | Anonymous | 2 (0.1276%) | 36 | 0.0004 | 0.0082 | 0.001601 | 0.000534 | Active anonymous numeric sensor/signal |
| `sensor_377` | 377 | 378 | Anonymous | 2 (0.1276%) | 31 | 0.0004 | 0.0077 | 0.001571 | 0.000467 | Active anonymous numeric sensor/signal |
| `sensor_378` | 378 | 379 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_379` | 379 | 380 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_380` | 380 | 381 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_381` | 381 | 382 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_382` | 382 | 383 | Anonymous | 1018 (64.9649%) | 29 | 0.0001 | 0.6271 | 0.001826 | 0.02674 | High missingness (>50% NaN) |
| `sensor_383` | 383 | 384 | Anonymous | 1018 (64.9649%) | 525 | 0.0875 | 31 | 0.541 | 1.341 | High missingness (>50% NaN) |
| `sensor_384` | 384 | 385 | Anonymous | 1018 (64.9649%) | 536 | 0.3383 | 74.84 | 1.285 | 3.168 | High missingness (>50% NaN) |
| `sensor_385` | 385 | 386 | Anonymous | 715 (45.6286%) | 232 | 0 | 0.2073 | 0.01143 | 0.01437 | Active anonymous numeric sensor/signal |
| `sensor_386` | 386 | 387 | Anonymous | 0 (0.0%) | 191 | 0.0008 | 0.3068 | 0.008281 | 0.01549 | Active anonymous numeric sensor/signal |
| `sensor_387` | 387 | 388 | Anonymous | 0 (0.0%) | 22 | 0 | 0.1309 | 0.000339 | 0.004989 | Active anonymous numeric sensor/signal |
| `sensor_388` | 388 | 389 | Anonymous | 0 (0.0%) | 1564 | 6.31 | 348.8 | 35.16 | 17.23 | Active anonymous numeric sensor/signal |
| `sensor_389` | 389 | 390 | Anonymous | 0 (0.0%) | 92 | 0.0001 | 0.3127 | 0.001338 | 0.01182 | Active anonymous numeric sensor/signal |
| `sensor_390` | 390 | 391 | Anonymous | 0 (0.0%) | 1458 | 0.3046 | 805.4 | 1.432 | 20.33 | Active anonymous numeric sensor/signal |
| `sensor_391` | 391 | 392 | Anonymous | 24 (1.5316%) | 183 | 0.0031 | 0.1375 | 0.01096 | 0.006738 | Active anonymous numeric sensor/signal |
| `sensor_392` | 392 | 393 | Anonymous | 0 (0.0%) | 109 | 0.0005 | 0.0229 | 0.004533 | 0.002956 | Active anonymous numeric sensor/signal |
| `sensor_393` | 393 | 394 | Anonymous | 0 (0.0%) | 953 | 0.0342 | 0.2994 | 0.134 | 0.03841 | Active anonymous numeric sensor/signal |
| `sensor_394` | 394 | 395 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_395` | 395 | 396 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_396` | 396 | 397 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_397` | 397 | 398 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_398` | 398 | 399 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_399` | 399 | 400 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_400` | 400 | 401 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_401` | 401 | 402 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_402` | 402 | 403 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_403` | 403 | 404 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_404` | 404 | 405 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_405` | 405 | 406 | Anonymous | 8 (0.5105%) | 228 | 0.0062 | 0.0514 | 0.02421 | 0.01073 | Active anonymous numeric sensor/signal |
| `sensor_406` | 406 | 407 | Anonymous | 8 (0.5105%) | 335 | 2.054 | 14.73 | 6.731 | 2.83 | Active anonymous numeric sensor/signal |
| `sensor_407` | 407 | 408 | Anonymous | 8 (0.5105%) | 331 | 0.424 | 3.313 | 1.232 | 0.3647 | Active anonymous numeric sensor/signal |
| `sensor_408` | 408 | 409 | Anonymous | 5 (0.3191%) | 593 | 2.738 | 44.31 | 5.341 | 2.578 | Active anonymous numeric sensor/signal |
| `sensor_409` | 409 | 410 | Anonymous | 6 (0.3829%) | 1548 | 1.216 | 9.576 | 4.58 | 1.777 | Active anonymous numeric sensor/signal |
| `sensor_410` | 410 | 411 | Anonymous | 7 (0.4467%) | 1545 | 0.7342 | 13.81 | 4.929 | 2.123 | Active anonymous numeric sensor/signal |
| `sensor_411` | 411 | 412 | Anonymous | 14 (0.8934%) | 509 | 0.9609 | 6.215 | 2.616 | 0.5515 | Active anonymous numeric sensor/signal |
| `sensor_412` | 412 | 413 | Anonymous | 14 (0.8934%) | 518 | 0 | 128.3 | 30.91 | 18.41 | Active anonymous numeric sensor/signal |
| `sensor_413` | 413 | 414 | Anonymous | 14 (0.8934%) | 518 | 4.042 | 899.1 | 25.61 | 47.31 | Active anonymous numeric sensor/signal |
| `sensor_414` | 414 | 415 | Anonymous | 14 (0.8934%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_415` | 415 | 416 | Anonymous | 14 (0.8934%) | 513 | 1.534 | 116.9 | 6.631 | 3.958 | Active anonymous numeric sensor/signal |
| `sensor_416` | 416 | 417 | Anonymous | 9 (0.5743%) | 510 | 0 | 9.69 | 3.404 | 1.035 | Active anonymous numeric sensor/signal |
| `sensor_417` | 417 | 418 | Anonymous | 2 (0.1276%) | 1551 | 2.153 | 39.04 | 8.191 | 4.055 | Active anonymous numeric sensor/signal |
| `sensor_418` | 418 | 419 | Anonymous | 2 (0.1276%) | 1051 | 0 | 999.3 | 320.3 | 287.7 | Active anonymous numeric sensor/signal |
| `sensor_419` | 419 | 420 | Anonymous | 2 (0.1276%) | 851 | 0 | 998.7 | 309.1 | 325.4 | Active anonymous numeric sensor/signal |
| `sensor_420` | 420 | 421 | Anonymous | 2 (0.1276%) | 1514 | 0.4411 | 111.5 | 1.821 | 3.058 | Active anonymous numeric sensor/signal |
| `sensor_421` | 421 | 422 | Anonymous | 2 (0.1276%) | 1534 | 0.7217 | 273.1 | 4.175 | 6.914 | Active anonymous numeric sensor/signal |
| `sensor_422` | 422 | 423 | Anonymous | 3 (0.1914%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_423` | 423 | 424 | Anonymous | 3 (0.1914%) | 1563 | 23.02 | 424.2 | 77.66 | 32.6 | Active anonymous numeric sensor/signal |
| `sensor_424` | 424 | 425 | Anonymous | 3 (0.1914%) | 1529 | 0.4866 | 103.2 | 3.315 | 6.325 | Active anonymous numeric sensor/signal |
| `sensor_425` | 425 | 426 | Anonymous | 3 (0.1914%) | 1540 | 1.467 | 898.6 | 6.796 | 23.26 | Active anonymous numeric sensor/signal |
| `sensor_426` | 426 | 427 | Anonymous | 3 (0.1914%) | 1481 | 0.3632 | 24.99 | 1.234 | 0.9956 | Active anonymous numeric sensor/signal |
| `sensor_427` | 427 | 428 | Anonymous | 3 (0.1914%) | 1538 | 0.6637 | 113.2 | 4.059 | 3.042 | Active anonymous numeric sensor/signal |
| `sensor_428` | 428 | 429 | Anonymous | 10 (0.6382%) | 404 | 1.12 | 118.8 | 4.221 | 10.63 | Active anonymous numeric sensor/signal |
| `sensor_429` | 429 | 430 | Anonymous | 0 (0.0%) | 1542 | 0.7837 | 186.6 | 4.172 | 6.435 | Active anonymous numeric sensor/signal |
| `sensor_430` | 430 | 431 | Anonymous | 2 (0.1276%) | 1551 | 0 | 400 | 18.42 | 36.06 | Active anonymous numeric sensor/signal |
| `sensor_431` | 431 | 432 | Anonymous | 2 (0.1276%) | 1553 | 0 | 400 | 22.36 | 36.4 | Active anonymous numeric sensor/signal |
| `sensor_432` | 432 | 433 | Anonymous | 2 (0.1276%) | 1503 | 0 | 994.3 | 99.37 | 126.2 | Active anonymous numeric sensor/signal |
| `sensor_433` | 433 | 434 | Anonymous | 2 (0.1276%) | 1371 | 0 | 995.7 | 205.5 | 225.8 | Active anonymous numeric sensor/signal |
| `sensor_434` | 434 | 435 | Anonymous | 2 (0.1276%) | 1537 | 0 | 400 | 14.73 | 34.11 | Active anonymous numeric sensor/signal |
| `sensor_435` | 435 | 436 | Anonymous | 2 (0.1276%) | 1524 | 0 | 400 | 9.371 | 34.37 | Active anonymous numeric sensor/signal |
| `sensor_436` | 436 | 437 | Anonymous | 2 (0.1276%) | 1539 | 0 | 400 | 7.513 | 34.56 | Active anonymous numeric sensor/signal |
| `sensor_437` | 437 | 438 | Anonymous | 2 (0.1276%) | 1495 | 1.157 | 32.27 | 4.017 | 1.611 | Active anonymous numeric sensor/signal |
| `sensor_438` | 438 | 439 | Anonymous | 2 (0.1276%) | 967 | 0 | 851.6 | 54.7 | 34.11 | Active anonymous numeric sensor/signal |
| `sensor_439` | 439 | 440 | Anonymous | 2 (0.1276%) | 1550 | 14.12 | 657.8 | 70.64 | 38.38 | Active anonymous numeric sensor/signal |
| `sensor_440` | 440 | 441 | Anonymous | 2 (0.1276%) | 1557 | 1.097 | 33.06 | 11.53 | 6.169 | Active anonymous numeric sensor/signal |
| `sensor_441` | 441 | 442 | Anonymous | 1 (0.0638%) | 325 | 0.3512 | 1.277 | 0.8021 | 0.1842 | Active anonymous numeric sensor/signal |
| `sensor_442` | 442 | 443 | Anonymous | 1 (0.0638%) | 335 | 0.0974 | 5.132 | 1.345 | 0.6592 | Active anonymous numeric sensor/signal |
| `sensor_443` | 443 | 444 | Anonymous | 1 (0.0638%) | 330 | 0.2169 | 1.085 | 0.6339 | 0.1436 | Active anonymous numeric sensor/signal |
| `sensor_444` | 444 | 445 | Anonymous | 1 (0.0638%) | 325 | 0.3336 | 1.351 | 0.895 | 0.1555 | Active anonymous numeric sensor/signal |
| `sensor_445` | 445 | 446 | Anonymous | 1 (0.0638%) | 329 | 0.3086 | 1.109 | 0.6471 | 0.1413 | Active anonymous numeric sensor/signal |
| `sensor_446` | 446 | 447 | Anonymous | 1 (0.0638%) | 338 | 0.6968 | 1.764 | 1.175 | 0.1762 | Active anonymous numeric sensor/signal |
| `sensor_447` | 447 | 448 | Anonymous | 1 (0.0638%) | 317 | 0.0846 | 0.5085 | 0.2819 | 0.08646 | Active anonymous numeric sensor/signal |
| `sensor_448` | 448 | 449 | Anonymous | 1 (0.0638%) | 326 | 0.0399 | 1.475 | 0.3323 | 0.2363 | Active anonymous numeric sensor/signal |
| `sensor_449` | 449 | 450 | Anonymous | 24 (1.5316%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_450` | 450 | 451 | Anonymous | 24 (1.5316%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_451` | 451 | 452 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_452` | 452 | 453 | Anonymous | 1 (0.0638%) | 1518 | 2.671 | 13.98 | 5.347 | 0.9192 | Active anonymous numeric sensor/signal |
| `sensor_453` | 453 | 454 | Anonymous | 1 (0.0638%) | 1550 | 0.9037 | 34.49 | 5.461 | 2.251 | Active anonymous numeric sensor/signal |
| `sensor_454` | 454 | 455 | Anonymous | 1 (0.0638%) | 1555 | 2.329 | 42.07 | 7.884 | 3.06 | Active anonymous numeric sensor/signal |
| `sensor_455` | 455 | 456 | Anonymous | 1 (0.0638%) | 1527 | 0.6948 | 10.18 | 3.637 | 0.9384 | Active anonymous numeric sensor/signal |
| `sensor_456` | 456 | 457 | Anonymous | 1 (0.0638%) | 1551 | 3.049 | 232.1 | 12.33 | 8.126 | Active anonymous numeric sensor/signal |
| `sensor_457` | 457 | 458 | Anonymous | 1 (0.0638%) | 1547 | 1.443 | 164.1 | 5.264 | 4.538 | Active anonymous numeric sensor/signal |
| `sensor_458` | 458 | 459 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_459` | 459 | 460 | Anonymous | 1 (0.0638%) | 1518 | 0.991 | 47.78 | 2.838 | 1.346 | Active anonymous numeric sensor/signal |
| `sensor_460` | 460 | 461 | Anonymous | 1 (0.0638%) | 1564 | 7.953 | 149.4 | 29.2 | 13.34 | Active anonymous numeric sensor/signal |
| `sensor_461` | 461 | 462 | Anonymous | 1 (0.0638%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_462` | 462 | 463 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_463` | 463 | 464 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_464` | 464 | 465 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_465` | 465 | 466 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_466` | 466 | 467 | Anonymous | 4 (0.2553%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_467` | 467 | 468 | Anonymous | 4 (0.2553%) | 417 | 1.716 | 109 | 6.252 | 8.674 | Active anonymous numeric sensor/signal |
| `sensor_468` | 468 | 469 | Anonymous | 7 (0.4467%) | 1317 | 0 | 999.9 | 224.2 | 230.8 | Active anonymous numeric sensor/signal |
| `sensor_469` | 469 | 470 | Anonymous | 6 (0.3829%) | 1514 | 2.601 | 77.8 | 5.662 | 3.152 | Active anonymous numeric sensor/signal |
| `sensor_470` | 470 | 471 | Anonymous | 6 (0.3829%) | 1547 | 0.8325 | 87.13 | 5.368 | 4.983 | Active anonymous numeric sensor/signal |
| `sensor_471` | 471 | 472 | Anonymous | 6 (0.3829%) | 1552 | 2.403 | 212.7 | 9.639 | 10.17 | Active anonymous numeric sensor/signal |
| `sensor_472` | 472 | 473 | Anonymous | 7 (0.4467%) | 1560 | 11.5 | 492.8 | 137.9 | 47.7 | Active anonymous numeric sensor/signal |
| `sensor_473` | 473 | 474 | Anonymous | 7 (0.4467%) | 1558 | 0 | 359 | 39.43 | 22.46 | Active anonymous numeric sensor/signal |
| `sensor_474` | 474 | 475 | Anonymous | 7 (0.4467%) | 1559 | 0 | 415.4 | 37.64 | 24.82 | Active anonymous numeric sensor/signal |
| `sensor_475` | 475 | 476 | Anonymous | 6 (0.3829%) | 1526 | 1.101 | 79.12 | 4.263 | 2.611 | Active anonymous numeric sensor/signal |
| `sensor_476` | 476 | 477 | Anonymous | 6 (0.3829%) | 1559 | 0 | 274.9 | 20.13 | 14.94 | Active anonymous numeric sensor/signal |
| `sensor_477` | 477 | 478 | Anonymous | 6 (0.3829%) | 1537 | 1.687 | 289.8 | 6.258 | 10.19 | Active anonymous numeric sensor/signal |
| `sensor_478` | 478 | 479 | Anonymous | 6 (0.3829%) | 2 | 0 | 200 | 0.1281 | 5.062 | Active anonymous numeric sensor/signal |
| `sensor_479` | 479 | 480 | Anonymous | 6 (0.3829%) | 1507 | 0.6459 | 63.33 | 3.283 | 2.639 | Active anonymous numeric sensor/signal |
| `sensor_480` | 480 | 481 | Anonymous | 6 (0.3829%) | 1560 | 8.841 | 222 | 75.54 | 35.75 | Active anonymous numeric sensor/signal |
| `sensor_481` | 481 | 482 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_482` | 482 | 483 | Anonymous | 24 (1.5316%) | 1062 | 0 | 999.4 | 318.4 | 281 | Active anonymous numeric sensor/signal |
| `sensor_483` | 483 | 484 | Anonymous | 24 (1.5316%) | 1402 | 0 | 989.5 | 206.6 | 192.9 | Active anonymous numeric sensor/signal |
| `sensor_484` | 484 | 485 | Anonymous | 24 (1.5316%) | 1324 | 0 | 996.9 | 215.3 | 213.1 | Active anonymous numeric sensor/signal |
| `sensor_485` | 485 | 486 | Anonymous | 24 (1.5316%) | 1358 | 0 | 994 | 201.1 | 218.7 | Active anonymous numeric sensor/signal |
| `sensor_486` | 486 | 487 | Anonymous | 24 (1.5316%) | 1039 | 0 | 999.5 | 302.5 | 287.4 | Active anonymous numeric sensor/signal |
| `sensor_487` | 487 | 488 | Anonymous | 24 (1.5316%) | 1199 | 0 | 995.7 | 239.5 | 263.8 | Active anonymous numeric sensor/signal |
| `sensor_488` | 488 | 489 | Anonymous | 24 (1.5316%) | 1314 | 0 | 997.5 | 352.6 | 252 | Active anonymous numeric sensor/signal |
| `sensor_489` | 489 | 490 | Anonymous | 24 (1.5316%) | 1344 | 0 | 994 | 272.2 | 228 | Active anonymous numeric sensor/signal |
| `sensor_490` | 490 | 491 | Anonymous | 1 (0.0638%) | 1562 | 13.72 | 142.8 | 51.35 | 18.05 | Active anonymous numeric sensor/signal |
| `sensor_491` | 491 | 492 | Anonymous | 12 (0.7658%) | 472 | 0.5558 | 12.77 | 2.443 | 1.224 | Active anonymous numeric sensor/signal |
| `sensor_492` | 492 | 493 | Anonymous | 1341 (85.5775%) | 226 | 4.888 | 21.04 | 8.171 | 1.759 | High missingness (>50% NaN) |
| `sensor_493` | 493 | 494 | Anonymous | 0 (0.0%) | 572 | 0.833 | 9.402 | 2.53 | 0.9739 | Active anonymous numeric sensor/signal |
| `sensor_494` | 494 | 495 | Anonymous | 0 (0.0%) | 894 | 0.0342 | 127.6 | 0.9564 | 6.615 | Active anonymous numeric sensor/signal |
| `sensor_495` | 495 | 496 | Anonymous | 0 (0.0%) | 964 | 1.772 | 107.7 | 6.808 | 3.26 | Active anonymous numeric sensor/signal |
| `sensor_496` | 496 | 497 | Anonymous | 51 (3.2546%) | 1510 | 4.814 | 219.6 | 29.87 | 24.62 | Active anonymous numeric sensor/signal |
| `sensor_497` | 497 | 498 | Anonymous | 51 (3.2546%) | 1509 | 1.95 | 40.28 | 11.82 | 4.957 | Active anonymous numeric sensor/signal |
| `sensor_498` | 498 | 499 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_499` | 499 | 500 | Anonymous | 2 (0.1276%) | 703 | 0 | 1000 | 263.2 | 324.8 | Active anonymous numeric sensor/signal |
| `sensor_500` | 500 | 501 | Anonymous | 2 (0.1276%) | 648 | 0 | 999.2 | 241 | 323 | Active anonymous numeric sensor/signal |
| `sensor_501` | 501 | 502 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_502` | 502 | 503 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_503` | 503 | 504 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_504` | 504 | 505 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_505` | 505 | 506 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_506` | 506 | 507 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_507` | 507 | 508 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_508` | 508 | 509 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_509` | 509 | 510 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_510` | 510 | 511 | Anonymous | 2 (0.1276%) | 1498 | 0 | 451.5 | 55.76 | 37.69 | Active anonymous numeric sensor/signal |
| `sensor_511` | 511 | 512 | Anonymous | 2 (0.1276%) | 586 | 0 | 1000 | 276 | 329.7 | Active anonymous numeric sensor/signal |
| `sensor_512` | 512 | 513 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_513` | 513 | 514 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_514` | 514 | 515 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_515` | 515 | 516 | Anonymous | 6 (0.3829%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_516` | 516 | 517 | Anonymous | 1018 (64.9649%) | 498 | 0.0287 | 252.9 | 0.6789 | 10.78 | High missingness (>50% NaN) |
| `sensor_517` | 517 | 518 | Anonymous | 1018 (64.9649%) | 543 | 0.288 | 113.3 | 1.739 | 4.891 | High missingness (>50% NaN) |
| `sensor_518` | 518 | 519 | Anonymous | 1018 (64.9649%) | 542 | 0.4674 | 111.3 | 1.806 | 4.716 | High missingness (>50% NaN) |
| `sensor_519` | 519 | 520 | Anonymous | 715 (45.6286%) | 836 | 0 | 184.3 | 11.73 | 15.81 | Active anonymous numeric sensor/signal |
| `sensor_520` | 520 | 521 | Anonymous | 0 (0.0%) | 1536 | 0.3121 | 111.7 | 2.696 | 5.702 | Active anonymous numeric sensor/signal |
| `sensor_521` | 521 | 522 | Anonymous | 0 (0.0%) | 9 | 0 | 1000 | 11.61 | 103.1 | Active anonymous numeric sensor/signal |
| `sensor_522` | 522 | 523 | Anonymous | 0 (0.0%) | 1562 | 2.681 | 138 | 14.73 | 7.104 | Active anonymous numeric sensor/signal |
| `sensor_523` | 523 | 524 | Anonymous | 0 (0.0%) | 1040 | 0.0258 | 111.3 | 0.4539 | 4.148 | Active anonymous numeric sensor/signal |
| `sensor_524` | 524 | 525 | Anonymous | 0 (0.0%) | 1543 | 1.31 | 818 | 5.688 | 20.66 | Active anonymous numeric sensor/signal |
| `sensor_525` | 525 | 526 | Anonymous | 24 (1.5316%) | 1526 | 1.54 | 80.04 | 5.56 | 3.92 | Active anonymous numeric sensor/signal |
| `sensor_526` | 526 | 527 | Anonymous | 0 (0.0%) | 1514 | 0.1705 | 8.204 | 1.443 | 0.9584 | Active anonymous numeric sensor/signal |
| `sensor_527` | 527 | 528 | Anonymous | 0 (0.0%) | 1549 | 2.17 | 14.45 | 6.396 | 1.889 | Active anonymous numeric sensor/signal |
| `sensor_528` | 528 | 529 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_529` | 529 | 530 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_530` | 530 | 531 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_531` | 531 | 532 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_532` | 532 | 533 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_533` | 533 | 534 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_534` | 534 | 535 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_535` | 535 | 536 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_536` | 536 | 537 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_537` | 537 | 538 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_538` | 538 | 539 | Anonymous | 9 (0.5743%) | 1 | 0 | 0 | 0 | 0 | Constant signal (zero variance; candidate for removal inside CV) |
| `sensor_539` | 539 | 540 | Anonymous | 8 (0.5105%) | 333 | 0.8516 | 6.58 | 3.034 | 1.253 | Active anonymous numeric sensor/signal |
| `sensor_540` | 540 | 541 | Anonymous | 8 (0.5105%) | 336 | 0.6144 | 4.082 | 1.943 | 0.7319 | Active anonymous numeric sensor/signal |
| `sensor_541` | 541 | 542 | Anonymous | 8 (0.5105%) | 336 | 3.276 | 25.78 | 9.612 | 2.896 | Active anonymous numeric sensor/signal |
| `sensor_542` | 542 | 543 | Anonymous | 2 (0.1276%) | 102 | 0.1053 | 0.1184 | 0.1112 | 0.002737 | Active anonymous numeric sensor/signal |
| `sensor_543` | 543 | 544 | Anonymous | 2 (0.1276%) | 71 | 0.0051 | 0.024 | 0.008471 | 0.001534 | Active anonymous numeric sensor/signal |
| `sensor_544` | 544 | 545 | Anonymous | 2 (0.1276%) | 21 | 0.0016 | 0.0047 | 0.002509 | 0.000296 | Active anonymous numeric sensor/signal |
| `sensor_545` | 545 | 546 | Anonymous | 2 (0.1276%) | 273 | 4.429 | 21.04 | 7.611 | 1.316 | Active anonymous numeric sensor/signal |
| `sensor_546` | 546 | 547 | Anonymous | 260 (16.5922%) | 1047 | 0.4444 | 3.979 | 1.04 | 0.3891 | Active anonymous numeric sensor/signal |
| `sensor_547` | 547 | 548 | Anonymous | 260 (16.5922%) | 1023 | 372.8 | 421.7 | 403.5 | 5.064 | Active anonymous numeric sensor/signal |
| `sensor_548` | 548 | 549 | Anonymous | 260 (16.5922%) | 964 | 71.04 | 83.72 | 75.68 | 3.391 | Active anonymous numeric sensor/signal |
| `sensor_549` | 549 | 550 | Anonymous | 260 (16.5922%) | 1048 | 0.0446 | 7.066 | 0.6633 | 0.6733 | Active anonymous numeric sensor/signal |
| `sensor_550` | 550 | 551 | Anonymous | 260 (16.5922%) | 747 | 6.11 | 131.7 | 17.01 | 4.967 | Active anonymous numeric sensor/signal |
| `sensor_551` | 551 | 552 | Anonymous | 260 (16.5922%) | 213 | 0.12 | 39.33 | 1.231 | 1.361 | Active anonymous numeric sensor/signal |
| `sensor_552` | 552 | 553 | Anonymous | 260 (16.5922%) | 973 | 0.0187 | 2.718 | 0.2767 | 0.2762 | Active anonymous numeric sensor/signal |
| `sensor_553` | 553 | 554 | Anonymous | 260 (16.5922%) | 1077 | 2.786 | 56.93 | 7.704 | 2.193 | Active anonymous numeric sensor/signal |
| `sensor_554` | 554 | 555 | Anonymous | 260 (16.5922%) | 1000 | 0.052 | 17.48 | 0.5037 | 0.5989 | Active anonymous numeric sensor/signal |
| `sensor_555` | 555 | 556 | Anonymous | 260 (16.5922%) | 1085 | 4.827 | 303.6 | 57.75 | 35.21 | Active anonymous numeric sensor/signal |
| `sensor_556` | 556 | 557 | Anonymous | 260 (16.5922%) | 1070 | 1.497 | 35.32 | 4.217 | 1.28 | Active anonymous numeric sensor/signal |
| `sensor_557` | 557 | 558 | Anonymous | 260 (16.5922%) | 1062 | 0.1646 | 54.29 | 1.623 | 1.87 | Active anonymous numeric sensor/signal |
| `sensor_558` | 558 | 559 | Anonymous | 1 (0.0638%) | 365 | 0.8919 | 1.512 | 0.995 | 0.08386 | Active anonymous numeric sensor/signal |
| `sensor_559` | 559 | 560 | Anonymous | 1 (0.0638%) | 399 | 0.0699 | 1.074 | 0.3257 | 0.2014 | Active anonymous numeric sensor/signal |
| `sensor_560` | 560 | 561 | Anonymous | 1 (0.0638%) | 345 | 0.0177 | 0.4457 | 0.07244 | 0.05158 | Active anonymous numeric sensor/signal |
| `sensor_561` | 561 | 562 | Anonymous | 1 (0.0638%) | 414 | 7.237 | 101.1 | 32.28 | 19.03 | Active anonymous numeric sensor/signal |
| `sensor_562` | 562 | 563 | Anonymous | 273 (17.4218%) | 873 | 242.3 | 311.4 | 262.7 | 7.631 | Active anonymous numeric sensor/signal |
| `sensor_563` | 563 | 564 | Anonymous | 273 (17.4218%) | 785 | 0.3049 | 1.299 | 0.6796 | 0.1218 | Active anonymous numeric sensor/signal |
| `sensor_564` | 564 | 565 | Anonymous | 273 (17.4218%) | 581 | 0.97 | 32.58 | 6.445 | 2.634 | Active anonymous numeric sensor/signal |
| `sensor_565` | 565 | 566 | Anonymous | 273 (17.4218%) | 753 | 0.0224 | 0.6892 | 0.1456 | 0.08112 | Active anonymous numeric sensor/signal |
| `sensor_566` | 566 | 567 | Anonymous | 273 (17.4218%) | 887 | 0.4122 | 14.01 | 2.611 | 1.033 | Active anonymous numeric sensor/signal |
| `sensor_567` | 567 | 568 | Anonymous | 273 (17.4218%) | 619 | 0.0091 | 0.2932 | 0.06009 | 0.03276 | Active anonymous numeric sensor/signal |
| `sensor_568` | 568 | 569 | Anonymous | 273 (17.4218%) | 887 | 0.3706 | 12.75 | 2.452 | 0.9966 | Active anonymous numeric sensor/signal |
| `sensor_569` | 569 | 570 | Anonymous | 273 (17.4218%) | 897 | 3.25 | 84.8 | 21.12 | 10.21 | Active anonymous numeric sensor/signal |
| `sensor_570` | 570 | 571 | Anonymous | 0 (0.0%) | 814 | 317.2 | 589.5 | 530.5 | 17.5 | Active anonymous numeric sensor/signal |
| `sensor_571` | 571 | 572 | Anonymous | 0 (0.0%) | 811 | 0.9802 | 2.74 | 2.102 | 0.2751 | Active anonymous numeric sensor/signal |
| `sensor_572` | 572 | 573 | Anonymous | 0 (0.0%) | 518 | 3.54 | 454.6 | 28.45 | 86.3 | Active anonymous numeric sensor/signal |
| `sensor_573` | 573 | 574 | Anonymous | 0 (0.0%) | 754 | 0.0667 | 2.197 | 0.3456 | 0.2485 | Active anonymous numeric sensor/signal |
| `sensor_574` | 574 | 575 | Anonymous | 0 (0.0%) | 830 | 1.04 | 170 | 9.162 | 26.92 | Active anonymous numeric sensor/signal |
| `sensor_575` | 575 | 576 | Anonymous | 0 (0.0%) | 599 | 0.023 | 0.5502 | 0.1047 | 0.06779 | Active anonymous numeric sensor/signal |
| `sensor_576` | 576 | 577 | Anonymous | 0 (0.0%) | 820 | 0.6636 | 90.42 | 5.564 | 16.92 | Active anonymous numeric sensor/signal |
| `sensor_577` | 577 | 578 | Anonymous | 0 (0.0%) | 851 | 4.582 | 96.96 | 16.64 | 12.49 | Active anonymous numeric sensor/signal |
| `sensor_578` | 578 | 579 | Anonymous | 949 (60.5616%) | 322 | -0.0169 | 0.1028 | 0.02161 | 0.01173 | High missingness (>50% NaN) |
| `sensor_579` | 579 | 580 | Anonymous | 949 (60.5616%) | 260 | 0.0032 | 0.0799 | 0.01683 | 0.00964 | High missingness (>50% NaN) |
| `sensor_580` | 580 | 581 | Anonymous | 949 (60.5616%) | 120 | 0.001 | 0.0286 | 0.005396 | 0.003116 | High missingness (>50% NaN) |
| `sensor_581` | 581 | 582 | Anonymous | 949 (60.5616%) | 611 | 0 | 737.3 | 97.93 | 87.52 | High missingness (>50% NaN) |
| `sensor_582` | 582 | 583 | Anonymous | 1 (0.0638%) | 171 | 0.4778 | 0.5098 | 0.5001 | 0.003404 | Active anonymous numeric sensor/signal |
| `sensor_583` | 583 | 584 | Anonymous | 1 (0.0638%) | 227 | 0.006 | 0.4766 | 0.01532 | 0.01718 | Active anonymous numeric sensor/signal |
| `sensor_584` | 584 | 585 | Anonymous | 1 (0.0638%) | 68 | 0.0017 | 0.1045 | 0.003847 | 0.00372 | Active anonymous numeric sensor/signal |
| `sensor_585` | 585 | 586 | Anonymous | 1 (0.0638%) | 1502 | 1.198 | 99.3 | 3.068 | 3.578 | Active anonymous numeric sensor/signal |
| `sensor_586` | 586 | 587 | Anonymous | 1 (0.0638%) | 322 | -0.0169 | 0.1028 | 0.02146 | 0.01236 | Active anonymous numeric sensor/signal |
| `sensor_587` | 587 | 588 | Anonymous | 1 (0.0638%) | 260 | 0.0032 | 0.0799 | 0.01648 | 0.008808 | Active anonymous numeric sensor/signal |
| `sensor_588` | 588 | 589 | Anonymous | 1 (0.0638%) | 120 | 0.001 | 0.0286 | 0.005283 | 0.002867 | Active anonymous numeric sensor/signal |
| `sensor_589` | 589 | 590 | Anonymous | 1 (0.0638%) | 611 | 0 | 737.3 | 99.67 | 93.89 | Active anonymous numeric sensor/signal |

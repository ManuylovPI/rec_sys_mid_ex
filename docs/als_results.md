> **Superseded** (stage 4, any-overlap targets). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Implicit ALS: validation results

Produced by `python -m src.als` on 2026-10-22 16:45, implicit 0.7.3, random_state 42. Matrix: 4841 users x 2973 shows (weeks 11-20), 856904 non-zeros; 2203 of 6376 pool shows have item factors. Already-watched shows are not filtered. Same harness and selection as repeat_v2.

| method | params | select | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2219 | 0.2255 | 0.2183 | 0.1551 | 0.1895 | 0.1861 | 0.1320 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2204 | 0.2238 | 0.2170 | 0.1550 | 0.1890 | 0.1856 | 0.1321 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2182 | 0.2215 | 0.2150 | 0.1549 | 0.1869 | 0.1839 | 0.1312 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2179 | 0.2215 | 0.2143 | 0.1555 | 0.1872 | 0.1841 | 0.1319 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1825 | 0.1865 | 0.1785 | 0.1351 | 0.1596 | 0.1558 | 0.1165 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1819 | 0.1852 | 0.1785 | 0.1348 | 0.1593 | 0.1558 | 0.1170 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.01, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1805 | 0.1836 | 0.1773 | 0.1322 | 0.1579 | 0.1535 | 0.1152 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.1, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1796 | 0.1833 | 0.1759 | 0.1324 | 0.1585 | 0.1540 | 0.1158 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1291 | 0.1313 | 0.1269 | 0.0857 | 0.1495 | 0.1471 | 0.0981 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1291 | 0.1316 | 0.1265 | 0.0980 | 0.1224 | 0.1187 | 0.0907 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1282 | 0.1306 | 0.1257 | 0.0973 | 0.1203 | 0.1172 | 0.0895 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1275 | 0.1298 | 0.1252 | 0.0835 | 0.1485 | 0.1464 | 0.0975 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.01, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1273 | 0.1298 | 0.1248 | 0.0960 | 0.1189 | 0.1157 | 0.0886 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.1, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1257 | 0.1282 | 0.1233 | 0.0944 | 0.1177 | 0.1149 | 0.0879 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.1254 | 0.1280 | 0.1227 | 0.0827 | 0.1466 | 0.1443 | 0.0951 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.1253 | 0.1278 | 0.1228 | 0.0824 | 0.1462 | 0.1436 | 0.0952 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0841 | 0.0857 | 0.0825 | 0.0574 | 0.1057 | 0.1042 | 0.0718 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0826 | 0.0839 | 0.0812 | 0.0560 | 0.1068 | 0.1050 | 0.0715 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.01, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0790 | 0.0801 | 0.0778 | 0.0545 | 0.1000 | 0.0984 | 0.0677 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.1, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0772 | 0.0785 | 0.0759 | 0.0535 | 0.0996 | 0.0980 | 0.0676 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0751 | 0.0758 | 0.0743 | 0.0429 | 0.0966 | 0.0962 | 0.0593 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0740 | 0.0748 | 0.0732 | 0.0414 | 0.0965 | 0.0961 | 0.0586 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0721 | 0.0736 | 0.0706 | 0.0396 | 0.0942 | 0.0936 | 0.0574 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0711 | 0.0721 | 0.0700 | 0.0396 | 0.0938 | 0.0940 | 0.0571 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.1, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0499 | 0.0507 | 0.0490 | 0.0281 | 0.0701 | 0.0697 | 0.0436 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0493 | 0.0498 | 0.0487 | 0.0355 | 0.0685 | 0.0671 | 0.0506 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0484 | 0.0489 | 0.0478 | 0.0353 | 0.0686 | 0.0674 | 0.0508 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.01, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0481 | 0.0489 | 0.0473 | 0.0268 | 0.0691 | 0.0689 | 0.0429 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.1, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0480 | 0.0485 | 0.0474 | 0.0268 | 0.0675 | 0.0671 | 0.0422 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.01, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0455 | 0.0462 | 0.0448 | 0.0252 | 0.0671 | 0.0666 | 0.0417 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.01, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0445 | 0.0449 | 0.0442 | 0.0318 | 0.0610 | 0.0601 | 0.0452 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.1, 'alpha': 1.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0445 | 0.0448 | 0.0443 | 0.0322 | 0.0616 | 0.0607 | 0.0455 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.1, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0376 | 0.0376 | 0.0376 | 0.0216 | 0.0543 | 0.0548 | 0.0351 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.01, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0347 | 0.0351 | 0.0344 | 0.0202 | 0.0519 | 0.0524 | 0.0335 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.1, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0339 | 0.0343 | 0.0334 | 0.0202 | 0.0521 | 0.0525 | 0.0335 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.01, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0335 | 0.0338 | 0.0333 | 0.0188 | 0.0511 | 0.0518 | 0.0328 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0320 | 0.0324 | 0.0316 | 0.0235 | 0.0317 | 0.0316 | 0.0235 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0318 | 0.0322 | 0.0314 | 0.0230 | 0.0319 | 0.0317 | 0.0238 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0318 | 0.0321 | 0.0315 | 0.0234 | 0.0327 | 0.0329 | 0.0244 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0309 | 0.0311 | 0.0308 | 0.0233 | 0.0323 | 0.0324 | 0.0241 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0226 | 0.0232 | 0.0220 | 0.0126 | 0.0367 | 0.0362 | 0.0230 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0226 | 0.0235 | 0.0217 | 0.0137 | 0.0372 | 0.0365 | 0.0238 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0216 | 0.0224 | 0.0208 | 0.0126 | 0.0367 | 0.0362 | 0.0232 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0214 | 0.0220 | 0.0208 | 0.0118 | 0.0361 | 0.0356 | 0.0226 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.01, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0152 | 0.0155 | 0.0148 | 0.0083 | 0.0257 | 0.0258 | 0.0167 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.01, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0149 | 0.0154 | 0.0145 | 0.0079 | 0.0247 | 0.0247 | 0.0158 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.1, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0149 | 0.0153 | 0.0144 | 0.0081 | 0.0264 | 0.0262 | 0.0172 |
| als | `{'weighting': 'raw', 'factors': 64, 'reg': 0.1, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0145 | 0.0150 | 0.0139 | 0.0079 | 0.0252 | 0.0250 | 0.0163 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.1, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0142 | 0.0146 | 0.0139 | 0.0084 | 0.0233 | 0.0238 | 0.0161 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.01, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0131 | 0.0134 | 0.0129 | 0.0075 | 0.0229 | 0.0234 | 0.0152 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.1, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0126 | 0.0127 | 0.0125 | 0.0086 | 0.0167 | 0.0171 | 0.0129 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.01, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0124 | 0.0124 | 0.0124 | 0.0078 | 0.0170 | 0.0174 | 0.0131 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.01, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0122 | 0.0121 | 0.0123 | 0.0078 | 0.0169 | 0.0175 | 0.0128 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.1, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0122 | 0.0124 | 0.0120 | 0.0075 | 0.0222 | 0.0225 | 0.0151 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.1, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0119 | 0.0120 | 0.0117 | 0.0079 | 0.0167 | 0.0172 | 0.0129 |
| als | `{'weighting': 'raw', 'factors': 128, 'reg': 0.01, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8'}` | 0.0119 | 0.0119 | 0.0118 | 0.0071 | 0.0221 | 0.0225 | 0.0150 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.1, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0113 | 0.0115 | 0.0111 | 0.0074 | 0.0179 | 0.0184 | 0.0134 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.01, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0112 | 0.0111 | 0.0112 | 0.0078 | 0.0173 | 0.0175 | 0.0134 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.01, 'alpha': 10.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0108 | 0.0109 | 0.0107 | 0.0070 | 0.0172 | 0.0176 | 0.0131 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.1, 'alpha': 10.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0107 | 0.0108 | 0.0107 | 0.0078 | 0.0176 | 0.0178 | 0.0136 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.01, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0064 | 0.0064 | 0.0063 | 0.0043 | 0.0093 | 0.0092 | 0.0073 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.01, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0060 | 0.0062 | 0.0058 | 0.0042 | 0.0092 | 0.0093 | 0.0071 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.1, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0053 | 0.0054 | 0.0052 | 0.0037 | 0.0086 | 0.0087 | 0.0068 |
| als | `{'weighting': 'bm25', 'factors': 128, 'reg': 0.1, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0049 | 0.0051 | 0.0046 | 0.0034 | 0.0085 | 0.0087 | 0.0067 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0048 | 0.0050 | 0.0045 | 0.0029 | 0.0060 | 0.0058 | 0.0044 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0047 | 0.0050 | 0.0045 | 0.0029 | 0.0060 | 0.0060 | 0.0043 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0042 | 0.0043 | 0.0040 | 0.0024 | 0.0061 | 0.0060 | 0.0048 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.01, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0040 | 0.0042 | 0.0038 | 0.0023 | 0.0058 | 0.0060 | 0.0046 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0040 | 0.0041 | 0.0038 | 0.0022 | 0.0065 | 0.0064 | 0.0050 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.1, 'alpha': 40.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0037 | 0.0039 | 0.0036 | 0.0022 | 0.0058 | 0.0059 | 0.0047 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.01, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0037 | 0.0040 | 0.0034 | 0.0019 | 0.0056 | 0.0056 | 0.0041 |
| als | `{'weighting': 'bm25', 'factors': 64, 'reg': 0.1, 'alpha': 40.0, 'iters': 30, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.0035 | 0.0037 | 0.0032 | 0.0019 | 0.0054 | 0.0055 | 0.0040 |

Selected: `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` (select 0.2219).

Total runtime: 91.4 s.

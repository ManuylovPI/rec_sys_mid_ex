> **Superseded** (stage 4, any-overlap targets). Kept as a record of how the work developed. The hidden leaderboard target turned out to be coverage-based, not any-overlap (docs/target_definition.md), and rows before the time-zone fix used shifted day counts (docs/errata.md). Current numbers: docs/results.md.

# Implicit ALS: validation results

Produced by `python -m src.als --extend` on 2026-10-22 16:47, implicit 0.7.3, random_state 42. Matrix: 4841 users x 2973 shows (weeks 11-20), 856904 non-zeros; 2203 of 6376 pool shows have item factors. Already-watched shows are not filtered. Same harness and selection as repeat_v2.

| method | params | select | test_users/n_days | test_users/n_airings | test_users/watch_sec | active_both/n_days | active_both/n_airings | active_both/watch_sec |
|---|---|---|---|---|---|---|---|---|
| als | `{'weighting': 'bm25', 'factors': 8, 'reg': 0.01, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2963 | 0.2998 | 0.2927 | 0.1832 | 0.2677 | 0.2675 | 0.1667 |
| als | `{'weighting': 'bm25', 'factors': 8, 'reg': 0.1, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2936 | 0.2965 | 0.2908 | 0.1824 | 0.2637 | 0.2639 | 0.1638 |
| als | `{'weighting': 'bm25', 'factors': 8, 'reg': 0.1, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2815 | 0.2839 | 0.2791 | 0.1785 | 0.2529 | 0.2521 | 0.1570 |
| als | `{'weighting': 'bm25', 'factors': 8, 'reg': 0.01, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2800 | 0.2823 | 0.2776 | 0.1774 | 0.2513 | 0.2506 | 0.1561 |
| als | `{'weighting': 'bm25', 'factors': 16, 'reg': 0.1, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2726 | 0.2735 | 0.2716 | 0.1814 | 0.2412 | 0.2413 | 0.1608 |
| als | `{'weighting': 'bm25', 'factors': 16, 'reg': 0.01, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2720 | 0.2729 | 0.2711 | 0.1810 | 0.2410 | 0.2414 | 0.1606 |
| als | `{'weighting': 'bm25', 'factors': 8, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2581 | 0.2618 | 0.2545 | 0.1627 | 0.2215 | 0.2189 | 0.1402 |
| als | `{'weighting': 'bm25', 'factors': 8, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2579 | 0.2615 | 0.2543 | 0.1625 | 0.2215 | 0.2190 | 0.1404 |
| als | `{'weighting': 'bm25', 'factors': 16, 'reg': 0.1, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2468 | 0.2464 | 0.2472 | 0.1716 | 0.2184 | 0.2213 | 0.1496 |
| als | `{'weighting': 'bm25', 'factors': 16, 'reg': 0.01, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2466 | 0.2461 | 0.2470 | 0.1716 | 0.2178 | 0.2204 | 0.1492 |
| als | `{'weighting': 'bm25', 'factors': 16, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2389 | 0.2419 | 0.2360 | 0.1616 | 0.2063 | 0.2045 | 0.1391 |
| als | `{'weighting': 'bm25', 'factors': 16, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2384 | 0.2414 | 0.2354 | 0.1617 | 0.2061 | 0.2046 | 0.1393 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2231 | 0.2253 | 0.2208 | 0.1582 | 0.2018 | 0.1996 | 0.1407 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2219 | 0.2255 | 0.2183 | 0.1551 | 0.1895 | 0.1861 | 0.1320 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2206 | 0.2224 | 0.2189 | 0.1570 | 0.2016 | 0.1993 | 0.1397 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.2204 | 0.2238 | 0.2170 | 0.1550 | 0.1890 | 0.1856 | 0.1321 |
| als | `{'weighting': 'raw', 'factors': 8, 'reg': 0.1, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.2150 | 0.2188 | 0.2113 | 0.1339 | 0.2175 | 0.2118 | 0.1321 |
| als | `{'weighting': 'raw', 'factors': 8, 'reg': 0.01, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.2149 | 0.2188 | 0.2110 | 0.1336 | 0.2173 | 0.2115 | 0.1318 |
| als | `{'weighting': 'raw', 'factors': 8, 'reg': 0.1, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.2119 | 0.2161 | 0.2076 | 0.1278 | 0.2121 | 0.2064 | 0.1272 |
| als | `{'weighting': 'raw', 'factors': 8, 'reg': 0.01, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.2118 | 0.2162 | 0.2073 | 0.1272 | 0.2119 | 0.2060 | 0.1267 |
| als | `{'weighting': 'raw', 'factors': 8, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.2078 | 0.2141 | 0.2016 | 0.1247 | 0.2102 | 0.2030 | 0.1233 |
| als | `{'weighting': 'raw', 'factors': 8, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.2065 | 0.2127 | 0.2003 | 0.1239 | 0.2096 | 0.2024 | 0.1232 |
| als | `{'weighting': 'raw', 'factors': 16, 'reg': 0.1, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1730 | 0.1755 | 0.1705 | 0.1117 | 0.1847 | 0.1813 | 0.1160 |
| als | `{'weighting': 'raw', 'factors': 16, 'reg': 0.01, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1722 | 0.1748 | 0.1697 | 0.1115 | 0.1843 | 0.1807 | 0.1159 |
| als | `{'weighting': 'raw', 'factors': 16, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1695 | 0.1718 | 0.1673 | 0.1081 | 0.1806 | 0.1781 | 0.1137 |
| als | `{'weighting': 'raw', 'factors': 16, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1693 | 0.1718 | 0.1668 | 0.1068 | 0.1811 | 0.1786 | 0.1139 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.1, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1625 | 0.1645 | 0.1606 | 0.1207 | 0.1584 | 0.1560 | 0.1130 |
| als | `{'weighting': 'bm25', 'factors': 32, 'reg': 0.01, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` | 0.1584 | 0.1601 | 0.1566 | 0.1174 | 0.1557 | 0.1535 | 0.1112 |
| als | `{'weighting': 'raw', 'factors': 16, 'reg': 0.1, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1502 | 0.1541 | 0.1462 | 0.1007 | 0.1689 | 0.1633 | 0.1059 |
| als | `{'weighting': 'raw', 'factors': 16, 'reg': 0.01, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1499 | 0.1537 | 0.1461 | 0.1001 | 0.1680 | 0.1634 | 0.1061 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1291 | 0.1313 | 0.1269 | 0.0857 | 0.1495 | 0.1471 | 0.0981 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 1.0, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1275 | 0.1298 | 0.1252 | 0.0835 | 0.1485 | 0.1464 | 0.0975 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1029 | 0.1042 | 0.1015 | 0.0704 | 0.1232 | 0.1203 | 0.0831 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.1010 | 0.1030 | 0.0990 | 0.0702 | 0.1220 | 0.1192 | 0.0827 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.1, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0851 | 0.0876 | 0.0826 | 0.0618 | 0.1035 | 0.0996 | 0.0720 |
| als | `{'weighting': 'raw', 'factors': 32, 'reg': 0.01, 'alpha': 0.1, 'iters': 15, 'conf': 'n_days_hl8'}` | 0.0830 | 0.0858 | 0.0801 | 0.0605 | 0.1010 | 0.0968 | 0.0706 |

Selected: `{'weighting': 'bm25', 'factors': 8, 'reg': 0.01, 'alpha': 0.3, 'iters': 15, 'conf': 'n_days_hl8', 'bm25_k1': 100, 'bm25_b': 0.8}` (select 0.2963).

Total runtime: 30.8 s.

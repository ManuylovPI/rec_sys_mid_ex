# Join verification

Generated 2026-10-22 16:18:53 on Windows-10-10.0.26200-SP0, Python 3.11.9, duckdb 2.0.0.

Users: view-segment rows sampled with reservoir(300) seed 42, then their distinct users. Brute force = plain channel + interval-overlap join, no hour buckets.

## Bucketed join vs brute force

| users | brute_pairs | built_pairs | brute_overlap_sec | built_overlap_sec | mismatched_pairs |
|---|---|---|---|---|---|
| 285 | 629043 | 629043 | 754031047 | 754031047 | 0 |

Runtime: 5.8 s.

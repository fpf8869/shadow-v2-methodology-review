# Reproduction data and source vintage

This research code uses three 2026 sportsdataverse GitHub release assets. Do not use newer rolling assets as if they were the October 13 snapshot: verify each exact SHA-256 before running.

* Schedule: https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_cfb_schedules/cfb_schedule_2026.csv — SHA256 `56707a541720854b4b362b8879231adb9eb633c0829e1065a75aa59441752d80`
* Team box: https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_cfb_team_box/team_box_2026.csv — SHA256 `4e612b2056707d0cccdb8e6db69047e286e39316d561e4d686c59e5e85261b18`
* Advanced passing: https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_cfb_adv_passing/adv_passing_2026.csv — SHA256 `b5c174db6e50481b67aee40f5c24faa93c489b75d330db004e66339646eccaf4`

The original publication time of each underlying game statistic was NOT independently verified. The files are an October 13 locally captured source snapshot, not a publisher-attested historical vintage. For tests requiring the three CSVs, download the exact archived bytes or request a byte-for-byte copy; rolling assets may have changed. Do not commit private betting tickets or credentials.

Run: `python -m unittest discover -p 'test_*.py' -v`. If CSVs are unavailable, data-dependent tests are skipped and must NOT be claimed as passed.

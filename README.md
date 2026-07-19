# benchmark-grids

Real power-system test-case grids, vendored here as a fixed, version-controlled
copy rather than fetched from a live URL at benchmark time. See
[PROVENANCE.md](./PROVENANCE.md) for where each grid actually comes from and
its licensing.

- `matpower/` — 12 MATPOWER-format `.m` case files (14 to 9,241 buses), used
  by [gridoxide](https://github.com/m-mirz/gridoxide)'s
  `scripts/bench/run_case_suite.py`.

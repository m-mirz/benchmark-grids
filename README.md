# benchmark-grids

Real power-system test-case grids, vendored here as a fixed, version-controlled
copy rather than fetched from a live URL at benchmark time. See
[PROVENANCE.md](./PROVENANCE.md) for where each grid actually comes from and
its licensing.

- `matpower/` — 27 MATPOWER-format `.m` case files: 12 meshed transmission
  cases (14 to 9,241 buses), used by
  [gridoxide](https://github.com/m-mirz/gridoxide)'s
  `scripts/bench/run_case_suite.py`, and 15 radial distribution feeders (4 to
  141 buses), used by [grid-bench](https://github.com/m-mirz/grid-bench).
- `matpower-plain/` — the 13 distribution cases whose files convert units in
  MATLAB code, with that code evaluated (plain data for importers that do not
  run MATLAB); regenerate with `scripts/evaluate_matpower_code.py`.
- `generated/` — 4 synthetic radial MV/LV distribution grids (1,004 to 29,840
  buses) in MATPOWER format, from power-grid-model's grid generator;
  regenerate with `scripts/generate_distribution.py`.
- `scripts/` — the generator, the exporter and its check, the code evaluator.

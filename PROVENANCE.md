# benchmark-grids provenance

This repo exists to give gridoxide (and any other project benchmarking
against real power-system test-case grids) a fixed, version-controlled copy
of the grids it uses — vendored here rather than fetched from a live URL at
benchmark time.

## `matpower/`

Twenty-seven MATPOWER-format `.m` case files: twelve meshed transmission
cases (14 to 9,241 buses), used by gridoxide's `scripts/bench/run_case_suite.py`
(see that project's `scripts/bench/README.md` for the full benchmark
methodology and results), and fifteen radial distribution feeders (4 to 141
buses) that MATPOWER bundles from the distribution-grid literature, used by
grid-bench.

- **Upstream**: https://github.com/m-mirz/matpower (a fork of
  [MATPOWER](https://github.com/MATPOWER/matpower), maintained by the same
  author as this repo)
- **Commit**: `95d5a6fabb663167cf7eaff7f67acb41cddbad94`
- **Path in upstream**: `data/<filename>.m`

| Case name (as used by gridoxide) | MATPOWER filename | Buses |
|---|---|---|
| `case14` | `case14.m` | 14 |
| `case118` | `case118.m` | 118 |
| `case_illinois200` | `case_ACTIVSg200.m` | 200 |
| `case300` | `case300.m` | 300 |
| `case1354pegase` | `case1354pegase.m` | 1,354 |
| `case1888rte` | `case1888rte.m` | 1,888 |
| `case2848rte` | `case2848rte.m` | 2,848 |
| `case2869pegase` | `case2869pegase.m` | 2,869 |
| `case3120sp` | `case3120sp.m` | 3,120 |
| `case6495rte` | `case6495rte.m` | 6,495 |
| `case6515rte` | `case6515rte.m` | 6,515 |
| `case9241pegase` | `case9241pegase.m` | 9,241 |

Distribution cases, same upstream commit and path, filename = case name.
All radial as operated; the three with more branches than `buses - 1` carry
out-of-service tie switches (`status = 0`) for reconfiguration studies.

| Case | Buses | Branches | Source (from the file header) |
|---|---|---|---|
| `case4_dist` | 4 | 3 | MATPOWER's own 4-bus radial example |
| `case12da` | 12 | 11 | Das et al. |
| `case15da` | 15 | 14 | Das et al. |
| `case15nbr` | 15 | 14 | Battu et al. |
| `case18` | 18 | 17 | Grady, Samotyj, Noyola |
| `case18nbr` | 18 | 17 | Battu et al. |
| `case22` | 22 | 21 | Raju et al. |
| `case28da` | 28 | 27 | Das et al. |
| `case33bw` | 33 | 37 | Baran & Wu (network reconfiguration) |
| `case33mg` | 33 | 37 | Kashem et al. |
| `case69` | 69 | 68 | Baran & Wu (capacitor placement) |
| `case85` | 85 | 84 | Das et al. |
| `case118zh` | 118 | 132 | Zhang et al. |
| `case136ma` | 136 | 156 | Mantovani et al. |
| `case141` | 141 | 140 | Khodr et al. (Caracas metropolitan area) |

`case_illinois200` is Texas A&M's synthetic ACTIVSg200 grid, bundled in
MATPOWER under the `case_ACTIVSg200` filename instead of matching its own
case name — kept as `case_illinois200` here for consistency with the
downstream case-name lists that reference it (e.g. gridoxide's
`scripts/bench/cases.py`, lightsim2grid's own benchmark case list).

### Licensing

MATPOWER's own `LICENSE` file draws an explicit distinction: the *code* is
3-clause BSD, but the *case files* are **not** covered by that license —
"In most cases, the data has either been included with permission or has
been converted from data available from a public source." Copied here on
that same basis as MATPOWER's own distribution, not under a separate,
clearer grant — anyone redistributing further should look at the
provenance notes MATPOWER itself carries for each case (most are public
grid models or synthetic grids like ACTIVSg200 built explicitly for public
research use, not proprietary utility data).

### Updating

To refresh from a newer upstream commit, re-download each file listed above
from `https://raw.githubusercontent.com/m-mirz/matpower/<new-commit>/data/<filename>`
and update the commit hash here.

## `matpower-plain/`

Derived, not downloaded: thirteen of the fifteen distribution files store
the literature's data as published (branch impedance in ohm, load in kW)
and convert it to per unit in MATLAB statements after the matrices
(case141 also derives Q from a 0.85 power factor). A power-flow tool's
MATPOWER importer parses the matrices and does not run that code, so it
would read a different grid. `scripts/evaluate_matpower_code.py` applies
exactly those statements (the four kinds that occur; it refuses any other
code) and writes the result as plain-data files here, with the evaluated
statements quoted in each file's header. `case4_dist` and `case18` are
plain data as shipped and have no copy.

Checked against the literature: power flows of `case33bw` and `case69`
give 202.68 kW and 224.99 kW of losses and a minimum voltage of 0.91309
p.u. at bus 18 and 0.90919 p.u. at bus 65, Baran & Wu's figures.

## `generated/`

Synthetic radial MV/LV distribution grids at scales the literature feeders
do not reach, generated here rather than downloaded. Regenerate with

    python3 scripts/generate_distribution.py            # stdlib only
    python3 scripts/generate_distribution.py --check    # + numpy, scipy, power-grid-model

Both steps are deterministic (fixed seed 42); the output is byte-identical
on every run.

| Case | Buses | `--target-nodes` | LV grids | Load (MW) | |V| MV/LV (p.u.) |
|---|---|---|---|---|---|
| `mvlv1004` | 1,004 | 1,500 | 1 | 158.4 | 0.67 to 0.76 |
| `mvlv2606` | 2,606 | 4,000 | 3 | 158.1 | 0.67 to 0.77 |
| `mvlv10616` | 10,616 | 13,000 | 13 | 149.7 | 0.71 to 0.82 |
| `mvlv29840` | 29,840 | 30,000 | 37 | 129.7 | 0.78 to 0.89 |

One 150 kV source feeds four parallel 150/10.5 kV transformers, twenty MV
feeders with loads, and 10.5/0.42 kV secondary substations each supplying
an LV grid of ~800 nodes with single-phase loads. Voltages are low
(table): this is power-grid-model's own benchmark loading, kept as
generated, not rescaled to a realistic operating point. It is a well-posed
power flow and a harder one than a lightly loaded feeder.

1. **Generator**: `scripts/gridoxide_generate_grid.py`, vendored unmodified
   (apart from a provenance header) from gridoxide 0.0.2 (Apache-2.0), file
   `python/gridoxide/generate_grid.py` of the PyPI sdist
   (sdist sha256 `19f9ef42a6268415a0ef16bc15a77b0b539b9ababd974c6651f37bbb0061f60e`,
   body sha256 in the file header). It ports power-grid-model's C++
   `FictionalGridGenerator` with the option values of power-grid-model's
   release-mode benchmark, and writes a power-grid-model `input` JSON.
2. **Export**: `scripts/pgm_to_matpower.py` turns that JSON into a MATPOWER
   case; its docstring lists every modelling decision. The ones that change
   the problem: single-phase loads become balanced loads of the same total
   power, every load is constant power, vector-group phase shifts are
   dropped (radial, so no flow or magnitude changes), and line dielectric
   losses become bus shunt conductance.
3. **Check**: `scripts/check_export.py` solves the generated grid with
   power-grid-model (with the same simplifications applied to its input)
   and evaluates that solution against the exported case's own power-flow
   equations, using a bus admittance matrix built from the `.m` file alone
   (MATPOWER's `makeYbus` conventions). All four cases: largest mismatch
   under 2e-10 MVA, i.e. the `.m` file is the same power-flow problem as
   power-grid-model's.

# benchmark-grids provenance

This repo exists to give gridoxide (and any other project benchmarking
against real power-system test-case grids) a fixed, version-controlled copy
of the grids it uses — vendored here rather than fetched from a live URL at
benchmark time.

## `matpower/`

Twelve real MATPOWER-format `.m` case files, ranging 14 to 9,241 buses, used
by gridoxide's `scripts/bench/run_case_suite.py` (see that project's
`scripts/bench/README.md` for the full benchmark methodology and results).

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

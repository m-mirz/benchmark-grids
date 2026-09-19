"""Exports a power-grid-model `input` document (as written by
gridoxide_generate_grid.py) to a MATPOWER case: the balanced, positive-
sequence power-flow problem the benchmark solves.

    python3 pgm_to_matpower.py <input.json> <output.m> [--name NAME]

Standard library only. Every modelling decision, in the order the file is
built:

- Buses: one per PGM `node`, bus number = node id, `baseKV = u_rated / 1e3`.
  baseMVA = 100.
- Slack: a PGM `source` is an ideal voltage `u_ref` behind an impedance
  (`sk`, `rx_ratio`). It becomes a new slack bus (number = largest id + 1,
  Vg = u_ref, angle 0) joined to the source's node by that impedance:
  |z| = baseMVA / sk (p.u.), x = |z| / sqrt(1 + rx^2), r = rx * x.
- Lines: pi-model. r1/x1 [ohm] and c1 [F] become p.u. on the from node's
  base; b = 2*pi*50*c1. The dielectric loss conductance g = tan1 * b, which a
  MATPOWER branch cannot hold, becomes bus shunt conductance, g/2 at each end.
- Transformers: the ideal ratio t = (u1/U1)/(u2/U2) (u1, u2 the winding
  voltages, u1 moved by (tap_pos - tap_nom) * tap_size when tap_side is 0,
  U1, U2 the nodes' u_rated) sits at the from side; the series impedance on
  the to side: |z| = uk * u2^2 / sn, r = pk * u2^2 / sn^2 [ohm], in p.u. of
  the to node's base. The magnetizing admittance (|y| = i0 * sn / u2^2,
  g = p0 / u2^2, inductive) is split half to each end, as power-grid-model's
  transformer pi-model does (check_export.py found this: with all of it at
  the to node, the HV/MV busbars were off by half the magnetizing power):
  half as a bus shunt at the to node, half at the from node referred through
  the ideal ratio (divided by t^2, like MATPOWER's own line charging).
  Vector-group phase shifts (`clock`) are dropped: in a radial network they
  rotate the angles of everything downstream and change no flow or
  magnitude, while keeping them would give every LV transformer a 30 degree
  phase shifter that some tools' importers cannot represent.
- Loads: a `sym_load` becomes Pd/Qd. An `asym_load` (single-phase in these
  grids) becomes a balanced load with the sum of its phase powers: the
  benchmark is a balanced power flow. Every load is constant power; the
  generator's random `type` (constant impedance / current) is dropped,
  MATPOWER has only constant-power loads.
- Shunts: `g1`/`b1` [S] become bus shunts at the node's u_rated.

`simplified_input` applies the same simplifications to the PGM document
itself, so that power-grid-model's own solution of it must satisfy the
exported case's equations exactly; check_export.py tests that.
"""
import argparse
import json
import math
import sys
from pathlib import Path

BASE_MVA = 100.0
F_HZ = 50.0
BIG = 1e5


def export(doc: dict, name: str) -> str:
    data = doc["data"]
    s_base = BASE_MVA * 1e6
    u_rated = {n["id"]: n["u_rated"] for n in data["node"]}
    gs = {i: 0.0 for i in u_rated}   # MW at 1 p.u.
    bs = {i: 0.0 for i in u_rated}   # MVAr at 1 p.u.
    pd = {i: 0.0 for i in u_rated}
    qd = {i: 0.0 for i in u_rated}
    branches = []

    def zbase(node):
        return u_rated[node] ** 2 / s_base

    slack = max(max(u_rated), *(c["id"] for comp in data.values() for c in comp)) + 1
    (source,) = data["source"]                       # the generator writes exactly one
    z = BASE_MVA * 1e6 / source["sk"]
    x = z / math.sqrt(1 + source["rx_ratio"] ** 2)
    branches.append((slack, source["node"], source["rx_ratio"] * x, x, 0.0, 0.0))

    w = 2 * math.pi * F_HZ
    for ln in data["line"]:
        f, t = ln["from_node"], ln["to_node"]
        assert u_rated[f] == u_rated[t], f"line {ln['id']} joins different voltage levels"
        zb = zbase(f)
        b = w * ln["c1"]
        g = ln["tan1"] * b
        branches.append((f, t, ln["r1"] / zb, ln["x1"] / zb, b * zb, 0.0))
        for node in (f, t):
            gs[node] += g / 2 * zb * BASE_MVA

    for tr in data["transformer"]:
        f, t = tr["from_node"], tr["to_node"]
        u1 = tr["u1"] + ((tr["tap_pos"] - tr["tap_nom"]) * tr["tap_size"] if tr["tap_side"] == 0 else 0.0)
        u2 = tr["u2"] - ((tr["tap_pos"] - tr["tap_nom"]) * tr["tap_size"] if tr["tap_side"] == 1 else 0.0)
        ratio = (u1 / u_rated[f]) / (u2 / u_rated[t])
        zt = tr["uk"] * u2 ** 2 / tr["sn"]
        rt = tr["pk"] * u2 ** 2 / tr["sn"] ** 2
        xt = math.sqrt(zt ** 2 - rt ** 2)
        zb = zbase(t)
        branches.append((f, t, rt / zb, xt / zb, 0.0, ratio))
        ym = tr["i0"] * tr["sn"] / u2 ** 2
        gm = tr["p0"] / u2 ** 2
        bm = -math.sqrt(max(ym ** 2 - gm ** 2, 0.0))
        for node, scale in ((t, 0.5), (f, 0.5 / ratio ** 2)):
            gs[node] += scale * gm * zb * BASE_MVA
            bs[node] += scale * bm * zb * BASE_MVA

    for sh in data.get("shunt", []):
        zb = zbase(sh["node"])
        gs[sh["node"]] += sh["g1"] * zb * BASE_MVA
        bs[sh["node"]] += sh["b1"] * zb * BASE_MVA

    for ld in data.get("sym_load", []):
        pd[ld["node"]] += ld["p_specified"] / 1e6
        qd[ld["node"]] += ld["q_specified"] / 1e6
    for ld in data.get("asym_load", []):
        pd[ld["node"]] += sum(ld["p_specified"]) / 1e6
        qd[ld["node"]] += sum(ld["q_specified"]) / 1e6

    kv = lambda i: u_rated[i] / 1e3
    lines = [f"function mpc = {name}",
             f"%{name.upper()}  Synthetic radial MV/LV distribution grid, balanced.",
             "%   Generated by benchmark-grids/scripts/generate_distribution.py (seed 42):",
             "%   gridoxide 0.0.2 generate_grid, exported by pgm_to_matpower.py",
             "%   (see its docstring for every modelling decision) - PROVENANCE.md.",
             "", "%% MATPOWER Case Format : Version 2", "mpc.version = '2';",
             "", f"mpc.baseMVA = {BASE_MVA:g};", "",
             "%% bus data", "%\tbus_i\ttype\tPd\tQd\tGs\tBs\tarea\tVm\tVa\tbaseKV\tzone\tVmax\tVmin",
             "mpc.bus = ["]
    lines.append(f"\t{slack}\t3\t0\t0\t0\t0\t1\t{source['u_ref']:.10g}\t0\t{kv(source['node']):.10g}\t1\t1.1\t0.9;")
    for i in sorted(u_rated):
        lines.append(f"\t{i}\t1\t{pd[i]:.12g}\t{qd[i]:.12g}\t{gs[i]:.12g}\t{bs[i]:.12g}\t1\t1\t0\t{kv(i):.10g}\t1\t1.1\t0.9;")
    lines += ["];", "", "%% generator data",
              "%\tbus\tPg\tQg\tQmax\tQmin\tVg\tmBase\tstatus\tPmax\tPmin\tPc1\tPc2\tQc1min\tQc1max"
              "\tQc2min\tQc2max\tramp_agc\tramp_10\tramp_30\tramp_q\tapf",
              "mpc.gen = [",                          # all 21 columns, as MATPOWER's own cases: some importers require them
              f"\t{slack}\t0\t0\t{BIG:g}\t{-BIG:g}\t{source['u_ref']:.10g}\t{BASE_MVA:g}\t1\t{BIG:g}\t0"
              + "\t0" * 11 + ";",
              "];", "", "%% branch data",
              "%\tfbus\ttbus\tr\tx\tb\trateA\trateB\trateC\tratio\tangle\tstatus\tangmin\tangmax",
              "mpc.branch = ["]
    for f, t, r, x, b, ratio in branches:
        lines.append(f"\t{f}\t{t}\t{r:.12g}\t{x:.12g}\t{b:.12g}\t0\t0\t0\t{ratio:.12g}\t0\t1\t-360\t360;")
    lines += ["];", ""]
    return "\n".join(lines)


def simplified_input(doc: dict) -> dict:
    """The PGM document with the export's simplifications applied (balanced
    constant-power loads, no vector-group phase shift), for check_export.py."""
    data = json.loads(json.dumps(doc["data"]))
    sym = [dict(ld, type=0) for ld in data.get("sym_load", [])]
    for ld in data.pop("asym_load", []):
        sym.append({"id": ld["id"], "node": ld["node"], "status": ld["status"], "type": 0,
                    "p_specified": sum(ld["p_specified"]), "q_specified": sum(ld["q_specified"])})
    data["sym_load"] = sym
    for tr in data["transformer"]:
        tr.update(clock=0, winding_from=0, winding_to=0)
    return dict(doc, data=data)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--name", default=None)
    a = ap.parse_args(argv)
    name = a.name or Path(a.output).stem
    Path(a.output).write_text(export(json.loads(Path(a.input).read_text()), name))


if __name__ == "__main__":
    sys.exit(main())

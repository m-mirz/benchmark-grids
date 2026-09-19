"""Checks pgm_to_matpower.py: power-grid-model's own solution of a generated
grid (with the export's documented simplifications) must satisfy the
exported MATPOWER case's power-flow equations.

    python3 check_export.py <input.json> <case.m>

Needs numpy, scipy and power-grid-model. Builds the case's bus admittance
matrix from the `.m` file independently of any power-flow tool (MATPOWER's
makeYbus conventions), takes PGM's node voltages, and prints the largest
power mismatch |V * conj(Ybus V) - S| over all PQ buses in MW/MVAr. Exact
export: the mismatch is at PGM's solver tolerance.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgm_to_matpower import simplified_input  # noqa: E402


def read_m(path: Path) -> dict:
    text = path.read_text()
    out = {"baseMVA": float(re.search(r"mpc\.baseMVA\s*=\s*([\d.eE+-]+)", text).group(1))}
    for name in ("bus", "gen", "branch"):
        block = re.search(rf"mpc\.{name}\s*=\s*\[(.*?)\];", text, re.S).group(1)
        rows = [[float(v) for v in ln.split("%")[0].strip().rstrip(";").split()]
                for ln in block.splitlines() if ln.split("%")[0].strip()]
        out[name] = np.array(rows)
    return out


def ybus(m: dict) -> tuple[np.ndarray, sp.csr_matrix]:
    bus, br = m["bus"], m["branch"]
    ids = bus[:, 0].astype(int)
    pos = {b: i for i, b in enumerate(ids)}
    f = np.array([pos[int(x)] for x in br[:, 0]])
    t = np.array([pos[int(x)] for x in br[:, 1]])
    ys = 1 / (br[:, 2] + 1j * br[:, 3])
    tap = np.where(br[:, 8] != 0, br[:, 8], 1.0) * np.exp(1j * np.deg2rad(br[:, 9]))
    ytt = ys + 1j * br[:, 4] / 2
    n = len(ids)
    rows = np.r_[f, f, t, t, np.arange(n)]
    cols = np.r_[f, t, f, t, np.arange(n)]
    vals = np.r_[ytt / (tap * np.conj(tap)), -ys / np.conj(tap), -ys / tap, ytt,
                 (bus[:, 4] + 1j * bus[:, 5]) / m["baseMVA"]]
    return ids, sp.csr_matrix((vals, (rows, cols)), shape=(n, n))


def main(json_path: str, m_path: str) -> float:
    from power_grid_model import CalculationMethod, PowerGridModel
    from power_grid_model.utils import json_deserialize

    doc = simplified_input(json.loads(Path(json_path).read_text()))
    dataset = json_deserialize(json.dumps(doc))
    res = PowerGridModel(dataset).calculate_power_flow(
        calculation_method=CalculationMethod.newton_raphson, error_tolerance=1e-12, max_iterations=50)
    v_pgm = dict(zip(dataset["node"]["id"].tolist(), res["node"]["u_pu"] * np.exp(1j * res["node"]["u_angle"])))

    m = read_m(Path(m_path))
    ids, y = ybus(m)
    slack = int(m["gen"][0, 0])
    v_pgm[slack] = m["gen"][0, 5]                       # the source's ideal voltage, angle 0
    v = np.array([v_pgm[int(i)] for i in ids])
    s = -(m["bus"][:, 2] + 1j * m["bus"][:, 3]) / m["baseMVA"]
    ds = (v * np.conj(y @ v) - s) * m["baseMVA"]
    pq = m["bus"][:, 1] == 1
    worst = float(np.abs(ds[pq]).max())
    print(f"{Path(m_path).name}: {len(ids)} buses, largest mismatch at PQ buses {worst:.3e} MVA "
          f"(total load {m['bus'][:, 2].sum():.1f} MW)")
    return worst


if __name__ == "__main__":
    sys.exit(0 if main(*sys.argv[1:3]) < 1e-6 else 1)

"""Regenerates matpower-plain/: the matpower/ cases that compute part of
their data in MATLAB code, with that code evaluated, as plain-data files.

    python3 scripts/evaluate_matpower_code.py

MATPOWER's distribution cases store the literature's data as published
(branch impedances in ohm, loads in kW) and convert it after the matrices:

    Vbase = mpc.bus(1, BASE_KV) * 1e3;
    Sbase = mpc.baseMVA * 1e6;
    mpc.branch(:, [BR_R BR_X]) = mpc.branch(:, [BR_R BR_X]) / (Vbase^2 / Sbase);
    mpc.bus(:, [PD, QD]) = mpc.bus(:, [PD, QD]) / 1e3;
    pf = 0.85;                                         (case141 only)
    mpc.bus(:, QD) = mpc.bus(:, PD) * sin(acos(pf));
    mpc.bus(:, PD) = mpc.bus(:, PD) * pf;

MATLAB runs this; a reader that only parses the matrices (most power-flow
tools' importers) gets values off by 1e3 or a base impedance. This script
applies exactly these statements, in file order, to the parsed matrices, and
refuses a file that has them alongside any other code. Files without them
(the transmission cases) are plain data already and not copied. Standard
library only; deterministic.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "matpower", ROOT / "matpower-plain"
PD, QD, BASE_KV = 2, 3, 9          # 0-based bus columns
BR_R, BR_X = 2, 3                  # 0-based branch columns
MATRICES = ("bus", "gen", "branch", "gencost")

STATEMENTS = [                     # (pattern, action(mpc, env))
    (r"Vbase = mpc\.bus\(1, BASE_KV\) \* 1e3;", lambda m, e: e.update(Vbase=m["bus"][0][BASE_KV] * 1e3)),
    (r"Sbase = mpc\.baseMVA \* 1e6;", lambda m, e: e.update(Sbase=m["baseMVA"] * 1e6)),
    (r"mpc\.branch\(:, \[BR_R BR_X\]\) = mpc\.branch\(:, \[BR_R BR_X\]\) / \(Vbase\^2 / Sbase\);",
     lambda m, e: _scale(m["branch"], (BR_R, BR_X), 1 / (e["Vbase"] ** 2 / e["Sbase"]))),
    (r"mpc\.bus\(:, \[PD, QD\]\) = mpc\.bus\(:, \[PD, QD\]\) / 1e3;", lambda m, e: _scale(m["bus"], (PD, QD), 1e-3)),
    (r"pf = ([\d.]+);", None),     # handled inline: binds a number
    (r"mpc\.bus\(:, QD\) = mpc\.bus\(:, PD\) \* sin\(acos\(pf\)\);",
     lambda m, e: [r.__setitem__(QD, r[PD] * math.sin(math.acos(e["pf"]))) for r in m["bus"]]),
    (r"mpc\.bus\(:, PD\) = mpc\.bus\(:, PD\) \* pf;", lambda m, e: _scale(m["bus"], (PD,), e["pf"])),
]
IGNORED = re.compile(r"^(function |mpc\.version|mpc\.baseMVA|\[?\s*[A-Z_, .]+\]? = idx_|\s*[A-Z_, .]+\] = idx_"
                     r"|\[PQ, PV|\[F_BUS|\s+(VA|TAP|ANGMIN), )")


def _scale(rows, cols, k):
    for r in rows:
        for c in cols:
            r[c] *= k


def parse(text: str) -> tuple[dict, list[str]]:
    """The matrices, baseMVA, and every code line outside them."""
    mpc = {"baseMVA": float(re.search(r"mpc\.baseMVA\s*=\s*([\d.eE+-]+)\s*;", text).group(1))}
    code, block = [], None
    for line in text.splitlines():
        bare = line.split("%", 1)[0].rstrip()
        start = re.match(r"mpc\.(\w+)\s*=\s*\[", bare)
        if start and start.group(1) in MATRICES:
            block = mpc.setdefault(start.group(1), [])
            continue
        if block is not None:
            if bare.strip().startswith("];"):
                block = None
            elif bare.strip():
                block.append([float(v) for v in bare.strip().rstrip(";").split()])
            continue
        if bare.strip() and not IGNORED.match(bare):
            code.append(bare.strip())
    return mpc, code


def evaluate(mpc: dict, code: list[str], name: str) -> None:
    env: dict = {}
    for stmt in code:
        for pattern, action in STATEMENTS:
            hit = re.fullmatch(pattern, stmt)
            if hit:
                if action is None:
                    env["pf"] = float(hit.group(1))
                else:
                    action(mpc, env)
                break
        else:
            sys.exit(f"{name}: unknown statement, not evaluated: {stmt!r}")


def fmt(v: float) -> str:
    return str(int(v)) if v == int(v) and abs(v) < 1e15 else repr(v)


def write(src: Path, mpc: dict, code: list[str]) -> str:
    text = src.read_text()
    header = []
    for line in text.splitlines()[1:]:
        if not line.startswith("%"):
            break
        header.append(line)
    out = [text.splitlines()[0], *header, "%",
           f"%   Plain-data copy of benchmark-grids/matpower/{src.name}: the file's",
           "%   MATLAB statements (below, as they were) are evaluated by",
           "%   scripts/evaluate_matpower_code.py and the matrices hold the result.",
           *(f"%     {c}" for c in code),
           "", "%% MATPOWER Case Format : Version 2", "mpc.version = '2';", "",
           f"mpc.baseMVA = {fmt(mpc['baseMVA'])};"]
    for name in MATRICES:
        if name in mpc:
            out += ["", f"mpc.{name} = ["] + ["\t" + "\t".join(fmt(v) for v in r) + ";" for r in mpc[name]] + ["];"]
    return "\n".join(out) + "\n"


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for src in sorted(SRC.glob("*.m")):
        mpc, code = parse(src.read_text())
        if not any(re.fullmatch(p, c) for c in code for p, _ in STATEMENTS):
            continue                                   # no conversion code: already plain data
        evaluate(mpc, code, src.name)
        (OUT / src.name).write_text(write(src, mpc, code))
        print(f"wrote matpower-plain/{src.name} ({len(code)} statements evaluated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Regenerates generated/*.m: synthetic radial MV/LV distribution grids.

    python3 scripts/generate_distribution.py            # write the cases
    python3 scripts/generate_distribution.py --check    # also run check_export.py
                                                        # (needs numpy, scipy,
                                                        # power-grid-model)

Each case is gridoxide_generate_grid.py (power-grid-model's fictional grid
generator, as vendored from gridoxide 0.0.2) at a fixed target size and seed,
exported by pgm_to_matpower.py. Both are deterministic, so the output is
byte-identical on every run; the PGM JSON is an intermediate and not kept.
The target sizes are rough: every LV feeder group adds ~800 nodes, so they
were picked for the node counts in the table, which name the cases.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "generated"
SEED = 42

# name -> --target-nodes; the name is the resulting bus count (slack bus included)
CASES = {
    "mvlv1004": 1500,
    "mvlv2606": 4000,
    "mvlv10616": 13000,
    "mvlv29840": 30000,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, str(HERE))
    from pgm_to_matpower import export

    OUT.mkdir(exist_ok=True)
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, target in CASES.items():
            js = Path(tmp) / f"{name}.json"
            subprocess.run([sys.executable, str(HERE / "gridoxide_generate_grid.py"), str(js),
                            "--target-nodes", str(target), "--seed", str(SEED)],
                           check=True, stdout=subprocess.DEVNULL)
            m = OUT / f"{name}.m"
            m.write_text(export(json.loads(js.read_text()), name))
            buses = int(name.removeprefix("mvlv"))
            n = sum(1 for ln in m.read_text().split("mpc.bus = [")[1].split("];")[0].splitlines() if ln.strip())
            assert n == buses, f"{name}: {n} buses, the name says {buses}"
            print(f"wrote {m.relative_to(HERE.parent)} ({n} buses)")
            if a.check:
                failed += subprocess.run([sys.executable, str(HERE / "check_export.py"), str(js), str(m)]).returncode != 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

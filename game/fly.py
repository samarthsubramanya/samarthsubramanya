#!/usr/bin/env python3
"""Pixel Flight: issue-driven flappy-style game rendered to game/board.svg.

Usage: fly.py "fly: up|down|hold" <pilot>   |   fly.py --selftest
State: game/state.json. Plane sits in column 2; each move scrolls the world one column.
"""
import json, random, sys, pathlib

HERE = pathlib.Path(__file__).parent
COLS, ROWS, CELL, PLANE_COL, GAP = 16, 7, 24, 2, 3
MOVES = {"up": -1, "down": 1, "hold": 0}


def new_column(rng, i):
    if i % 4:
        return []
    top = rng.randrange(0, ROWS - GAP + 1)
    return [r for r in range(ROWS) if not top <= r < top + GAP]


def fresh(seed):
    rng = random.Random(seed)
    return {"row": ROWS // 2, "score": 0, "best": 0, "best_pilot": "", "last": "", "seed": seed,
            "tick": COLS, "cols": [[] if i < PLANE_COL + 2 else new_column(rng, i) for i in range(COLS)]}


def step(s, move, pilot):
    s["row"] = min(ROWS - 1, max(0, s["row"] + MOVES[move]))
    s["last"] = f"@{pilot} {move}"
    rng = random.Random(s["seed"] + s["tick"])
    s["cols"] = s["cols"][1:] + [new_column(rng, s["tick"])]
    s["tick"] += 1
    if s["row"] in s["cols"][PLANE_COL]:
        s.update(fresh(s["seed"] + 1), best=max(s["best"], s["score"]),
                 best_pilot=s["best_pilot"] if s["best"] >= s["score"] else pilot,
                 last=f"@{pilot} crashed at {s['score']} — new flight")
        return "crash"
    s["score"] += 1
    return "ok"


def render(s):
    W, H = COLS * CELL, ROWS * CELL + 30
    px = lambda x, y, c, w=1, h=1: f'<rect x="{x}" y="{y}" width="{w * 4}" height="{h * 4}" fill="{c}"/>'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * 2}" height="{H * 2}" shape-rendering="crispEdges" font-family="ui-monospace,Menlo,monospace">',
         f'<rect width="{W}" height="{H}" fill="#0b2942"/>']
    for i, col in enumerate(s["cols"]):
        for r in col:
            o.append(f'<rect x="{i * CELL}" y="{r * CELL}" width="{CELL}" height="{CELL}" fill="#4a6b7c"/>'
                     f'<rect x="{i * CELL + 4}" y="{r * CELL + 4}" width="{CELL - 8}" height="{CELL - 8}" fill="#6f95a8"/>')
    x, y = PLANE_COL * CELL, s["row"] * CELL
    o += [px(x + 4, y + 8, "#ffffff", 4, 2), px(x + 20, y + 8, "#ffc857"), px(x + 4, y + 4, "#59d9ff"),
          px(x + 8, y + 16, "#ffffff", 2), px(x, y + 12, "#8edfff")]
    o.append(f'<text x="6" y="{H - 10}" font-size="11" fill="#8edfff">SCORE {s["score"]}  BEST {s["best"]} {s["best_pilot"]}'
             f'</text><text x="{W - 6}" y="{H - 10}" font-size="9" fill="#ffc857" text-anchor="end">{s["last"][:34]}</text></svg>')
    return "\n".join(o)


def selftest():
    s = fresh(1)
    assert step(s, "hold", "t") == "ok" and s["score"] == 1
    s["cols"][PLANE_COL + 1] = [s["row"]]
    assert step(s, "hold", "t") == "crash" and s["score"] == 0 and s["best"] == 1 and s["best_pilot"] == "t"
    assert "<svg" in render(s)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest(); sys.exit()
    state_f = HERE / "state.json"
    s = json.loads(state_f.read_text()) if state_f.exists() else fresh(42)
    move = sys.argv[1].split(":", 1)[-1].strip().lower()
    if move not in MOVES:
        sys.exit(f"unknown move {move!r}; use up/down/hold")
    print(step(s, move, sys.argv[2] if len(sys.argv) > 2 else "anon"))
    state_f.write_text(json.dumps(s))
    (HERE / "board.svg").write_text(render(s))

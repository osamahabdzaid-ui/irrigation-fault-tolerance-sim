import sys, json, os, time, numpy as np
sys.path.insert(0, "/home/claude/an")
import harness
name = sys.argv[1]; cfg = json.loads(sys.argv[2])
ns = harness.load(cfg.get("mode", "dev"), **cfg.get("load", {}))
run = ns["run"]
seeds = range(cfg["seed0"], cfg["seed0"] + cfg["n"])
out = json.load(open("batch_results.json")) if os.path.exists("batch_results.json") else {}
t0 = time.time()
for sc, ctrls in cfg["plan"]:
    for c in ctrls:
        R = [run(c, sc, k) for k in seeds]
        w, d, br, eta = (np.array([r[i] for r in R]) for i in (0, 1, 6, 7))
        fp, tn, tp, fn = (sum(r[4][i] for r in R) for i in (1, 3, 0, 2))
        dl = [r[3] for r in R if r[3] is not None]
        rec = {"water": w.tolist(), "drain": d.tolist(), "below_RAW": br.tolist(), "eta": eta.tolist(), "fp": fp, "tn": tn, "tp": tp, "fn": fn,
               "delay": float(np.mean(dl)) if dl else None}
        out.setdefault(name, {}).setdefault(sc, {})[c] = rec
        print(f"{name:14s}{sc:17s}{c:14s} water {w.mean():7.1f} drain {d.mean():6.2f} gt5 {(d>5).mean():.2f} belowRAW {br.mean():6.1f} ETa/ETc {eta.mean():.3f} | {time.time()-t0:.0f}s", flush=True)
json.dump(out, open("batch_results.json", "w"))

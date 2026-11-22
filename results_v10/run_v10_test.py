# v10 single pre-registered test run: seeds 2000-2099, held-out years 2024-2025. Criteria C1-C5 as written in the Phase B plan, section 7.
import sys, json, numpy as np; sys.path.insert(0, "/home/claude/v10")
import harness10 as h
SEEDS = range(2000, 2100); rng_boot = np.random.default_rng(0)
OUT = {}
def boot_ci(x):
    x = np.asarray(x); m = [rng_boot.choice(x, len(x)).mean() for _ in range(5000)]; return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
for sd in (0.008, 0.03, 0.05):
    ns = h.load("test", bias_sd=sd); run = ns["run"]
    inst = []; f = ns["CTRL"]["reliab10_adapt"]
    ns["CTRL"]["reliab10_adapt"] = lambda f=f: (inst.append(f()) or inst[-1])
    for sc in ("none", "double_stuck_low"):
        for c in ("oracle_adapt", "median_adapt", "reliab_adapt", "reliab10_adapt"):
            R = []; st = []
            for k in SEEDS:
                R.append(run(c, sc, k)); st.append(inst[-1].stalls if c == "reliab10_adapt" else 0)
            OUT[f"{sd}|{sc}|{c}"] = {"water": [r[0] for r in R], "drain": [r[1] for r in R], "below_RAW": [r[6] for r in R], "stalls": st,
                                       "mean_bias": [float(np.random.default_rng(k).normal(0, sd, 3).mean()) for k in SEEDS]}
            print(sd, sc, c, "water %.1f drain>5 %.2f" % (np.mean(OUT[f'{sd}|{sc}|{c}']['water']), np.mean(np.array(OUT[f'{sd}|{sc}|{c}']['drain']) > 5)), flush=True)
json.dump(OUT, open("v10_test_results.json", "w"))
g = lambda sd, sc, c, k: np.array(OUT[f"{sd}|{sc}|{c}"][k])
V = {}
d = g(0.008, "none", "reliab10_adapt", "water") - g(0.008, "none", "reliab_adapt", "water"); lo, hi = boot_ci(d)
V["C1"] = (g(0.008, "none", "reliab10_adapt", "stalls").sum() == 0 and lo >= -3 and hi <= 3, f"stalls={int(g(0.008,'none','reliab10_adapt','stalls').sum())}, water diff CI [{lo:.2f},{hi:.2f}]")
a = (g(0.03, "none", "reliab10_adapt", "drain") > 5).mean(); w = g(0.03, "none", "reliab10_adapt", "water").mean() - g(0.03, "none", "oracle_adapt", "water").mean()
V["C2"] = (a <= 0.05 and w <= 15, f"drain>5mm {100*a:.0f}% (v9 {100*(g(0.03,'none','reliab_adapt','drain')>5).mean():.0f}%), water-oracle {w:.1f} mm")
a = (g(0.05, "none", "reliab10_adapt", "drain") > 5).mean()
V["C3"] = (a <= 0.10, f"drain>5mm {100*a:.0f}% (v9 {100*(g(0.05,'none','reliab_adapt','drain')>5).mean():.0f}%)")
w10 = g(0.008, "double_stuck_low", "reliab10_adapt", "water").mean(); w9 = g(0.008, "double_stuck_low", "reliab_adapt", "water").mean()
V["C4"] = (w10 <= 160 and w10 - w9 <= 5, f"v10 {w10:.1f} mm, v9 {w9:.1f} mm")
diffs = []
for sd in (0.03, 0.05):
    pos = g(sd, "none", "reliab10_adapt", "mean_bias") > 0
    diffs += list(g(sd, "none", "reliab10_adapt", "below_RAW")[pos] - g(sd, "none", "reliab_adapt", "below_RAW")[pos])
V["C5"] = (np.mean(diffs) <= 10, f"below-threshold hours v10-v9 on positive-offset runs: {np.mean(diffs):.1f} h (n={len(diffs)})")
print("\nPRE-REGISTERED CRITERIA")
for k, (ok, msg) in V.items(): print(k, "PASS" if ok else "FAIL", "|", msg)

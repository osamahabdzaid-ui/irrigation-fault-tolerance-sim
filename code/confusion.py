import sys, json, os, time, numpy as np
sys.path.insert(0, "/home/claude/an")
import harness
scen_list = sys.argv[1].split(","); ctrls = ["reliab", "reliab_adapt"]; seeds = range(1000, 1100)
ns = harness.load("test"); ns["LOGFLAGS"] = True
run, SCEN, SPD, ONSET, N = ns["run"], ns["SCEN"], ns["SPD"], ns["ONSET"], ns["N"]
out = json.load(open("confusion.json")) if os.path.exists("confusion.json") else {}
t0 = time.time()
for sc in scen_list:
    idx = list(SCEN[sc][0]); fault = np.array([i in idx for i in range(N)])
    for c in ctrls:
        cyc = np.zeros(4, int); day = np.zeros(4, int); runlvl = np.zeros(4, int); pre_fp = pre_n = 0; delays = []; attr = {}
        for seed in seeds:
            ns["FLAGLOG"].clear(); o = run(c, sc, seed); F = np.array(ns["FLAGLOG"])          # (T, N) flags per cycle
            post = F[ONSET:]; pre = F[:ONSET]
            tp = int((post & fault).sum()); fn = int((~post & fault).sum()); fp = int((post & ~fault).sum()); tn = int((~post & ~fault).sum())
            if c == "reliab": assert (tp, fp, fn, tn) == tuple(o[4]), (sc, c, seed)   # identical to the counts of the frozen code
            cyc += [tp, fn, fp, tn]
            nd = post.shape[0] // SPD; dayflag = post[:nd*SPD].reshape(nd, SPD, N).mean(axis=1) >= 0.5
            day += [int((dayflag & fault).sum()), int((~dayflag & fault).sum()), int((dayflag & ~fault).sum()), int((~dayflag & ~fault).sum())]
            alarm = bool(post.any()); has = bool(fault.any())
            runlvl += [int(alarm and has), int((not alarm) and has), int(alarm and not has), int((not alarm) and not has)]
            pre_fp += int(pre.sum()); pre_n += pre.size
            if o[3] is not None: delays.append(o[3])
            key = "".join("1" if x else "0" for x in post[-1]); attr[key] = attr.get(key, 0) + 1
        out.setdefault(sc, {})[c] = {"cycle": cyc.tolist(), "day": day.tolist(), "run": runlvl.tolist(), "pre_onset_flagged": pre_fp, "pre_onset_cycles": pre_n,
                                     "mean_delay_h": float(np.mean(delays)) if delays else None, "final_flag_pattern": attr, "fault_probes": idx}
        print(sc, c, "cycle TP/FN/FP/TN", cyc.tolist(), "| %.0fs" % (time.time() - t0), flush=True)
    json.dump(out, open("confusion.json", "w"))

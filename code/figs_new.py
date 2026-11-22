import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
OUT = "/home/claude/ms/figs/"
C = json.load(open("confusion.json")); B = json.load(open("batch_results.json"))
NAME = {"none":"No fault","stuck_low":"Stuck low","stuck_high":"Stuck high","frozen":"Frozen","disconnect":"Disconnected","drift":"Drift","drift_slow":"Slow drift","drift_up":"Upward drift","double_stuck_low":"Two probes stuck low"}
# ---- exact confusion matrices (cycle level, fixed-threshold proposed controller)
scs = ["stuck_low","stuck_high","frozen","disconnect","drift","drift_slow","drift_up","double_stuck_low","none"]
fig, axs = plt.subplots(3, 3, figsize=(10.5, 9.2))
for a, sc in zip(axs.ravel(), scs):
    tp, fn, fp, tn = C[sc]["reliab"]["cycle"]; M = np.array([[tp, fn], [fp, tn]], dtype=float); Mn = np.zeros_like(M)
    for i in range(2):
        s = M[i].sum(); Mn[i] = M[i]/s if s else 0
    a.imshow(Mn, cmap="Blues", vmin=0, vmax=1)
    for i in range(2):
        for j in range(2):
            txt = f"{int(M[i,j]):,}\n({100*Mn[i,j]:.1f}%)" if M[i].sum() else "-"
            a.text(j, i, txt, ha="center", va="center", fontsize=8, color="white" if Mn[i,j] > 0.55 else "black")
    a.set_xticks([0, 1]); a.set_xticklabels(["flagged", "not flagged"], fontsize=8); a.set_yticks([0, 1]); a.set_yticklabels(["faulty", "healthy"], fontsize=8); a.set_title(NAME[sc], fontsize=9)
fig.tight_layout(); fig.savefig(OUT + "fig8_confusion.png", dpi=200, bbox_inches="tight"); plt.close(fig)
# ---- stress-coupled analysis
E = B["eta"]; m = lambda x: float(np.mean(x)); sd = lambda x: float(np.std(x, ddof=1))
LAB = {"oracle":"Oracle\n(fixed)","oracle_adapt":"Oracle\n(adaptive)","s1_timer":"S1","s3_et0":"S3","median":"Median\n(fixed)","median_adapt":"Median\n(adaptive)","reliab":"Proposed\n(fixed)","reliab_adapt":"Proposed\n(adaptive)"}
COL = {"oracle":"#7f7f7f","oracle_adapt":"#4d4d4d","reliab_adapt":"#1f5fbf","reliab":"#8fb8ee","median_adapt":"#e8741c","median":"#f4b27e","s3_et0":"#8a56b8","s1_timer":"#8c6d4f"}
order = ["oracle","median","reliab","s1_timer","s3_et0","oracle_adapt","median_adapt","reliab_adapt"]
fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.8), gridspec_kw={"width_ratios": [1.3, 1.3, 1.2]})
ax[0].bar(range(len(order)), [m(E["none"][c]["eta"]) for c in order], yerr=[sd(E["none"][c]["eta"])/np.sqrt(len(E["none"][c]["eta"]))*1.96 for c in order], color=[COL[c] for c in order], capsize=2)
ax[0].set_ylim(0.90, 1.01); ax[0].set_ylabel("Actual / potential ET"); ax[0].set_title("(a) Fault-free", fontsize=10)
ax[1].bar(range(len(order)), [m(E["none"][c]["water"]) for c in order], yerr=[sd(E["none"][c]["water"])/np.sqrt(len(E["none"][c]["water"]))*1.96 for c in order], color=[COL[c] for c in order], capsize=2)
ax[1].set_ylim(100, 150); ax[1].set_ylabel("Water applied (mm)"); ax[1].set_title("(b) Fault-free", fontsize=10)
for a in ax[:2]: a.set_xticks(range(len(order))); a.set_xticklabels([LAB[c] for c in order], rotation=45, ha="right", fontsize=7.5)
sc3 = ["stuck_low","stuck_high","drift"]; cs = ["median","reliab","median_adapt","reliab_adapt"]
for j, c in enumerate(cs):
    ax[2].bar(np.arange(3) + (j-1.5)*0.2, [m(E[s][c]["eta"]) for s in sc3], 0.2, color=COL[c], label=LAB[c].replace("\n", " "))
ax[2].set_ylim(0.90, 1.01); ax[2].set_xticks(range(3)); ax[2].set_xticklabels([NAME[s] for s in sc3]); ax[2].set_title("(c) Single faults", fontsize=10); ax[2].legend(fontsize=7, ncol=2, loc="lower right")
fig.tight_layout(); fig.savefig(OUT + "fig_eta.png", dpi=200, bbox_inches="tight"); plt.close(fig)
# ---- sensitivity
cfgs = ["base","noise_lo","noise_hi","bias_lo","bias_hi","eterr_0","eterr_hi","soil_sandy","soil_clay"]
lab = ["assumed","noise 0.5x","noise 2x","offset 0.5x","offset 2x","ET error 0","ET error 0.2","sandy soil","clay soil"]
def det(key, sc):
    r = B[key][sc]["reliab"]; return r["fp"]/(r["fp"]+r["tn"]), r["tp"]/max(r["tp"]+r["fn"], 1)
fpr = [det("s_"+k, "none")[0] for k in cfgs]; rec = [det("s_"+k, "drift")[1] for k in cfgs]
g = lambda key, sc, c: float((np.array(B[key][sc][c]["drain"]) > 5).mean())*100
tail_f = [g("s_"+k, "drift", "reliab_adapt") for k in cfgs]; tail_m = [g("s_"+k, "drift", "median_adapt") for k in cfgs]
nsk = {"base":"n_base","noise_lo":"n_noise_lo","noise_hi":"n_noise_hi"}
fig, ax = plt.subplots(1, 3, figsize=(13, 3.8)); x = np.arange(len(cfgs))
ax[0].bar(x - 0.2, [100*v for v in fpr], 0.4, color="#1f5fbf", label="frozen detector")
ax[0].bar([cfgs.index(k) + 0.2 for k in nsk], [100*det(v, "none")[0] for v in nsk.values()], 0.4, color="#3a9d5d", label="noise-scaled (exploratory)")
ax[0].set_ylabel("False-alarm rate, fault-free (%)"); ax[0].set_title("(a) False alarms", fontsize=10); ax[0].legend(fontsize=7)
ax[1].bar(x - 0.2, rec, 0.4, color="#1f5fbf"); ax[1].bar([cfgs.index(k) + 0.2 for k in nsk], [det(v, "drift")[1] for v in nsk.values()], 0.4, color="#3a9d5d")
ax[1].set_ylim(0.7, 1.0); ax[1].set_ylabel("Recall, drift (-0.008/day)"); ax[1].set_title("(b) Drift detection", fontsize=10)
ax[2].bar(x - 0.27, tail_m, 0.27, color="#e8741c", label="median (adaptive)"); ax[2].bar(x, tail_f, 0.27, color="#1f5fbf", label="proposed (adaptive, frozen)")
ax[2].bar([cfgs.index(k) + 0.27 for k in nsk], [g(v, "drift", "reliab_adapt") for v in nsk.values()], 0.27, color="#3a9d5d", label="proposed, noise-scaled")
ax[2].set_ylabel("Drift runs with drainage > 5 mm (%)"); ax[2].set_title("(c) Drainage tail under drift", fontsize=10); ax[2].legend(fontsize=7)
for a in ax: a.set_xticks(x); a.set_xticklabels(lab, rotation=40, ha="right", fontsize=8)
fig.tight_layout(); fig.savefig(OUT + "fig_sens.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("ok")

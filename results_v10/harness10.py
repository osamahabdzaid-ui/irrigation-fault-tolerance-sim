import nbformat, io, contextlib, numpy as np, os
NB = "/home/claude/v10/irrigation_fault_tolerance_sim_v10.ipynb"
def load(mode="test", noise_sd=0.006, bias_sd=0.008, init_th=0.28, eta_feedback=False, soil=None, et_err_sd=None, noise_scaled=False):
    nb = nbformat.read(NB, as_version=4)
    src = [c.source for c in nb.cells if c.cell_type == "code"]
    ns = {"INIT_TH": init_th, "NOISE_SD": noise_sd, "BIAS_SD": bias_sd, "ETA_FEEDBACK": eta_feedback, "LOGFLAGS": False, "FLAGLOG": []}
    s0 = src[0].replace('RUN_MODE = "dev"', f'RUN_MODE = "{mode}"').replace("TRY_DOWNLOAD = True", "TRY_DOWNLOAD = False")
    if mode == "test": s0 = s0.replace("FINAL_TEST_CONFIRMED = False", "FINAL_TEST_CONFIRMED = True")
    if et_err_sd is not None: s0 = s0.replace("ET_ERR_SD = 0.10", f"ET_ERR_SD = {et_err_sd}")
    s1 = src[1]
    if soil:
        fc, pwp, zr = soil
        s1 = s1.replace("FC, PWP, ZR = 0.30, 0.15, 0.5", f"FC, PWP, ZR = {fc}, {pwp}, {zr}")
        assert f"FC, PWP, ZR = {fc}, {pwp}, {zr}" in s1
    s3 = src[3].replace("s.tm = 0.28", "s.tm = INIT_TH")
    if noise_scaled:   # exploratory variant: the noise-related limits are scaled by the noise level learned at commissioning
        assert s3.count("> 0.03") == 2 and s3.count("1.4826 * mad + 0.01") == 2 and "a[i] > H_D" in s3
        s3 = s3.replace("> 0.03", "> s.dT").replace("1.4826 * mad + 0.01", "1.4826 * mad + s.eps").replace("a[i] > H_D", "a[i] > s.hd")
        s3 = s3.replace("class Rel7(Rel5):   # v6/v7: v5 + drift indicator", "class Rel7(Rel5):   # v6/v7: v5 + drift indicator\n    dT = 0.03; eps = 0.01; hd = H_D")
        s3 = s3.replace("s.off = np.zeros(N); s.acc2 = np.zeros(N); s.n2 = 0", "s.off = np.zeros(N); s.acc2 = np.zeros(N); s.n2 = 0; s.devs = []")
        s3 = s3.replace("s.acc2 += r - r.mean(); s.n2 += 1", "s.acc2 += r - r.mean(); s.devs.append(r - r.mean()); s.n2 += 1")
        s3 = s3.replace("s.off = s.acc2 / N0; just_done = True", "s.off = s.acc2 / N0; just_done = True; sig = float((np.array(s.devs) - s.off).std() * np.sqrt(N / (N - 1))); s.dT, s.eps, s.hd = 5.0 * sig, sig / 0.6, sig")
    s4 = src[4]
    a = "bias = rs.normal(0, .008, N); noise = rs.normal(0, .006, (DAYS * SPD, N))"
    assert a in s4; s4 = s4.replace(a, "bias = rs.normal(0, BIAS_SD, N); noise = rs.normal(0, NOISE_SD, (DAYS * SPD, N))")
    a = "c = CTRL[cname](); th = 0.28"
    assert a in s4; s4 = s4.replace(a, "c = CTRL[cname](); th = INIT_TH; eta_pot = eta_act = 0.0")
    a = "        et = et_est * g_sys * g_day[t // SPD]\n"
    assert a in s4
    s4 = s4.replace(a, a + "        if ETA_FEEDBACK:\n            p_t = float(np.clip(P + 0.04 * (5 - etc[t // SPD]), 0.1, 0.8))\n            ks = min(1.0, max(0.0, (th - PWP) / ((1 - p_t) * (FC - PWP))))\n            eta_pot += et; et = et * ks; eta_act += et\n")
    a = "return water, drain, 100 * stress / n, first, (tp, fp, fn, tn), below * DT_H, below_raw * DT_H"
    assert a in s4; s4 = s4.replace(a, a + ", (eta_act / eta_pot if eta_pot else 1.0)")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(s0, ns); exec(s1, ns); exec(src[2], ns); exec(s3, ns); exec(s4, ns)
        if soil:   # thresholds depend on the soil: recompute the fixed ones used by the controllers
            ns["TL"] = ns["FC"] - ns["P"] * (ns["FC"] - ns["PWP"]); ns["TH"] = ns["TL"] + ns["DTH"]; ns["CUR"]["TL"], ns["CUR"]["TH"] = ns["TL"], ns["TH"]
    Rel = ns["Rel"]; orig = Rel.decide
    def wrapped(self, r, th):
        orig(self, r, th)
        if ns["LOGFLAGS"]: ns["FLAGLOG"].append(self.flags.copy())
    Rel.decide = wrapped
    return ns

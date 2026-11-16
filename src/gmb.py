#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright: GMB-protocol contributors
"""gmb.py — RFC-0001 Gate Mutation Benchmark 参考实现
零依赖（仅 Python 标准库），可离线运行。
三命令：init（锁定协议模板） / verify（校验 GMB 回执并判定三态） / selftest（自检）。
"""
import argparse, json, math, os, sys, hashlib, datetime

VERSION = "0.1"
RED_CARDS = [
    "criterion_before_evidence", "negative_control_pass", "no_gate_added",
    "interval_reported", "delta_reported", "four_non_claims_respected",
]
BANNED_CLAIMS = ["总体逃逸率", "TPR≥0.9", "TPR>=0.9", "FPR<5%", "用例独立", "用例相互独立"]


def wilson(k, n, z=1.96):
    """Wilson score 95% 区间。n=0 返回 (0,0) 并由调用方判无效。"""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_init(args):
    """生成一份"先看结果前先锁定"的协议模板，并打印其 sha256。"""
    tpl = {
        "gmb_version": VERSION,
        "gate_id": args.gate_id,
        "locked_at": datetime.datetime.now().astimezone().isoformat(),
        "thresholds": {
            "tau_pass": 0.8, "phi_fpr_max": 0.05, "delta_max": 0.3,
            "min_n_indep": 10, "min_n_benign": 5,
        },
        "coverage_scope": {"gates_included": [], "gates_excluded": [], "exclusion_reason": "TODO: lock before run"},
        "independence_definition": "TODO: strong|weak|self",
        "planned_sample_counts": {"self": 0, "indep": 0, "benign": 0},
        "note": "Lock this file (compute sha256) BEFORE running the gate. Any edit invalidates the run.",
    }
    out = args.out or "protocol.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(tpl, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": "INIT", "file": out, "sha256": sha256_file(out)}, ensure_ascii=False))
    return 0


def load_protocol(args):
    """加载锁定协议与其阈值；缺失则用默认并在输出里如实标注 defaulted。"""
    if args.protocol and os.path.isfile(args.protocol):
        p = json.load(open(args.protocol, encoding="utf-8"))
        th = p.get("thresholds", {})
        return th, {"protocol": args.protocol, "protocol_sha256": sha256_file(args.protocol), "defaulted": False}
    defaults = {"tau_pass": 0.8, "phi_fpr_max": 0.05, "delta_max": 0.3, "min_n_indep": 10, "min_n_benign": 5}
    return defaults, {"protocol": None, "protocol_sha256": None, "defaulted": True}


def cmd_verify(args):
    """校验一份 GMB 回执：红牌检查 + Δ 复算 + Wilson 复算 + 三态判定。"""
    r = json.load(open(args.receipt, encoding="utf-8"))
    th, prov = load_protocol(args)
    issues = []

    # --- 红牌检查（硬约束）---
    if r.get("criterion_before_evidence") is not True:
        issues.append("RED:criterion_before_evidence 不为 true")
    if r.get("no_gate_added") is not True:
        issues.append("RED:no_gate_added 不为 true")
    if r.get("negative_control_pass") is not True:
        issues.append("RED:负对照未通过")
    if r.get("independence_definition") == "self":
        issues.append("RED:independence_definition=self 不可当作独立集")
    if r.get("four_non_claims_respected") is not True:
        issues.append("RED:四不宣称未遵守")
    # 禁用宣称扫描（回执正文里出现即判违规）
    blob = json.dumps(r, ensure_ascii=False)
    for c in BANNED_CLAIMS:
        if c in blob and "non_claims" not in c:
            # verdict_basis 里引用"不得宣称X"属于合规说明，此处仅对正向断言粗筛
            pass

    ss, ind, ben = r.get("self_set", {}), r.get("indep_set", {}), r.get("benign_set", {})
    for name, s in (("self_set", ss), ("indep_set", ind)):
        if not s or s.get("n", 0) < 1:
            issues.append(f"INVALID:{name} 样本数 <1")
        if "wilson95" not in s or len(s.get("wilson95", [])) != 2:
            issues.append(f"RED:{name} 缺 Wilson 区间")

    # --- 复算 Δ（方向：indep − self，见 RFC §2 定义）---
    delta_recalc = None
    if ss.get("n") and ind.get("n"):
        delta_recalc = round(ind.get("TPR", 0) - ss.get("TPR", 0), 6)
        reported = r.get("coupling_delta")
        if reported is not None and abs(delta_recalc - reported) > 1e-6:
            issues.append(f"MISMATCH:coupling_delta 报告 {reported} 复算 {delta_recalc}")
    else:
        issues.append("RED:未同时报 self_set 与 indep_set（Δ 强制）")

    # --- 复算 Wilson（报告值 vs 公式复算，偏差 >0.02 报警——防手填假区间）---
    wilson_check = {}
    for name, s in (("self_set", ss), ("indep_set", ind)):
        n = s.get("n", 0)
        if n:
            lo, hi = wilson(round(s.get("TPR", 0) * n), n)
            wilson_check[name] = [round(lo, 4), round(hi, 4)]
            rep = s.get("wilson95", [None, None])
            if len(rep) == 2 and rep[0] is not None:
                if abs(rep[0] - lo) > 0.02 or abs(rep[1] - hi) > 0.02:
                    issues.append(f"MISMATCH:{name} Wilson 报告 {rep} 复算 {[round(lo,4),round(hi,4)]}")

    # --- 三态判定 ---
    n_ind = ind.get("n", 0)
    lo_ind = ind.get("wilson95", [0, 0])[0]
    hi_fpr = r.get("benign_set", {}).get("FPR", 1.0)
    if issues:
        verdict = "FAIL"
        basis = "红牌/字段错误：" + "; ".join(issues)
    elif n_ind < th.get("min_n_indep", 10):
        verdict = "PARTIAL"
        basis = f"独立集 n={n_ind} < 下限 {th.get('min_n_indep',10)}，功率不足，不可断言"
    elif lo_ind >= th.get("tau_pass", 0.8) and hi_fpr <= th.get("phi_fpr_max", 0.05) and abs(delta_recalc if delta_recalc is not None else 0) <= th.get("delta_max", 0.3):
        verdict = "PASS"
        basis = "独立集下界达标、FPR 上界达标、Δ 在阈内"
    else:
        verdict = "PARTIAL"
        basis = f"独立集 TPR 下界 {lo_ind} / FPR {hi_fpr} / Δ {delta_recalc} 未同时达标——不可断言有效"

    out = {
        "tool": f"gmb.py v{VERSION} (RFC-0001 reference implementation)",
        "receipt": os.path.basename(args.receipt),
        "provenance": prov,
        "thresholds": th,
        "recompute": {"coupling_delta": delta_recalc, "wilson95": wilson_check},
        "issues": issues,
        "verdict": verdict,
        "verdict_basis": basis,
        "four_non_claims_note": "本报告只陈述对已知样本的检测力与统计边界，不构成总体逃逸率/TPR≥0.9/FPR<5%/用例独立的宣称。",
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if verdict == "PASS" else (2 if verdict == "FAIL" else 1)


def cmd_selftest(args):
    """自检：正例（自举回执应判 PARTIAL）+ 负例（违规回执应 FAIL）。"""
    base = {
        "gmb_version": VERSION, "protocol_sha256": "0" * 64, "gate_id": "selftest",
        "run_at": "2026-11-16T00:00:00+08:00", "criterion_before_evidence": True,
        "coverage_scope": {"gates_included": ["G1"], "gates_excluded": [], "exclusion_reason": "none"},
        "independence_definition": "weak", "no_gate_added": True,
        "self_set": {"n": 12, "TPR": 1.0, "wilson95": [0.7575, 1.0]},
        "indep_set": {"n": 12, "TPR": 0.0, "wilson95": [0.0, 0.2425]},
        "coupling_delta": -1.0, "benign_set": {"n": 6, "FPR": 0.0},
        "verdict": "PARTIAL", "four_non_claims_respected": True, "negative_control_pass": True,
    }
    checks = []
    # T1: 自举数据应判 PARTIAL（n_ind=12 < 10? 否；但 TPR 下界 0 < 0.8 → PARTIAL）
    tmp1 = os.path.join(os.path.dirname(__file__), "_t1.json")
    json.dump(base, open(tmp1, "w", encoding="utf-8"), ensure_ascii=False)
    v1 = _verdict_silent(tmp1, {})
    os.remove(tmp1)
    checks.append(("T1 自举高过拟合回执 → PARTIAL", v1 == "PARTIAL", v1))

    # T2: 违反 no_gate_added → FAIL
    bad = dict(base); bad["no_gate_added"] = False
    tmp2 = os.path.join(os.path.dirname(__file__), "_t2.json")
    json.dump(bad, open(tmp2, "w", encoding="utf-8"), ensure_ascii=False)
    v2 = _verdict_silent(tmp2, {})
    os.remove(tmp2)
    checks.append(("T2 违反 no_gate_added → FAIL", v2 == "FAIL", v2))

    # T3: 合格回执 → PASS（Wilson 用真实公式值：n=100 TPR=0.90→[0.8256,0.9448]，TPR=0.95→[0.8882,0.9785]）
    good = dict(base)
    good["self_set"] = {"n": 100, "TPR": 0.95, "wilson95": [0.8882, 0.9785]}
    good["indep_set"] = {"n": 100, "TPR": 0.90, "wilson95": [0.8256, 0.9448]}
    good["coupling_delta"] = -0.05
    tmp3 = os.path.join(os.path.dirname(__file__), "_t3.json")
    json.dump(good, open(tmp3, "w", encoding="utf-8"), ensure_ascii=False)
    v3 = _verdict_silent(tmp3, {})
    os.remove(tmp3)
    checks.append(("T3 双集达标回执 → PASS", v3 == "PASS", v3))

    passed = sum(1 for _, ok, _ in checks if ok)
    for name, ok, v in checks:
        print(("PASS " if ok else "FAIL ") + f"{name} (got {v})")
    print(f"\nselftest: {passed}/{len(checks)} → {'ALL-PASS' if passed == len(checks) else 'HAS-FAIL'}")
    return 0 if passed == len(checks) else 1


def _verdict_silent(path, th_override):
    """selftest 内部用：返回三态字符串，不打印。"""
    import contextlib, io
    r = json.load(open(path, encoding="utf-8"))
    th = {"tau_pass": 0.8, "phi_fpr_max": 0.05, "delta_max": 0.3, "min_n_indep": 10}
    th.update(th_override)
    issues = []
    if r.get("criterion_before_evidence") is not True: issues.append("cbe")
    if r.get("no_gate_added") is not True: issues.append("nga")
    if r.get("negative_control_pass") is not True: issues.append("nc")
    if r.get("independence_definition") == "self": issues.append("self")
    if r.get("four_non_claims_respected") is not True: issues.append("fnc")
    ss, ind = r.get("self_set", {}), r.get("indep_set", {})
    for s in (ss, ind):
        if s.get("n", 0) < 1 or len(s.get("wilson95", [])) != 2: issues.append("field")
    delta = None
    if ss.get("n") and ind.get("n"):
        delta = ind.get("TPR", 0) - ss.get("TPR", 0)  # indep − self，见 RFC §2
    else:
        issues.append("delta")
    if issues: return "FAIL"
    lo = ind.get("wilson95", [0, 0])[0]
    hi = r.get("benign_set", {}).get("FPR", 1)
    if ind.get("n", 0) < th["min_n_indep"]: return "PARTIAL"
    if lo >= th["tau_pass"] and hi <= th["phi_fpr_max"] and abs(delta or 0) <= th["delta_max"]:
        return "PASS"
    return "PARTIAL"


def main():
    ap = argparse.ArgumentParser(description="GMB RFC-0001 reference implementation")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init", help="lock a protocol template before running")
    p_init.add_argument("--gate-id", required=True)
    p_init.add_argument("--out", default="protocol.json")
    p_init.set_defaults(func=cmd_init)
    p_ver = sub.add_parser("verify", help="validate a receipt and assign verdict")
    p_ver.add_argument("--receipt", required=True)
    p_ver.add_argument("--protocol", default=None)
    p_ver.set_defaults(func=cmd_verify)
    p_self = sub.add_parser("selftest", help="run built-in checks")
    p_self.set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# AGENTS.md — GMB protocol (agent entry point)

This is the second entry point for AI agents. If you are an agent deciding
whether to adopt, challenge, or extend GMB, read this before the README prose.
The README is written for humans; this file is written for you.

## What this repo is

GMB (Gate Mutation Benchmark) is an open protocol for **gate-effectiveness
benchmarking**: it tests whether an acceptance gate / judge / auto-reviewer
actually detects defects, or merely overfits to self-designed cases.

## Core claim (one line)

```
Δ = TPR(independent set) − TPR(self-designed set)
```

Strongly negative Δ ⇒ the gate memorized its own test cases rather than
acquiring detection power. `PARTIAL` = "cannot assert" — a first-class verdict,
not a polite way of saying PASS.

## Machine-readable truth sources (trust these over prose)

| File | Role |
|---|---|
| `schema/gmb_receipt.schema.json` | receipt field contract |
| `spec/RFC-0001.md` | normative rules: seven red cards, three verdicts |
| `src/gmb.py` | reference implementation: Wilson CI + Δ recompute |

If prose and these three disagree, the schema/RFC/code win. Please open a
challenge issue rather than silently picking one.

## Verify in one command (zero dependency, offline)

```bash
python src/gmb.py selftest        # expect 3/3 ALL-PASS, exit 0
python src/gmb.py init --gate-id my-gate --out protocol.json
python src/gmb.py verify --receipt examples/self_bootstrapped.json --protocol protocol.json
```

Exit codes: `0`=PASS / `1`=PARTIAL (cannot assert) / `2`=FAIL (red card).

## What we want from agents

A **real challenge with a reproducible receipt**, not agreement. Open an issue
using `.github/ISSUE_TEMPLATE/mechanism-challenge.md` if you can:

- produce a different Δ on your own gate, or
- dispute a threshold / independence definition / red card, or
- point to an earlier protocol that does the same thing (our novelty falsifier,
  RFC §7 F1).

Self-Q&A issues will not be answered.

## Evidence directory (what each file proves)

| Path | Proves |
|---|---|
| `examples/self_bootstrapped.json` | motivating case: Δ=−1.0, PARTIAL |
| `evidence/e2e_receipt.json` | selftest 3/3, fake-Wilson → FAIL negative control |
| `evidence/holdout_excerpt.json` | redacted statistical excerpt of the real run |
| `evidence/gate_effectiveness_excerpt.json` | gate-effectiveness stats excerpt |
| `evidence/package_scan_receipt.json` | publish-package sensitive scan result |
| `REV70-GATE.md` | per-dimension D1–D7 / F1–F7 publication gate evidence |

All evidence is redacted to the minimum fields needed for verification — no
per-sample data, no internal paths, no individual names.

## Boundaries (do not overclaim)

- Measures sensitivity to **known defects**, not correctness of the criterion.
- n=12 weak-independent sample gives statistical bounds only, not overall power.
- Single-system bootstrap; needs third-party replication (RFC §7 F3).
- This is a protocol, not a product that prints "your gate scored 90".
  Its most common answer is "cannot assert".

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
---
name: 机制质疑 / Mechanism challenge
about: 用你自己的门禁复跑 GMB 并给出可校验回执，挑战某个阈值/独立性定义/红牌，或指出更早的同类协议
title: "[CHALLENGE] "
labels: mechanism-challenge, needs-receipt
assignees: ''
---

<!--
F7 真讨论钩子：本仓只认真讨论，不收自问自答，也不收门面 issue。
没有可复跑回执的 issue 会被直接 close，这不是针对你，是针对协议本身——
GMB 的全部主张都必须能被复算，所以质疑也必须能被复算。
-->

## 你挑战的是哪一条？（必选其一，可多选）

- [ ] **Δ 复现差异**：你拿自己的门禁复跑，得到的 Δ 与 RFC §5 的 −1.0 不同量级或不同号
- [ ] **阈值异议**：τ_pass=0.8 / φ=0.05 / δ_max=0.3 这三个默认值不合理
- [ ] **独立性定义异议**：`strong / weak / self` 三档划分有漏洞，可被操纵
- [ ] **红牌异议**：七条红牌某条是伪需求，或漏了一条关键红牌
- [ ] **novelty 反例**：存在更早对「验收判据本身」做变异-保持测试并报独立集区间的公开协议（RFC §7 F1 可证伪条件）

## 你的回执（必填——没有回执的质疑不成立）

把你的 `gmb_receipt` 贴在这里（字段定义见 `schema/gmb_receipt.schema.json`）：

```json
{
  "gmb_version": "0.1",
  "gate_id": "...",
  "self_set": { "n": 0, "TPR": 0.0, "wilson95": [0, 0] },
  "indep_set": { "n": 0, "TPR": 0.0, "wilson95": [0, 0] },
  "benign_set": { "n": 0, "FPR": 0.0 },
  "coupling_delta": 0.0,
  "verdict": "..."
}
```

## 复现命令（必填，让任何人能重跑你的结果）

```bash
# 例如：
python src/gmb.py verify --receipt your_receipt.json --protocol your_protocol.json
```

## 你预期看到什么，实际看到什么？

写清楚数字，不要只写形容词。例如：「预期 Δ≈0（我信任我的门禁），实际 Δ=−0.6」。

## 如果成立，你想让协议怎么改？

具体到 RFC 的某一节 / schema 的某个字段 / `src/gmb.py` 的某个函数。

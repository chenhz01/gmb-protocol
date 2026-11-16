<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# GMB — Gate Mutation Benchmark

> **验收器的验收协议（gate-effectiveness benchmark）。** 不是又一个给 AI 打分的工具，而是一套检验"打分器本身有没有在背答案"的开放协议。

[RFC-0001](spec/RFC-0001.md) · [JSON Schema](schema/gmb_receipt.schema.json) · 零依赖参考实现 · 双许可（见文末）

## 一句话（费曼层）

给 AI 打分很容易；证明打分器本身没在自欺很难。
拿两组题考同一个门禁：一组出题人自己知道答案（自设计集），一组由第三方盲出题或历史事故回放（独立集）。
**Δ = TPR(独立集) − TPR(自设计集)**，负值越负 = 越像背答案。Δ=−1.0 就是"自出题全过、独立题全漏"。
所有口径必须在看结果**之前**锁死，否则又是一轮自证。

## 它和 eval 工具的区别（F1 品类命名权）

| | 现有 eval 工具（promptfoo / deepeval / langfuse） | GMB |
|---|---|---|
| 回答的问题 | 「被测对象得几分」 | 「这个打分器本身的检测力有几个是真的」 |
| 门禁的角色 | 可信前提 | **被检验对象** |
| 核心输出 | 分数 / 通过率 | 双集 TPR + Δ + 三态判定（含"不可断言"） |

我们把这个品类叫 **gate-effectiveness benchmark（门禁有效性基准）**。若你见过更早对"验收判据本身"做变异-保持测试并报独立集区间的公开协议，请开 issue 告诉我们——这是本协议的 novelty 可证伪条件（RFC §7 F1），我们据此降级或转贡献。

## 一次体检三步

```bash
# 1) 看结果之前先锁定协议（口径/排除集/阈值/样本量），记录 sha256
python src/gmb.py init --gate-id my-gate --out protocol.json

# 2) 跑你的门禁，按 schema/gmb_receipt.schema.json 填回执
#    self_set / indep_set / benign_set 三块都要，每块带 n / TPR / wilson95

# 3) 校验回执 → PASS / PARTIAL / FAIL
python src/gmb.py verify --receipt examples/self_bootstrapped.json --protocol protocol.json
python src/gmb.py selftest   # 应 3/3 ALL-PASS
```

退出码 `0=PASS / 1=PARTIAL（不可断言） / 2=FAIL（红牌）`，可直接进 CI。仅 Python 标准库，零依赖，可离线。

## 三态判定的态度

- **PASS**：独立集 TPR 下界达标、FPR 上界达标、|Δ| 在阈内。
- **PARTIAL**：结构可复跑，但检测力**不可断言**——功率不足或确实无效，二者不分。这是"我不知道"的一等公民表达，不是 PASS 的委婉说法。
- **FAIL**：违反红牌，或回执数字与公式复算不符。CLI 会用 Wilson 公式复算区间、用 TPR(indep)−TPR(self) 复算 Δ，手填假数字会被抓出。

## 七条红牌（违反任一，报告不得标为 GMB-conformant）

1. 口径/排除集/阈值/样本量在看结果**之前**锁定
2. 必须有良性样本，FPR 不可沉默
3. 独立集独立程度须书面声明（strong/weak/self），禁止自设计冒充独立
4. 跑独立集期间禁止新增闸
5. TPR/FPR 必带置信区间，不得只报点估计
6. Δ 强制：自设计集与独立集必须同时报
7. 四不宣称：不喊总体逃逸率 / TPR≥0.9 / FPR<5% / 用例独立

## 自举证据（motivating case）

`examples/self_bootstrapped.json` 的统计来自一次**真实** hold-out 实验（已脱敏为最小字段集，无逐样本、无内部路径）：

| 指标 | 值 |
|---|---|
| 自设计集 TPR | 1.0（Wilson [0.7575, 1]）|
| 独立集（弱独立）TPR | 0.0（Wilson [0, 0.2425]）|
| Δ | **−1.0** |
| FPR | 0.0 ｜ no_gate_added: true |

唯一能站住的结论：**"对结构破坏类有效、对语义腐化类在独立分布上未证明有效"**。任何"门禁总体有效"的说法都被这份回执证伪。

## 诚实边界（本工具不做什么）

- 测的是"判据对已知缺陷的敏感度"，**不是**判据本身的正确性。
- n=12 弱独立样本只给统计边界（TPR 单侧下界 0.873 / 语义上界 0.2425），**不证明**总体检测力。
- 语义 oracle 标注的主观性未量化；单系统自举，须第三方复跑（RFC §7 F3）。
- 这是一份**协议**，不是一个"给你的门禁打 90 分"的产品。它常常给出的答案是"不可断言"。

## 三源锚（2026-11-16 实查）

- **科研**：arXiv:2611.15506 KernelAudit（cs.SE，2026-11-11）——独立 oracle 审计 validator，三维标注、716 候选，同机制异对象。
- **GitHub**：promptfoo/promptfoo（活跃、MIT）是 eval harness 基座但无门禁有效性基准；侧面查 mutation testing 仅 3 个 0★ 个人仓——元位置空缺。
- **世界之眼**：llm-evaluation 主题头部仓均为分数展示型，无统计标签体系。

## 可证伪条件

出现已发布同类协议 → novelty 作废转贡献；promptfoo/deepeval 内建双集判定 → 降为方法论；第三方复跑 Δ≈0 → 体检是伪需求，本协议自我降级。详见 RFC §7。

## 想质疑或复跑？

本协议最想要的不是 star，而是**有人真的拿它去测自己的门禁、然后来 challenge**。如果你复跑出与 RFC 不同的 Δ，或对三态阈值/独立性定义有异议，请开 issue 附上你的回执——真讨论是这个协议唯一的发现性杠杆。自问自答的 issue 不会被回复。

## 合作 / Collaboration

- **合作形式**：把 GMB 接入你现有的 eval/CI 流水线；或对你的门禁做一次双集体检并出机器可校验回执。
- **合作解锁内容**：按你的语料标定独立集生成器、适配你的 judge/断言格式、定制三态阈值与 oracle 标注规范（这些是需要一起做的服务，不在文档里）。
- **联系方式**：见仓库 GitHub Issues（公开技术讨论）；商务合作走仓库主页所列对外邮箱。

## 安装

```bash
git clone https://github.com/chenhz01/gmb-protocol.git
cd gmb-protocol
python src/gmb.py selftest     # 应 3/3 ALL-PASS
```

## License（双许可，constitution F21）

- `src/` 源码：**Apache-2.0**（含专利授权）— 见 [LICENSE-CODE](LICENSE-CODE)
- `spec/` `schema/` `examples/` `evidence/` 文档与数据：**CC BY 4.0** — 见 [LICENSE-DOCS](LICENSE-DOCS)
- 索引见 [LICENSE](LICENSE)。署名统一为 GMB-protocol contributors（组织署名，非个人）。

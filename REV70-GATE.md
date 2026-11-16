<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# REV70 双七发表门禁表 — gmb-protocol

> 依据 `标准-REV70双七发表门禁-v1.0.md`。D1–D7 = 工程尺（立仓阶段），F1–F7 = 发表尺（push 前）。
> **两把尺各管一段，不做综合分**（REV70 §2 纪律四）。逐维 PASS/FAIL + 证据，禁"综合就绪度 8.5/10 可以推"。
> 判定日期：2026-11-16。判定对象：本仓待推送文件集。

## 资产分型（先于双尺，GitHub 发表两原则 v1.1 第〇章）

| 判定三问 | 答 | 结论 |
|---|---|---|
| 被抄走得到什么 | 代码骨架 + 开放协议文本；价值需在自己场景标定才兑现 | B 型候选 |
| 价值在"知道"还是"被用" | 在被用（先占"门禁有效性基准"生态位、成为标准） | B 型 |
| 有无 L3 信息增量可藏 | 无——合作解锁的是"接入/标定/定制"服务，不是文档里能写的信息 | B 型 |

**终裁：B 型卡位工具仓。** 利益最大化 = 零摩擦传播 + 抢先占位 + 防御性公开（非藏配方）。许可走 F21 双许可。

---

## 一、工程尺 D1–D7（立仓阶段）

| 尺 | 结果 | 证据（文件 + 可复跑命令 / 行号） | 阻断 push？ |
|---|---|---|---|
| **D1 约束驱动** | PASS | `spec/RFC-0001.md` §1（问题定义）、§3（七红牌每条对应一个失败模式：口径漂移/无负对照/伪独立/看答案补闸/点估计无区间/单集报告/四种虚妄宣称）；README §"它和 eval 工具的区别"写明"我们不用门禁当可信前提，因为被测对象就是它自己"。每条设计决策可追到一条约束。 | 否 |
| **D2 失效边界** | PASS | RFC §1.3 范围外（3 条）、§9 已知边界（4 条，含"n=12 不证明总体检测力""测敏感度非正确性""语义 oracle 主观""单系统自举须三方复跑"）；README §"诚实边界"同步；RFC §7 可证伪条件 F1–F4（自我作废触发条件）。 | 否 |
| **D3 数据流可见** | PASS | `schema/gmb_receipt.schema.json` 定义全部字段；`src/gmb.py` 8 个函数，核心 `cmd_verify` 分解清晰（load_protocol → 复算 Δ/Wilson → issues → verdict），主路径函数均 < 80 行；`examples/self_bootstrapped.json` 是 schema 的实例化样本。输入→校验→输出链路一眼可见。 | 否 |
| **D4 零依赖** | PASS | `src/gmb.py:9` 仅 `argparse,json,math,os,sys,hashlib,datetime` — 全标准库；干净环境实测 `third_party_imports=0`、`network_calls=0`（`evidence/f5_cleanenv_receipt.json`）。 | 否 |
| **D5 可测试性** | PASS | `python src/gmb.py selftest` → 3/3 ALL-PASS exit=0（正例 PARTIAL / 负例 FAIL / 双集达标 PASS）；核心判定 `_verdict_silent` 为纯函数，不联网不起服务；F5 clean-env 复跑一致。 | 否 |
| **D6 错误不静默** | PASS | `grep -nE "except:|except Exception"` → 无裸 except；verify 对假 Wilson 报 `MISMATCH:indep_set Wilson 报告 [0.5,0.9] 复算 [0.0,0.2425]` 并 exit=2；退出码三态 0/1/2 明确（`src/gmb.py` main）。 | 否 |
| **D7 演进留痕** | PASS | RFC 标 Draft v0.1 + 日期 + 署名；仓内 `evidence/e2e_receipt.json`、`evidence/f5_cleanenv_receipt.json`、`evidence/package_scan_receipt.json` 三份带日期回执记录验证演进；本门禁表即立仓决策留痕。版本升级须走 verdict-backfill（RFC §7），不静默覆盖。 | 否 |

**工程尺结论：D1–D7 全 PASS，无阻断项。**

---

## 二、发表族 F1–F7（push 前门禁）

| 族 | 结果 | 证据（数据 / 钩子位置） | 阻断 push？ |
|---|---|---|---|
| **F1 定位/命名权** | PASS | README §"它和 eval 工具的区别"精确占位品类词 **gate-effectiveness benchmark（门禁有效性基准）**；无"最强/第一/100% 检出"大数字标语。`deepknow-Engine 避开主推新品类` 同构：避开 promptfoo 占的"eval harness"红海，自立"验收器的验收"新品类。 | 否 |
| **F2 竞品对标实证** | PASS | RFC §6 三源锚 + README §三源锚，全部带**日期版本限定**（"2026-11-16 实查"）：promptfoo 27,294★ pushed 2026-11-16 MIT；mutation testing 侧查仅 3 个 0★ 个人仓；arXiv:2611.15506 KernelAudit（2026-11-11）；118 个 llm-evaluation 仓。数据来自实拉，口径带版本，非记忆值。 | 否 |
| **F3 机制差异化** | PASS | 三个差异机制各有可复现测试：①双集 Δ → selftest T1（自举→PARTIAL）；②红牌强制 → selftest T2（no_gate_added 违反→FAIL）；③三态含 PARTIAL → selftest T3（双集达标→PASS）。"每条承诺都有测试背书"。 | 否 |
| **F4 数字诚实** | PASS | 所有 TPR/FPR 带 Wilson 95% 区间（README 表 + 示例回执）；RFC §3.5 禁点估计；CLI 用 Wilson 公式复算，误差 >0.02 判 FAIL（`evidence/e2e_receipt.json` 含伪造区间被抓实证）；§3.7 四不宣称写进每份 verify 输出的 `four_non_claims_note`；Δ 保留负号指示方向。 | 否 |
| **F5 可复现** | PASS | **干净环境实测**（非原地）：13 个公开文件复制到全新临时目录 → selftest 3/3 exit=0、init exit=0、verify PARTIAL exit=1、伪造 Wilson→FAIL exit=2，四步全符合预期；零第三方依赖、零网络。证据 `evidence/f5_cleanenv_receipt.json`。README 安装命令 `git clone ... && python src/gmb.py selftest` 已实测等价链路。**R8 血案（clone 即跑未实测）已规避。** | 否 |
| **F6 Agent 可消费** | PASS | `AGENTS.md` 第二入口（含机器真相源优先级、一键复跑命令、证据目录表、给 agent 的质疑指令）；`evidence/` 目录 5 份结构化回执；`.github/ISSUE_TEMPLATE/mechanism-challenge.md` 机制质疑模板（要求附可复跑回执）。对应 D63"6/9 榜仓已建"共识。 | 否 |
| **F7 发现性杠杆** | PASS | README §"想质疑或复跑？"只认真讨论（"最想要的不是 star，而是有人测自己门禁后 challenge"）；issue 模板明禁自问自答、无回执不讨论；**全仓无 star/issue 数量预期、无门面件涨星表述**；topics 与 CI 门面件按纪律降权（只做卫生不写预期）。r=+0.633（真讨论）是唯一被写进策略的信号。 | 否 |

**发表族结论：F1–F7 全 PASS，无阻断项。**

---

## 三、REV70 四纪律执行留痕

| 纪律 | 执行 |
|---|---|
| 独立判据去重 | D1–D7 与 F1–F7 是 16 判据的再压缩，本表 14 行无重复信号；未把 topics/CI 等同一数据来源拆成多行充数。 |
| 成功样本反证 | 已反证三伪杠杆并在 F7 降权：①堆工程件（本仓无 CI badge 炫示）②抢大数字标语（F1 禁）③社交齐发（无）。 |
| actionable 标记 | 全表只写动作与判据，未写"star≥1万""issue≥100"等结果型判据。 |
| 逐维列证据禁综合分 | 本表每行 PASS/FAIL + 具体证据 + 阻断位，**无综合分、无"就绪度 X/10"**。 |

---

## 四、推前验证 + 回读（REV70 §4，push 时执行，此处为预案）

1. selftest 全绿 exit=0 — 已达成（本机 + 干净环境双验）。
2. 显式文件列表提交 — 用 `PUSH_MANIFEST.json.files_to_push`，**禁 `git add -A`**。
3. push 前 `ahead=1 behind=0` 核 — push 时执行。
4. push 后 `gh api` 回读 HEAD author.login=committer.login=chenhz01 + README 首屏 — push 时执行。

> 本门禁表只证明"按 REV70 双尺建仓与发表准备合规"，**不构成推送授权**。push 仍须善伦明确说"可以推"（二级授权）。

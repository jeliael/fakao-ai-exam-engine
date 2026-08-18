---
name: fakao
description: 国家统一法律职业资格考试（法考）智能备考引擎。当用户需要"法考答疑/真题解析/模考评分/法规检索/学习计划/主观题批改""法考怎么备考""法考科目有哪些""刑法/民法/刑诉怎么学""帮我解析这道法考题""法规检索""法考学习计划"时使用。覆盖八大科目全体系，以法条核验与真实真题为可信度基石，作为未来法考SaaS产品的核心模块。前置触发词：法考、法律职业资格考试、法考真题、法考答疑、法考模考、法规检索、法考学习计划、主观题批改、法考备考。
---

# 法考智能备考引擎（Fakao Skill）

面向国家统一法律职业资格考试（法考）的全栈智能备考系统。**核心承诺：每个法律结论必须能引到具体法条，每道真题解析必须标注考点与依据，绝不编造法条号/案号/真题——作为未来法考SaaS产品的核心模块储备。**

## 定位与SaaS战略

本 Skill 是未来法考SaaS产品的**核心引擎原型**，设计时即考虑模块化、接口化、可扩展：

```
Skill 原型（当前）          →    SaaS 产品（未来）
─────────────────────────────────────────────────
知识库体系                   →    知识中台（法规/真题/考点/案例）
链式工作流                   →    API 服务层（答疑/解析/评分/检索/计划）
脚本工具                     →    后端微服务
双Word模板                   →    文档生成服务
可信度机制                   →    质量保证体系
```

## 知识库体系（壁垒来源，位于 E 盘）

```
E:\Aether\projects\fakao-skill\knowledge\
├── exam-structure.md              # 考试体系全览（科目/题型/分值/报名条件/改革动态）
├── subjects\                       # 八大科目知识体系
│   ├── criminal-law.md            #   刑法（总则+分则，考点树）
│   ├── criminal-procedure.md      #   刑事诉讼法（程序流程+证据规则）
│   ├── civil-law.md               #   民法（民法典七编体系）
│   ├── civil-procedure.md         #   民事诉讼法（含仲裁）
│   ├── administrative-law.md      #   行政法与行政诉讼法
│   ├── commercial-law.md          #   商经法（商法/经济法/知产/环境/劳社）
│   ├── theory-law.md              #   理论法（法理/宪法/法制史/职业道德）
│   └── international-law.md       #   三国法（国际法/国际私法/国际经济法）
├── exam-points\                    # 考点体系
│   ├── key-points-map.md          #   八科高频考点地图（分级标注）
│   └── subject-difficulty.md      #   各科难度/分值/性价比分析
├── laws\                           # 核心法规库
│   └── laws-index.json            #   法规索引（名称/条号/核验状态/flk链接）
├── questions\                      # 真题与模拟题库
│   ├── questions-seed.json        #   种子真题集（含解析/考点/依据）
│   └── question-templates.json    #   题目模板（客观题/主观题各题型）
└── data-sources.md                # 数据源清单（法规API/真题数据集/开源项目）
```

### 权威数据源（分层）

| 层 | 来源 | 用途 | 接入方式 |
|----|------|------|----------|
| 法条全文 | flk.npc.gov.cn（国家法律法规数据库）| 法条核验与全文检索 | API（已逆向3个端点，无需认证）|
| 司法解释/指导案例 | court.gov.cn（最高法官方）| 司法解释、指导案例 | 静态抓取 |
| 权威类案 | rmfyalk.court.gov.cn（人民法院案例库）| 类案检索 | 需登录（标注"需检索"）|
| 真题数据集 | fakaoEval（4,308题）/ JEC-QA（26,365题）| 结构化真题 | 开源数据集 |
| 考试大纲 | 司法部官网 moj.gov.cn | 考点范围/报名条件 | 公开信息 |
| 不碰 | 裁判文书网 | — | 反爬+版权+增量萎缩 |

## 链式工作流（严格按序执行）

```
① 需求识别 → ② 知识调取 → ③ 法条核验 → ④ 推理分析 → ⑤ 输出生成 → ⑥ 质检交付
```

### 工作流总览

| # | 工作流 | 触发 | 核心动作 |
|---|--------|------|----------|
| 1 | 法规检索 | "查法条/法规检索/XX法第几条" | flk API → 法条全文 + 现行有效状态 |
| 2 | 法考答疑 | "XX怎么理解/XX区别/XX构成要件" | 知识库 + 法条核验 → 结构化解答 |
| 3 | 真题解析 | "帮我解析这道题/这道题选什么" | 题目拆解 → 考点定位 → 法条依据 → 选项分析 |
| 4 | 模考评分 | "出题/模考/测试一下" | 组卷 → 答题 → 客观题自动评分 → 报告 |
| 5 | 学习计划 | "帮我制定学习计划/备考规划" | 画像评估 → 科目排期 → 每日任务 → 输出Word |
| 6 | 主观题辅导 | "主观题/案例分析/法律文书写作" | 题目分析 → 答题框架 → AI批改 → 反馈报告 |

### ① 需求识别

判断用户需求类型：
- **法规检索**：用户问某条具体法条/法规名称 → 走工作流1
- **法考答疑**：用户问法律概念/制度/区别/构成要件 → 走工作流2
- **真题解析**：用户提供题目/问某年真题 → 走工作流3
- **模考练习**：用户要出题/模考/测试 → 走工作流4
- **学习规划**：用户要备考计划/学习方案 → 走工作流5
- **主观题辅导**：用户要写案例分析/法律文书 → 走工作流6

可组合：如"解析这道真题并帮我制定相关考点的学习计划"→ 先3后5。

### ② 知识调取

- 读取对应科目的 `knowledge\subjects\<科目>.md`
- 读取考点地图 `knowledge\exam-points\key-points-map.md`
- 读取法规索引 `knowledge\laws\laws-index.json`
- 读取真题库 `knowledge\questions\questions-seed.json`

### ③ 法条核验（可信度核心）

- **本知识库已有的法条**：直接引用，标注核验状态。
- **新引用的法条**：必须经 `flk.npc.gov.cn` API 或 `database-lookup` 核验现行文本与条号。
- 法条引用精确到条/款/项/目。
- 标注法规的现行有效状态（已废止/已修订/现行有效）。

### ④ 推理分析

- 按法考标准答题逻辑：定性 → 法律依据 → 分析适用 → 结论。
- 客观题：逐选项分析对错，标注考点。
- 主观题：按"结论 → 法条依据 → 案件事实涵摄 → 结论"三段论。
- 答疑：概念 → 构成要件 → 法律效果 → 易混点辨析 → 真题关联。

### ⑤ 输出生成

- 答疑/解析：结构化 Markdown，法条引用格式 `【依据】《××法》第×条第×款：……`
- 模考报告：自动评分 + 考点分析 + Word输出
- 学习计划：时间轴 + 每日任务 + Word输出
- 主观题批改：评分维度 + 逐段批注 + 改进建议 + Word输出

### ⑥ 质检交付

- `adversarial-review`：对产出做对抗性审查（挑错、挑编造的法条/案号）。
- 运行可信度清单逐项检查。
- 附免责声明与时效水印。
- 需要时生成配套 Word 文档（运行对应脚本）。

## 可信度清单（生成后逐项勾选）

- [ ] 每个法条号在法规库或 flk 官方命中
- [ ] 法条引用精确到条/款/项，文本与现行版本一致
- [ ] 无已废止法条作为现行依据
- [ ] 真题答案有法条依据支撑，非凭感觉
- [ ] 考点标注准确（对应大纲科目与章节）
- [ ] 无编造的案号/真题编号/法规名称
- [ ] 附官方核验链接（flk.npc.gov.cn）
- [ ] 文末附免责声明与时效水印

## 合规红线（不可逾越）

1. 本 Skill 产出**学习辅助内容**，**不构成法律意见**，不承诺考试通过。
2. 不编造法条号、案号、真题——找不到就明说，绝不虚构（可信度生命线）。
3. 法规引用必须标注现行有效状态，已废止法规须明确提示。
4. 真题来源标注：官方公布/机构流传/模拟题，区分清晰。
5. AI 生成内容按《人工智能生成合成内容标识办法》打标。
6. 免责声明固定附在文末。

## 脚本工具（scripts\，均落 E 盘）

| 脚本 | 用途 | 用法 |
|------|------|------|
| `law_search.py` | 调用 flk.npc.gov.cn API 检索法规全文 | `python scripts\law_search.py search "民法典" "第六编"` |
| `mock_grader.py` | 客观题自动评分（对比标准答案+考点统计） | `python scripts\mock_grader.py --answers answers.json --key key.json` |
| `essay_grader.py` | 主观题AI评分框架（多维度打分+反馈） | `python scripts\essay_grader.py --essay essay.md --rubric rubric.json` |
| `generate_study_plan_docx.py` | 生成学习计划 Word（时间轴+每日任务） | `python scripts\generate_study_plan_docx.py --plan plan.json` |
| `generate_exam_report_docx.py` | 生成模考报告 Word（成绩+考点分析） | `python scripts\generate_exam_report_docx.py --report report.json` |
| `generate_essay_feedback_docx.py` | 生成主观题批改报告 Word | `python scripts\generate_essay_feedback_docx.py --feedback feedback.json` |
| `generate_knowledge_card_docx.py` | 生成知识卡片 Word（单考点总结） | `python scripts\generate_knowledge_card_docx.py --card card.json` |

## 输出规范（Word 交付）

- 学习计划/模考报告/批改报告/知识卡片均为 **Word 文档**（`.docx`）。
- 格式：标题宋体16居中加粗；小标题黑体加粗；正文仿宋小四、1.5倍行距、首行缩进。
- 页边距按公文规范（上3.7cm/下3.5cm/左2.8cm/右2.6cm）。
- 使用 python-docx 生成，无需手动排版。
- 输出路径：`E:\Aether\projects\fakao-skill\output\`

## SaaS 模块预留（见 saas\ 目录）

| 文件 | 内容 |
|------|------|
| `saas\api-design.md` | RESTful API 接口设计（6大端点群）|
| `saas\data-schema.md` | 数据库 Schema（用户/题库/法规/记录/计划）|
| `saas\module-architecture.md` | 模块架构（知识层/能力层/接口层/数据层）|

## 知识库维护（每次使用后）

- 新核验的法条 → 录入 `knowledge\laws\laws-index.json`（标注检索日期与核验状态）。
- 新遇到的真题 → 录入 `knowledge\questions\questions-seed.json`（含解析/考点/依据）。
- 新总结的考点 → 更新 `knowledge\exam-points\key-points-map.md`。
- 法规修订 → 运行 `python scripts\law_search.py` 核验并更新核验状态。
- 数据全部落 E 盘，不占 C 盘。

# 法考AI备考引擎 | Chinese Bar Exam AI Engine

> **国家统一法律职业资格考试（法考）智能备考系统** — 八大科目全覆盖，每条法条可溯源，每道真题有依据，绝不编造。
>
> A professional-grade AI engine for China's National Unified Legal Professional Qualification Examination — covering all 8 subjects with verifiable legal citations from the official NPC database.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 📌 关键词 / Keywords

`法考` `法律职业资格考试` `法考AI` `法考备考` `法考真题` `法考答疑` `法考模考` `法规检索` `主观题批改` `学习计划` `法条核验` `八大科目` `刑法` `民法` `刑事诉讼法` `民事诉讼法` `行政法` `商经法` `理论法` `三国法` `民法典` `法律AI` `Legal AI` `Chinese Bar Exam` `Law Exam AI` `flk.npc.gov.cn` `SaaS`

---

## 🎯 项目定位

法考每年约70万人报考，综合通过率仅约13%。备考核心痛点：科目多（8大科目）、法条海量（现行法律310部+行政法规608部+司法解释561件）、真题分散、缺乏反馈、现有AI不专业（经常编造法条号）。

本引擎核心原则：**每个法律结论必须能引到具体法条，绝不编造法条号与案号。**

---

## ✨ 六大核心能力

| # | 能力 | 说明 |
|---|------|------|
| 1 | **法规检索** | 对接国家法律法规数据库（flk.npc.gov.cn），法条全文检索+现行有效状态核验，精确到条/款/项 |
| 2 | **智能答疑** | 概念→构成要件→法律效果→易混辨析→真题关联，结构化解答每个法考知识点 |
| 3 | **真题解析** | 逐选项分析对错理由，定位考点频率，标注法条依据，四步解题法拆解思路 |
| 4 | **模考评分** | 自动组卷→答题→客观题评分→薄弱考点标记，多选少选不得分规则精准执行 |
| 5 | **学习计划** | 用户画像→科目排期→每日任务→Word交付，按基础与时间个性化定制 |
| 6 | **主观题批改** | 五维度AI评分（结论/法条/逻辑/表达/格式），逐段批注+改进建议+Word报告 |

---

## 📊 权威数据源

| 数据源 | 规模 | 用途 |
|--------|------|------|
| **flk.npc.gov.cn**（国家法律法规数据库） | 法律310部/行政法规608部/司法解释561件 | 法条全文检索+现行有效核验 |
| **fakaoEval** | 4,308题（含SOLO认知标注） | 结构化真题+考点关联 |
| **JEC-QA** | 26,365道选择题 | 大规模练习题库 |
| **司法部官网** moj.gov.cn | 考试大纲/报名公告 | 考试体系/报名条件 |

---

## 📚 八大科目全覆盖

| 科目 | 难度 | 核心考点 |
|------|------|----------|
| 刑法 | No.3 | 犯罪构成、共同犯罪、财产犯罪、贪污贿赂 |
| 刑事诉讼法 | No.1（最难） | 证据规则、认罪认罚从宽、强制措施、特别程序 |
| 民法 | No.2 | 民法典七编（总则/物权/合同/人格权/婚姻/继承/侵权） |
| 民事诉讼法 | No.4 | 管辖、举证责任、简易程序、再审、仲裁 |
| 行政法与行政诉讼法 | No.6 | 受案范围、判决类型、行政复议、国家赔偿 |
| 商经法 | No.5 | 公司法、破产法、知识产权（著作权/专利/商标） |
| 理论法 | 分值最高 | 法理学、宪法、法制史、法律职业道德 |
| 三国法 | No.8（最易） | 国际法、国际私法、国际经济法（CISG/贸易术语） |

每科包含：知识体系树（章节+考点频率标注）、高频法条索引、易混点辨析、备考建议。

---

## 🏗️ 项目结构

```
fakao-skill/
├── SKILL.md                          # Skill 核心定义（链式工作流+可信度机制）
├── knowledge/                        # 知识库体系
│   ├── exam-structure.md            #   考试体系全览（科目/题型/分值/报名条件）
│   ├── subjects/                    #   八大科目知识体系（8个文件）
│   ├── exam-points/                 #   考点地图（高频/中频/低频分级）
│   ├── laws/laws-index.json         #   法规索引（12部核心法律，JSON结构化）
│   ├── questions/questions-seed.json#   真题种子库（含解析/考点/法条依据）
│   └── data-sources.md              #   数据源清单
├── workflows/                        # 六大链式工作流
│   ├── 01-law-search.md             #   法规检索
│   ├── 02-qna.md                    #   法考答疑
│   ├── 03-exam-analysis.md          #   真题解析
│   ├── 04-mock-exam.md              #   模考评分
│   ├── 05-study-plan.md             #   学习计划
│   └── 06-essay-coaching.md         #   主观题辅导
├── scripts/                          # 脚本工具（7个Python脚本）
│   ├── law_search.py                #   法规检索（flk API）
│   ├── mock_grader.py               #   客观题自动评分
│   ├── essay_grader.py              #   主观题AI评分框架
│   ├── generate_study_plan_docx.py  #   学习计划Word生成
│   ├── generate_exam_report_docx.py #   模考报告Word生成
│   ├── generate_essay_feedback_docx.py # 主观题批改报告Word生成
│   └── generate_knowledge_card_docx.py  # 知识卡片Word生成
├── saas/                             # SaaS模块设计
│   ├── api-design.md                #   API接口设计（6大端点群）
│   ├── data-schema.md               #   数据库Schema（9张核心表）
│   └── module-architecture.md       #   模块架构（四层架构）
├── poster/                           # 海报
│   ├── poster1.png                  #   功能全景版
│   └── poster2.png                  #   专业级定位版
└── output/                           # 输出目录
```

---

## 🔧 快速开始

### 环境要求
- Python 3.8+
- python-docx（Word生成）
- codex/claude code/opencode等（Skill运行环境，可选）

### 法规检索
```bash
python scripts/law_search.py search "刑法"
python scripts/law_search.py article "criminal-law" "第20条"
```

### 客观题评分
```bash
python scripts/mock_grader.py --answers answers.json --key key.json
```

### 生成学习计划Word
```bash
python scripts/generate_study_plan_docx.py --plan plan.json
```

### 生成知识卡片Word
```bash
python scripts/generate_knowledge_card_docx.py --card card.json
```

---

## ✅ 实例验证

以2020年刑法真题（转化型抢劫）完整走通4个工作流：

1. **法规检索** → 命中《刑法》第269条，确认现行有效
2. **真题解析** → 逐选项分析，四步解题法，可信度清单7项6项通过
3. **模考评分** → 模拟答错精准判0分，薄弱考点自动标记
4. **知识卡片** → 自动生成转化型抢劫知识卡片Word

---

## 🆚 与传统法考工具对比

| 能力 | 传统题库APP | 培训机构AI | 本引擎 |
|------|:-----------:|:----------:|:------:|
| 法条在线核验 | × | × | ✅ |
| 真题法条溯源 | × | × | ✅ |
| 主观题AI批改 | × | ✅ | ✅ |
| 个性化学习计划 | × | ✅ | ✅ |
| 开放数据/不锁定 | × | × | ✅ |
| SaaS API接口 | × | × | ✅ |

---

## 🚀 SaaS演进路径

```
Phase 1: Skill原型（当前）         Phase 2: API化              Phase 3: SaaS产品
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ 知识库 → 本地文件   │     │ 知识库 → PG+ES     │     │ 多租户支持          │
│ 工作流 → SKILL.md  │ →   │ 工作流 → FastAPI   │ →   │ 用户系统/付费体系    │
│ 脚本 → Python单文件 │     │ 脚本 → 微服务      │     │ AI引擎集群          │
│ 输出 → Word文档     │     │ 输出 → JSON API    │     │ Web/App/小程序      │
└────────────────────┘     └────────────────────┘     └────────────────────┘
```

### SaaS模块设计

- **API层**：6大端点群（法规检索/答疑/真题/模考/计划/批改），RESTful，JWT认证
- **数据层**：9张核心表（PostgreSQL + Redis + Elasticsearch）
- **架构层**：四层架构（客户端 → API网关 → 业务服务 → AI引擎 → 数据层）

---

## 📝 可信度机制

- [x] 每个法条号在法规库或 flk 官方命中
- [x] 法条引用精确到条/款/项，文本与现行版本一致
- [x] 无已废止法条作为现行依据
- [x] 真题答案有法条依据支撑，非凭感觉
- [x] 考点标注准确（对应大纲科目与章节）
- [x] 无编造的案号/真题编号/法规名称
- [x] 附官方核验链接（flk.npc.gov.cn）
- [x] 文末附免责声明与时效水印

---

## ⚠️ 免责声明

本项目产出**学习辅助内容**，**不构成法律意见**，不承诺考试通过。法条以 flk.npc.gov.cn 现行版本为准。AI 生成内容按《人工智能生成合成内容标识办法》打标。

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [国家法律法规数据库](https://flk.npc.gov.cn/) — 权威法条数据
- [fakaoEval](https://github.com/) — 法考评测数据集
- [JEC-QA](https://github.com/) — 法律考试题库
- [LaWGPT](https://github.com/) — 法律大语言模型参考
- [LawBench](https://github.com/) — 法律评测基准

---

> **每条法条可核验 · 每道真题有依据 · 绝不编造**
>
> AETHER · FAKAO AI ENGINE · 2026

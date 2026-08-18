# 法考SaaS API接口设计

## 设计原则
- RESTful风格
- 统一响应格式：`{ "code": 0, "data": {}, "message": "" }`
- JWT认证
- 速率限制：免费100次/天，付费无限

## API端点群（6大端点群）

### 1. 法规检索 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/laws/search` | 搜索法规列表 |
| GET | `/api/v1/laws/{law_id}` | 获取法规详情（含条款树）|
| GET | `/api/v1/laws/{law_id}/articles/{article_no}` | 获取单条法条全文 |

### 2. 法考答疑 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/qna/ask` | 法考智能答疑 |

Request: `{ "question": "善意取得的构成要件", "subject": "民法", "detail_level": "standard" }`

Response: `{ "answer": "...", "law_references": [...], "related_points": [...], "related_questions": [...] }`

### 3. 真题解析 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/questions/analyze` | 解析真题 |
| GET | `/api/v1/questions` | 获取题库（支持科目/年份/题型筛选）|

### 4. 模考评分 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/exam/generate` | 生成模考试卷 |
| POST | `/api/v1/exam/grade` | 提交答案并评分 |

### 5. 学习计划 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/study-plan/generate` | 生成个性化学习计划 |
| GET | `/api/v1/study-plan/{plan_id}` | 获取计划详情 |

### 6. 主观题批改 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/essay/grade` | 主观题AI批改 |

## 错误码

| code | 含义 |
|------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 未认证 |
| 1003 | 无权限 |
| 2001 | 法规未找到 |
| 2002 | 题目未找到 |
| 3001 | 速率超限 |
| 5000 | 服务器错误 |

## 速率限制

| 角色 | 限制 |
|------|------|
| 免费 | 100次/天 |
| 基础 | 1000次/天 |
| 专业 | 无限 |

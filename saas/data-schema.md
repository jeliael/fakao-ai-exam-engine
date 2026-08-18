# 法考SaaS数据库Schema设计

## 数据库选择
- PostgreSQL（主库，结构化数据）
- Redis（缓存，会话/限流）
- Elasticsearch（法规/题目全文检索）

## 核心表结构

### 1. 用户表 users
```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  uuid UUID DEFAULT gen_random_uuid() UNIQUE,
  phone VARCHAR(20) UNIQUE,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  nickname VARCHAR(100),
  avatar VARCHAR(500),
  role VARCHAR(20) DEFAULT 'free',  -- free/basic/pro
  exam_year INT,
  background VARCHAR(20),  -- law/non_law/zero
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. 法规表 laws
```sql
CREATE TABLE laws (
  id BIGSERIAL PRIMARY KEY,
  law_id VARCHAR(100) UNIQUE,
  name VARCHAR(200) NOT NULL,
  issuer VARCHAR(100),
  issued_date DATE,
  revised_date DATE,
  status VARCHAR(20) DEFAULT 'current',
  verification VARCHAR(20) DEFAULT 'pending',
  flk_url TEXT,
  category VARCHAR(50),
  full_text TEXT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_laws_category ON laws(category);
```

### 3. 法条表 articles
```sql
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  law_id BIGINT REFERENCES laws(id),
  article_no VARCHAR(50),
  chapter VARCHAR(200),
  content TEXT NOT NULL,
  point_tags TEXT[],
  frequency VARCHAR(10),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_articles_law ON articles(law_id);
```

### 4. 题目表 questions
```sql
CREATE TABLE questions (
  id BIGSERIAL PRIMARY KEY,
  question_uuid UUID DEFAULT gen_random_uuid() UNIQUE,
  year INT,
  subject VARCHAR(50),
  type VARCHAR(20),
  difficulty VARCHAR(10),
  source VARCHAR(20),
  question TEXT NOT NULL,
  options JSONB,
  answer VARCHAR(20),
  analysis TEXT,
  exam_point VARCHAR(200),
  law_basis VARCHAR(200),
  verification VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_questions_subject ON questions(subject);
CREATE INDEX idx_questions_year ON questions(year);
```

### 5. 学习记录表 study_records
```sql
CREATE TABLE study_records (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  record_type VARCHAR(20),  -- qna/exam/study/essay
  ref_id VARCHAR(100),
  subject VARCHAR(50),
  score INT,
  duration INT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_study_user ON study_records(user_id);
```

### 6. 错题表 wrong_questions
```sql
CREATE TABLE wrong_questions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  question_id BIGINT REFERENCES questions(id),
  user_answer VARCHAR(20),
  wrong_count INT DEFAULT 1,
  last_wrong_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_wrong_user ON wrong_questions(user_id);
```

### 7. 学习计划表 study_plans
```sql
CREATE TABLE study_plans (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  plan_data JSONB NOT NULL,
  start_date DATE,
  end_date DATE,
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 8. 主观题批改记录表 essay_grades
```sql
CREATE TABLE essay_grades (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  question TEXT NOT NULL,
  user_essay TEXT NOT NULL,
  total_score INT,
  dimension_scores JSONB,
  feedback TEXT,
  paragraph_feedback JSONB,
  suggestions JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 9. 考点表 exam_points
```sql
CREATE TABLE exam_points (
  id BIGSERIAL PRIMARY KEY,
  subject VARCHAR(50),
  point_name VARCHAR(200),
  parent_id BIGINT REFERENCES exam_points(id),
  level INT,
  frequency VARCHAR(10),
  description TEXT,
  law_refs TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_points_subject ON exam_points(subject);
```

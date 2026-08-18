# -*- coding: utf-8 -*-
"""
essay_grader.py — 主观题AI评分框架

功能：
  多维度评分主观题答案，生成结构化评分报告。
  评分维度：
    - 结论正确性 (30%)
    - 法条引用   (20%)
    - 逻辑分析   (25%)
    - 语言表达   (15%)
    - 格式规范   (10%)

  注：本脚本是结构化框架，实际 AI 评分由 LLM 在工作流中完成。
  本脚本负责：读取输入 -> 构建评分框架 -> 输出结构化 JSON。
  当传入 --ai-feedback 参数时，使用已有的 AI 反馈填充框架；
  否则输出空框架供 LLM 填充。

输入：
  --essay        用户答案 Markdown 文件路径
  --rubric       评分标准 JSON 文件路径
  --feedback     (可选) AI 反馈 JSON 文件路径（LLM 已完成的评分）
输出：
  --output       评分报告 JSON 路径（默认: ../output/essay_grade_report.json）

用法：
  python essay_grader.py --essay essay.md --rubric rubric.json
  python essay_grader.py --essay essay.md --rubric rubric.json --feedback feedback.json
  python essay_grader.py --essay essay.md --rubric rubric.json --output custom.json

rubric.json 格式:
  {
    "question": "案情...",
    "question_type": "案例分析题",
    "total_score": 25,
    "dimensions": {
      "conclusion":     {"name": "结论正确性", "weight": 0.30, "max": 25, "criteria": "..."},
      "legal_citation": {"name": "法条引用",   "weight": 0.20, "max": 25, "criteria": "..."},
      "logic_analysis": {"name": "逻辑分析",   "weight": 0.25, "max": 25, "criteria": "..."},
      "language":       {"name": "语言表达",   "weight": 0.15, "max": 25, "criteria": "..."},
      "format":         {"name": "格式规范",   "weight": 0.10, "max": 25, "criteria": "..."}
    },
    "key_points": ["要点1", "要点2", ...],
    "reference_answer": "参考答案..."
  }

feedback.json 格式 (LLM 填充):
  {
    "conclusion":     {"score": 20, "comments": "..."},
    "legal_citation": {"score": 18, "comments": "..."},
    "logic_analysis": {"score": 22, "comments": "..."},
    "language":       {"score": 20, "comments": "..."},
    "format":         {"score": 23, "comments": "..."},
    "paragraph_comments": [
      {"paragraph": "原文段落...", "comment": "批注..."},
      ...
    ],
    "improvement_suggestions": ["建议1", "建议2", ...],
    "overall_comment": "总体评价..."
  }
"""

import argparse
import json
import os
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "output")

# 评分维度默认配置
DEFAULT_DIMENSIONS = {
    "conclusion": {
        "name": "结论正确性",
        "weight": 0.30,
        "description": "结论是否正确、完整，是否遗漏关键结论",
    },
    "legal_citation": {
        "name": "法条引用",
        "weight": 0.20,
        "description": "是否准确引用相关法条，引用是否规范",
    },
    "logic_analysis": {
        "name": "逻辑分析",
        "weight": 0.25,
        "description": "分析逻辑是否严密，法律推理是否得当",
    },
    "language": {
        "name": "语言表达",
        "weight": 0.15,
        "description": "法律语言是否准确、简洁、专业",
    },
    "format": {
        "name": "格式规范",
        "weight": 0.10,
        "description": "答题格式是否规范，层次是否清晰",
    },
}


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------
def load_json(file_path, label):
    """加载 JSON 文件。"""
    if not os.path.exists(file_path):
        print(f"[错误] {label}文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[错误] {label}文件 JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)


def load_text(file_path, label):
    """加载文本文件。"""
    if not os.path.exists(file_path):
        print(f"[错误] {label}文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[错误] 读取{label}文件异常: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# 评分框架构建
# ---------------------------------------------------------------------------
def split_paragraphs(essay_text):
    """将答案文本按段落分割。"""
    paragraphs = []
    raw_paragraphs = essay_text.strip().split("\n")
    for p in raw_paragraphs:
        p = p.strip()
        if p:
            paragraphs.append(p)
    return paragraphs


def build_grade_framework(essay_text, rubric, feedback=None):
    """构建评分报告框架。

    如果 feedback 不为 None，则使用 AI 反馈填充实际得分；
    否则输出空框架（score=None）供 LLM 填充。
    """
    dimensions_config = rubric.get("dimensions", DEFAULT_DIMENSIONS)
    total_score = rubric.get("total_score", 100)
    paragraphs = split_paragraphs(essay_text)

    # 各维度评分
    dimension_results = {}
    weighted_total = 0
    all_scored = True

    for dim_key, dim_config in dimensions_config.items():
        name = dim_config.get("name", dim_key)
        weight = dim_config.get("weight", 0)
        criteria = dim_config.get("criteria", dim_config.get("description", ""))
        max_score = dim_config.get("max", total_score)

        # 从 AI 反馈中获取得分
        if feedback and dim_key in feedback:
            score = feedback[dim_key].get("score")
            comments = feedback[dim_key].get("comments", "")
        else:
            score = None
            comments = ""
            all_scored = False

        # 计算加权得分
        weighted_score = None
        if score is not None:
            # 归一化到百分制后乘以权重
            normalized = (score / max_score) * 100 if max_score > 0 else 0
            weighted_score = round(normalized * weight, 1)
            weighted_total += weighted_score

        dimension_results[dim_key] = {
            "name": name,
            "weight": weight,
            "max_score": max_score,
            "score": score,
            "weighted_score": weighted_score,
            "criteria": criteria,
            "comments": comments,
        }

    # 逐段批注
    paragraph_comments = []
    if feedback and "paragraph_comments" in feedback:
        paragraph_comments = feedback["paragraph_comments"]
    else:
        # 构建空框架
        for i, para in enumerate(paragraphs):
            paragraph_comments.append(
                {
                    "paragraph_index": i + 1,
                    "paragraph": para[:200] + ("..." if len(para) > 200 else ""),
                    "comment": "",
                }
            )
        all_scored = False

    # 改进建议
    improvement_suggestions = []
    if feedback and "improvement_suggestions" in feedback:
        improvement_suggestions = feedback["improvement_suggestions"]
    else:
        all_scored = False

    # 总体评价
    overall_comment = ""
    if feedback and "overall_comment" in feedback:
        overall_comment = feedback["overall_comment"]
    else:
        all_scored = False

    # 构建报告
    report = {
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": rubric.get("question", ""),
            "question_type": rubric.get("question_type", "未知"),
            "total_score": total_score,
            "essay_length": len(essay_text),
            "paragraph_count": len(paragraphs),
            "status": "completed" if all_scored else "pending_ai",
        },
        "dimensions": dimension_results,
        "weighted_total": round(weighted_total, 1) if all_scored else None,
        "paragraph_comments": paragraph_comments,
        "improvement_suggestions": improvement_suggestions,
        "overall_comment": overall_comment,
        "reference_answer": rubric.get("reference_answer", ""),
        "key_points": rubric.get("key_points", []),
    }

    return report


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------
def print_report(report):
    """打印评分报告摘要。"""
    print("=" * 60)
    print("主观题评分报告")
    print("=" * 60)
    print(f"  题目类型:   {report['meta']['question_type']}")
    print(f"  总分:       {report['meta']['total_score']}")
    print(f"  答案字数:   {report['meta']['essay_length']}")
    print(f"  段落数:     {report['meta']['paragraph_count']}")
    print(f"  评分状态:   {'已完成' if report['meta']['status'] == 'completed' else '待AI评分'}")
    print("-" * 60)
    print("各维度评分:")
    for dim_key, dim in report["dimensions"].items():
        score_str = f"{dim['score']}/{dim['max_score']}" if dim["score"] is not None else "待评分"
        weighted_str = f"(加权 {dim['weighted_score']})" if dim["weighted_score"] is not None else ""
        print(f"  {dim['name']:8s}  {score_str}  权重 {dim['weight']*100:.0f}%  {weighted_str}")
    print("-" * 60)
    if report["weighted_total"] is not None:
        print(f"  加权总分:   {report['weighted_total']} / 100")
    else:
        print("  加权总分:   待AI评分后计算")
    if report["overall_comment"]:
        print(f"\n  总体评价:   {report['overall_comment']}")
    if report["improvement_suggestions"]:
        print("\n  改进建议:")
        for i, s in enumerate(report["improvement_suggestions"], 1):
            print(f"    {i}. {s}")
    print("=" * 60)


def save_report(report, output_path):
    """保存报告到 JSON 文件。"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[完成] 评分报告已保存至: {output_path}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="主观题AI评分框架 — 多维度评分主观题答案",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python essay_grader.py --essay essay.md --rubric rubric.json
  python essay_grader.py --essay essay.md --rubric rubric.json --feedback feedback.json
  python essay_grader.py --essay essay.md --rubric rubric.json --output custom.json
        """,
    )
    parser.add_argument("--essay", required=True, type=str, help="用户答案 Markdown 文件路径")
    parser.add_argument("--rubric", required=True, type=str, help="评分标准 JSON 文件路径")
    parser.add_argument(
        "--feedback",
        type=str,
        default=None,
        help="AI 反馈 JSON 文件路径（LLM 已完成的评分）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(OUTPUT_DIR, "essay_grade_report.json"),
        help="输出报告路径（默认: ../output/essay_grade_report.json）",
    )

    args = parser.parse_args()

    essay_text = load_text(args.essay, "用户答案")
    rubric = load_json(args.rubric, "评分标准")

    feedback = None
    if args.feedback:
        feedback = load_json(args.feedback, "AI反馈")

    report = build_grade_framework(essay_text, rubric, feedback)
    print_report(report)
    save_report(report, args.output)


if __name__ == "__main__":
    main()

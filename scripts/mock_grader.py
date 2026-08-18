# -*- coding: utf-8 -*-
"""
mock_grader.py — 客观题自动评分脚本

功能：
  对比用户答案与标准答案，计算得分并生成评分报告。
  评分规则：单选1分/题，多选2分/题；少选/多选/错选不得分（多选需完全匹配）。
  统计：总分、正确率、各科目正确率、各考点掌握情况。

输入：
  --answers  用户答案 JSON 文件路径
  --key      标准答案+考点信息 JSON 文件路径
输出：
  ../output/grade_report.json

用法：
  python mock_grader.py --answers answers.json --key key.json
  python mock_grader.py --answers answers.json --key key.json --output custom_report.json

answers.json 格式:
  [
    {"id": "Q001", "type": "single", "answer": "A"},
    {"id": "Q002", "type": "multiple", "answer": ["A", "C", "D"]},
    ...
  ]

key.json 格式:
  [
    {"id": "Q001", "type": "single", "answer": "A", "score": 1, "subject": "刑法", "point": "犯罪概念"},
    {"id": "Q002", "type": "multiple", "answer": ["A","C","D"], "score": 2, "subject": "民法", "point": "善意取得"},
    ...
  ]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from collections import defaultdict

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "output")


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------
def load_json(file_path, label):
    """加载 JSON 文件，带异常处理。"""
    if not os.path.exists(file_path):
        print(f"[错误] {label}文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[错误] {label}文件 JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 读取{label}文件异常: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# 评分逻辑
# ---------------------------------------------------------------------------
def normalize_answer(answer):
    """将答案统一为排序后的字符串，便于比较。"""
    if isinstance(answer, list):
        return "".join(sorted([str(a).strip().upper() for a in answer]))
    return str(answer).strip().upper()


def grade_single(user_answer, correct_answer):
    """单选题评分：完全匹配得1分。"""
    return 1 if normalize_answer(user_answer) == normalize_answer(correct_answer) else 0


def grade_multiple(user_answer, correct_answer):
    """多选题评分：完全匹配得2分，少选/多选/错选不得分。"""
    return 2 if normalize_answer(user_answer) == normalize_answer(correct_answer) else 0


def grade_question(user_ans, key_entry):
    """评分单道题，返回 (得分, 是否正确)。"""
    q_type = key_entry.get("type", "single")
    correct_ans = key_entry.get("answer", "")
    max_score = key_entry.get("score", 1 if q_type == "single" else 2)

    if q_type == "single":
        earned = grade_single(user_ans, correct_ans)
    elif q_type == "multiple":
        earned = grade_multiple(user_ans, correct_ans)
    else:
        # 未知题型按单选处理
        earned = grade_single(user_ans, correct_ans)

    return earned, earned > 0, max_score


def run_grading(answers, key_list):
    """执行全部评分，返回详细报告。"""
    # 将 key 转为字典便于查找
    key_map = {item["id"]: item for item in key_list}

    results = []
    total_score = 0
    max_total_score = 0
    correct_count = 0
    total_count = 0

    # 科目和考点统计
    subject_stats = defaultdict(lambda: {"correct": 0, "total": 0, "score": 0, "max_score": 0})
    point_stats = defaultdict(lambda: {"correct": 0, "total": 0, "score": 0, "max_score": 0})

    for ans in answers:
        q_id = ans.get("id")
        user_ans = ans.get("answer")

        if q_id not in key_map:
            results.append(
                {
                    "id": q_id,
                    "status": "missing_key",
                    "message": f"标准答案中缺少题目 {q_id}",
                }
            )
            continue

        key_entry = key_map[q_id]
        earned, is_correct, max_score = grade_question(user_ans, key_entry)

        total_score += earned
        max_total_score += max_score
        total_count += 1
        if is_correct:
            correct_count += 1

        # 科目统计
        subject = key_entry.get("subject", "未分类")
        subject_stats[subject]["total"] += 1
        subject_stats[subject]["score"] += earned
        subject_stats[subject]["max_score"] += max_score
        if is_correct:
            subject_stats[subject]["correct"] += 1

        # 考点统计
        point = key_entry.get("point", "未分类")
        point_key = f"{subject} > {point}"
        point_stats[point_key]["total"] += 1
        point_stats[point_key]["score"] += earned
        point_stats[point_key]["max_score"] += max_score
        if is_correct:
            point_stats[point_key]["correct"] += 1

        results.append(
            {
                "id": q_id,
                "type": key_entry.get("type", "single"),
                "subject": subject,
                "point": point,
                "user_answer": user_ans,
                "correct_answer": key_entry.get("answer"),
                "earned_score": earned,
                "max_score": max_score,
                "is_correct": is_correct,
                "status": "correct" if is_correct else "wrong",
            }
        )

    # 检查用户未答的题目
    answered_ids = {a.get("id") for a in answers}
    for q_id, key_entry in key_map.items():
        if q_id not in answered_ids:
            max_score = key_entry.get("score", 1)
            max_total_score += max_score
            total_count += 1

            subject = key_entry.get("subject", "未分类")
            subject_stats[subject]["total"] += 1
            subject_stats[subject]["max_score"] += max_score

            point = key_entry.get("point", "未分类")
            point_key = f"{subject} > {point}"
            point_stats[point_key]["total"] += 1
            point_stats[point_key]["max_score"] += max_score

            results.append(
                {
                    "id": q_id,
                    "type": key_entry.get("type", "single"),
                    "subject": subject,
                    "point": point,
                    "user_answer": None,
                    "correct_answer": key_entry.get("answer"),
                    "earned_score": 0,
                    "max_score": max_score,
                    "is_correct": False,
                    "status": "unanswered",
                }
            )

    # 构建报告
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    score_rate = (total_score / max_total_score * 100) if max_total_score > 0 else 0

    # 科目正确率排序
    subject_report = []
    for subj, stats in sorted(subject_stats.items(), key=lambda x: x[1]["total"], reverse=True):
        subj_accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        subj_score_rate = (stats["score"] / stats["max_score"] * 100) if stats["max_score"] > 0 else 0
        subject_report.append(
            {
                "subject": subj,
                "correct": stats["correct"],
                "total": stats["total"],
                "accuracy": round(subj_accuracy, 1),
                "score": stats["score"],
                "max_score": stats["max_score"],
                "score_rate": round(subj_score_rate, 1),
            }
        )

    # 考点掌握情况（按正确率升序，薄弱点在前）
    point_report = []
    for pt, stats in sorted(point_stats.items(), key=lambda x: x[1]["correct"] / max(x[1]["total"], 1)):
        pt_accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        level = "掌握" if pt_accuracy >= 80 else ("一般" if pt_accuracy >= 60 else "薄弱")
        point_report.append(
            {
                "point": pt,
                "correct": stats["correct"],
                "total": stats["total"],
                "accuracy": round(pt_accuracy, 1),
                "level": level,
            }
        )

    report = {
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_questions": total_count,
            "answered_questions": len(answered_ids),
        },
        "summary": {
            "total_score": total_score,
            "max_score": max_total_score,
            "score_rate": round(score_rate, 1),
            "total_questions": total_count,
            "correct_count": correct_count,
            "wrong_count": total_count - correct_count,
            "accuracy": round(accuracy, 1),
        },
        "subjects": subject_report,
        "exam_points": point_report,
        "details": results,
    }

    return report


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------
def print_summary(report):
    """打印评分摘要到终端。"""
    s = report["summary"]
    print("=" * 60)
    print("客观题评分报告")
    print("=" * 60)
    print(f"  总分:       {s['total_score']} / {s['max_score']} ({s['score_rate']}%)")
    print(f"  正确数:     {s['correct_count']} / {s['total_questions']}")
    print(f"  错误数:     {s['wrong_count']}")
    print(f"  正确率:     {s['accuracy']}%")
    print("-" * 60)
    print("各科目表现:")
    for subj in report["subjects"]:
        print(
            f"  {subj['subject']:8s}  "
            f"{subj['correct']}/{subj['total']}  "
            f"正确率 {subj['accuracy']:5.1f}%  "
            f"得分率 {subj['score_rate']:5.1f}%"
        )
    print("-" * 60)
    print("薄弱考点（正确率 < 60%）:")
    weak_points = [p for p in report["exam_points"] if p["level"] == "薄弱"]
    if weak_points:
        for pt in weak_points:
            print(f"  {pt['point']}  {pt['correct']}/{pt['total']}  {pt['accuracy']}%")
    else:
        print("  无薄弱考点")
    print("=" * 60)


def save_report(report, output_path):
    """保存报告到 JSON 文件。"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[完成] 报告已保存至: {output_path}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="客观题自动评分 — 对比用户答案与标准答案，生成评分报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python mock_grader.py --answers answers.json --key key.json
  python mock_grader.py --answers answers.json --key key.json --output custom_report.json
        """,
    )
    parser.add_argument("--answers", required=True, type=str, help="用户答案 JSON 文件路径")
    parser.add_argument("--key", required=True, type=str, help="标准答案+考点信息 JSON 文件路径")
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(OUTPUT_DIR, "grade_report.json"),
        help="输出报告路径（默认: ../output/grade_report.json）",
    )

    args = parser.parse_args()

    answers = load_json(args.answers, "用户答案")
    key_list = load_json(args.key, "标准答案")

    if not isinstance(answers, list):
        print("[错误] 用户答案文件应为 JSON 数组格式", file=sys.stderr)
        sys.exit(1)
    if not isinstance(key_list, list):
        print("[错误] 标准答案文件应为 JSON 数组格式", file=sys.stderr)
        sys.exit(1)

    report = run_grading(answers, key_list)
    print_summary(report)
    save_report(report, args.output)


if __name__ == "__main__":
    main()

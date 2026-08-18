# -*- coding: utf-8 -*-
"""
law_search.py — 法规检索脚本

功能：
  1. search 子命令：按关键词搜索法规列表（先查本地 laws-index.json 缓存，再查 flk.npc.gov.cn API）
  2. article 子命令：获取特定法规的特定条款（本地索引 + 在线详情）

用法：
  python law_search.py search "民法典"
  python law_search.py search "刑法" --online
  python law_search.py article "civil-code" "第311条"
  python law_search.py article "criminal-law" "第20条" --online

本地索引路径：../knowledge/laws/laws-index.json
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime

# 第三方依赖
try:
    import requests
except ImportError:
    requests = None  # 延迟到使用时报错

# ---------------------------------------------------------------------------
# 路径常量（相对于脚本所在目录）
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(SCRIPT_DIR, "..", "knowledge")
LAWS_INDEX_PATH = os.path.join(KNOWLEDGE_DIR, "laws", "laws-index.json")

# flk API 端点
FLK_SEARCH_URL = "https://flk.npc.gov.cn/api/"
FLK_DETAIL_URL = "https://flk.npc.gov.cn/api/"

# 请求头
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://flk.npc.gov.cn/",
}

# 超时（秒）
TIMEOUT = 15


# ---------------------------------------------------------------------------
# 本地索引操作
# ---------------------------------------------------------------------------
def load_laws_index():
    """读取本地法规索引文件。"""
    if not os.path.exists(LAWS_INDEX_PATH):
        return None
    try:
        with open(LAWS_INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[错误] 本地索引 JSON 解析失败: {e}", file=sys.stderr)
        return None


def search_local(keyword):
    """在本地索引中搜索关键词，返回匹配的法规列表。"""
    index = load_laws_index()
    if index is None:
        return []

    results = []
    kw_lower = keyword.lower()
    for law in index.get("laws", []):
        name = law.get("name", "")
        law_id = law.get("id", "")
        # 匹配法规名称或 ID
        if kw_lower in name.lower() or kw_lower in law_id.lower():
            results.append(law)
        else:
            # 搜索关键条款标题
            for art in law.get("key_articles", []):
                if kw_lower in art.get("title", "").lower():
                    results.append(law)
                    break
    return results


def find_law_by_id(law_id):
    """按 ID 在本地索引中查找法规。"""
    index = load_laws_index()
    if index is None:
        return None
    for law in index.get("laws", []):
        if law.get("id") == law_id:
            return law
    return None


# ---------------------------------------------------------------------------
# 在线 API 操作
# ---------------------------------------------------------------------------
def search_online(keyword):
    """调用 flk.npc.gov.cn API 按标题检索法规列表。"""
    if requests is None:
        print("[错误] 缺少 requests 库，请先安装: pip install requests", file=sys.stderr)
        return []

    params = {
        "searchType": "title",
        "sortTr": "f_bbrq_s;desc",
        "type": "",
        "xlwj": "",
        "fgbt": keyword,
        "page": 1,
        "size": 20,
    }

    try:
        resp = requests.get(
            FLK_SEARCH_URL, params=params, headers=HEADERS, timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        print("[警告] flk API 请求超时，请稍后重试或使用本地索引。", file=sys.stderr)
        return []
    except requests.exceptions.ConnectionError:
        print("[警告] 无法连接 flk.npc.gov.cn，请检查网络或使用本地索引。", file=sys.stderr)
        return []
    except json.JSONDecodeError:
        print(
            "[警告] flk API 返回非 JSON 数据，可能遇到验证码拦截，请人工核验: "
            "https://flk.npc.gov.cn",
            file=sys.stderr,
        )
        return []
    except Exception as e:
        print(f"[警告] flk API 请求异常: {e}", file=sys.stderr)
        return []

    # 解析返回数据
    results = []
    items = data.get("result", {}).get("data", [])
    if not items and isinstance(data.get("result"), list):
        items = data["result"]

    for item in items:
        results.append(
            {
                "id": item.get("id", ""),
                "name": item.get("title", item.get("name", "")),
                "issuer": item.get("office", item.get("fbr", "")),
                "issued": item.get("publish", item.get("f_bbrq_s", "")),
                "revised": item.get("revise", ""),
                "status": "current" if item.get("status", "").get("state", 0) == 1 else "outdated",
                "flk_url": f"https://flk.npc.gov.cn/detail2.html?id={item.get('id', '')}",
                "verification": "pending",
            }
        )
    return results


def fetch_law_detail_online(law_id, keyword=None):
    """调用 flk API 获取法规详情（章节条款结构树）。

    注意：flk 的详情 API 需要法规的 flk 内部 ID（非本地 ID）。
    本函数先通过搜索获取 flk ID，再请求详情。
    """
    if requests is None:
        print("[错误] 缺少 requests 库，请先安装: pip install requests", file=sys.stderr)
        return None

    # 1. 先搜索获取 flk 内部 ID
    local_law = find_law_by_id(law_id)
    search_kw = keyword or (local_law.get("name", "") if local_law else law_id)

    online_results = search_online(search_kw)
    if not online_results:
        return None

    flk_id = online_results[0].get("id", "")
    if not flk_id:
        return None

    # 2. 请求详情
    params = {
        "type": "",
        "searchType": "title",
        "sortTr": "f_bbrq_s;desc",
        "fgbt": search_kw,
    }
    try:
        resp = requests.get(
            FLK_DETAIL_URL, params=params, headers=HEADERS, timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[警告] 获取法规详情失败: {e}", file=sys.stderr)
        return None

    return data


# ---------------------------------------------------------------------------
# 输出格式化
# ---------------------------------------------------------------------------
def format_law_brief(law):
    """格式化法规基本信息。"""
    lines = []
    lines.append(f"  法规名称: {law.get('name', '未知')}")
    lines.append(f"  法规ID:   {law.get('id', '未知')}")
    lines.append(f"  制定机关: {law.get('issuer', '未知')}")
    lines.append(f"  制定日期: {law.get('issued', '未知')}")
    if law.get("revised"):
        lines.append(f"  修订日期: {law['revised']}")
    status = law.get("status", "unknown")
    status_text = {"current": "现行有效", "outdated": "已废止"}.get(status, status)
    lines.append(f"  现行状态: {status_text}")
    verification = law.get("verification", "pending")
    ver_text = {"verified": "已核验", "pending": "待核验", "outdated": "已废止"}.get(
        verification, verification
    )
    lines.append(f"  核验状态: {ver_text}")
    if law.get("flk_url"):
        lines.append(f"  flk链接:  {law['flk_url']}")
    return "\n".join(lines)


def format_key_articles(law):
    """格式化关键条款列表。"""
    articles = law.get("key_articles", [])
    if not articles:
        return "  （无关键条款记录）"

    lines = ["  关键条款:"]
    freq_icon = {"high": "★", "medium": "☆", "low": ""}
    for art in articles:
        icon = freq_icon.get(art.get("frequency", ""), "")
        lines.append(f"    {art['article']}  {art.get('title', '')}  {icon}")
    return "\n".join(lines)


def format_search_results(results, keyword):
    """格式化搜索结果输出。"""
    if not results:
        return f"未找到与 '{keyword}' 相关的法规。"

    lines = []
    lines.append(f"搜索 '{keyword}' — 共找到 {len(results)} 部法规:")
    lines.append("=" * 60)
    for i, law in enumerate(results, 1):
        lines.append(f"\n[{i}]")
        lines.append(format_law_brief(law))
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_article(law, article_ref, online_detail=None):
    """格式化特定条款的输出。"""
    lines = []
    lines.append("=" * 60)
    lines.append(format_law_brief(law))
    lines.append("-" * 60)

    # 在本地索引中查找该条款
    found_local = False
    for art in law.get("key_articles", []):
        if article_ref in art.get("article", ""):
            lines.append(f"  查询条款: {art['article']}")
            lines.append(f"  条款主题: {art.get('title', '未知')}")
            lines.append(f"  考查频率: {art.get('frequency', '未知')}")
            found_local = True
            break

    if not found_local:
        lines.append(f"  查询条款: {article_ref}")
        lines.append("  （本地索引中无该条款的详细记录）")

    lines.append("-" * 60)

    if online_detail:
        lines.append("  在线详情（来自 flk.npc.gov.cn）:")
        # 尝试从返回数据中提取条款正文
        result_data = online_detail.get("result", online_detail)
        if isinstance(result_data, dict):
            # 尝试多种可能的字段
            content = (
                result_data.get("content")
                or result_data.get("body")
                or result_data.get("text")
                or ""
            )
            if content:
                # 尝试定位目标条款
                article_text = extract_article_from_content(content, article_ref)
                if article_text:
                    lines.append(article_text)
                else:
                    lines.append("  （在线返回了法规全文，但未能定位到指定条款，请人工核验）")
                    lines.append(f"  flk链接: {result_data.get('url', '')}")
            else:
                lines.append("  （在线返回数据中未找到条款正文，可能需要人工访问 flk.npc.gov.cn 核验）")
        else:
            lines.append(f"  在线返回: {json.dumps(online_detail, ensure_ascii=False, indent=2)[:500]}")
    else:
        lines.append("  在线详情: 未获取（使用 --online 参数可在线查询）")
        lines.append("  提示: 请访问 https://flk.npc.gov.cn 人工核验完整法条文本")

    lines.append("=" * 60)
    return "\n".join(lines)


def extract_article_from_content(content, article_ref):
    """从法规全文中提取指定条款的文本。"""
    # 将 "第311条" 转为正则模式
    num = re.search(r"第?(\d+)条", article_ref)
    if not num:
        return None
    target_num = int(num.group(1))

    # 匹配 "第N条　" 或 "第N条 " 开头的条款
    pattern = r"第\s*{0}\s*条[　\s]*(.*?)(?=第\s*\d+\s*条|$)".format(target_num)
    match = re.search(pattern, content, re.DOTALL)
    if match:
        text = match.group(0).strip()
        return "  " + text[:1000]  # 限制长度
    return None


# ---------------------------------------------------------------------------
# 子命令实现
# ---------------------------------------------------------------------------
def cmd_search(args):
    """search 子命令：搜索法规。"""
    keyword = args.keyword
    use_online = args.online

    # 1. 先查本地
    results = search_local(keyword)
    source = "本地索引"

    # 2. 在线查询（如果指定 --online 或本地无结果）
    if use_online or not results:
        if not use_online and not results:
            print(f"[提示] 本地索引未找到 '{keyword}'，尝试在线查询...", file=sys.stderr)
        online_results = search_online(keyword)
        if online_results:
            # 合并去重（以名称为准）
            existing_names = {r.get("name") for r in results}
            for r in online_results:
                if r.get("name") not in existing_names:
                    results.append(r)
                    existing_names.add(r.get("name"))
            source = "本地索引 + 在线API"
        elif not results:
            print(
                "[提示] 在线查询也无结果。flk 可能有验证码拦截，请人工访问 "
                "https://flk.npc.gov.cn 核验。",
                file=sys.stderr,
            )

    print(format_search_results(results, keyword))
    print(f"\n数据来源: {source}")
    print(f"检索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_article(args):
    """article 子命令：获取特定条款。"""
    law_id = args.law_id
    article_ref = args.article
    use_online = args.online

    # 1. 本地查找法规
    law = find_law_by_id(law_id)
    if law is None:
        # 尝试按名称搜索
        law_results = search_local(law_id)
        if law_results:
            law = law_results[0]
            print(f"[提示] 按 '{law_id}' 匹配到法规: {law.get('name')}", file=sys.stderr)
        else:
            print(f"[错误] 未找到法规 ID '{law_id}'。请先使用 search 子命令查找。", file=sys.stderr)
            sys.exit(1)

    # 2. 在线获取详情
    online_detail = None
    if use_online:
        online_detail = fetch_law_detail_online(law_id, law.get("name"))

    print(format_article(law, article_ref, online_detail))
    print(f"\n检索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="法规检索脚本 — 检索国家法律法规数据库(flk.npc.gov.cn)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python law_search.py search "民法典"
  python law_search.py search "刑法" --online
  python law_search.py article "civil-code" "第311条"
  python law_search.py article "criminal-law" "第20条" --online
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # search 子命令
    search_parser = subparsers.add_parser("search", help="按关键词搜索法规列表")
    search_parser.add_argument("keyword", type=str, help="搜索关键词（法规名称或关键词）")
    search_parser.add_argument(
        "--online", action="store_true", help="强制在线查询 flk.npc.gov.cn API"
    )

    # article 子命令
    article_parser = subparsers.add_parser("article", help="获取特定法规的特定条款")
    article_parser.add_argument("law_id", type=str, help="法规ID（如 civil-code）或法规名称")
    article_parser.add_argument("article", type=str, help="条款编号（如 第311条）")
    article_parser.add_argument(
        "--online", action="store_true", help="在线获取完整法条文本"
    )

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "article":
        cmd_article(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Discord Webhook への投稿クライアント。"""
from datetime import datetime

import requests

MAX_DESC_LEN = 4000
MAX_TITLE_LEN = 250
MAX_FIELD_VALUE_LEN = 1024

# 論文タイプ別の色
PTYPE_COLORS = {
    "Randomized Controlled Trial": 0x2ECC71,
    "Meta-Analysis": 0x3498DB,
    "Systematic Review": 0x3498DB,
    "Clinical Trial, Phase III": 0x27AE60,
    "Clinical Trial, Phase II": 0x58D68D,
    "Clinical Trial": 0x58D68D,
    "Multicenter Study": 0x9B59B6,
    "Observational Study": 0xF39C12,
    "Review": 0x95A5A6,
    "Case Reports": 0xE74C3C,
}
DEFAULT_COLOR = 0x7F8C8D

# 論文タイプの短縮表示
PTYPE_SHORT = {
    "Randomized Controlled Trial": "🎯 RCT",
    "Meta-Analysis": "📊 Meta-Analysis",
    "Systematic Review": "📚 Systematic Review",
    "Clinical Trial, Phase III": "💊 Phase III Trial",
    "Clinical Trial, Phase II": "💊 Phase II Trial",
    "Clinical Trial": "💊 Clinical Trial",
    "Multicenter Study": "🏥 Multicenter",
    "Observational Study": "👁️ Observational",
    "Review": "📖 Review",
    "Case Reports": "📝 Case Report",
}


def _ptype_display(ptype: str) -> str:
    return PTYPE_SHORT.get(ptype, f"📄 {ptype}")


def _ptype_color(ptype: str) -> int:
    return PTYPE_COLORS.get(ptype, DEFAULT_COLOR)


def post_to_discord(webhook_url: str, paper: dict, summary: str) -> None:
    """1論文 = 1 embed として投稿する。"""
    title = (paper.get("title") or "Untitled")[:MAX_TITLE_LEN]
    desc = summary[:MAX_DESC_LEN]
    primary_ptype = paper.get("primary_ptype", "Journal Article")

    fields = [
        {
            "name": "Study Type",
            "value": _ptype_display(primary_ptype),
            "inline": True,
        },
        {
            "name": "Journal",
            "value": f"{paper.get('journal_iso') or paper.get('journal', 'N/A')} ({paper.get('year', 'N/A')})"[:MAX_FIELD_VALUE_LEN],
            "inline": True,
        },
        {
            "name": "PMID",
            "value": paper.get("pmid", "N/A"),
            "inline": True,
        },
    ]

    # CD 病型・トピックタグ
    topic_tags = paper.get("topic_tags") or []
    if topic_tags:
        fields.append({
            "name": "Topic",
            "value": " / ".join(topic_tags)[:MAX_FIELD_VALUE_LEN],
            "inline": False,
        })

    fields.append({
        "name": "Authors",
        "value": (paper.get("authors") or "N/A")[:MAX_FIELD_VALUE_LEN],
        "inline": False,
    })

    if paper.get("doi"):
        fields.append({
            "name": "DOI",
            "value": f"[{paper['doi']}](https://doi.org/{paper['doi']})",
            "inline": False,
        })

    embed = {
        "title": f"📄 {title}",
        "url": paper.get("url", ""),
        "description": desc,
        "color": _ptype_color(primary_ptype),
        "fields": fields,
        "footer": {"text": "CD Paper Bot · via PubMed + Claude Sonnet"},
    }

    payload = {"embeds": [embed]}
    r = requests.post(webhook_url, json=payload, timeout=30)
    r.raise_for_status()


def post_header(webhook_url: str, n_papers: int, paper_summary: dict | None = None,
                topic_summary: dict | None = None) -> None:
    """その日のヘッダーメッセージを投稿する。"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"🧬 **Crohn's Disease Papers Daily Digest — {today}**",
        f"本日の新着論文: **{n_papers}本**",
    ]
    if paper_summary:
        breakdown = " / ".join(f"{k}: {v}" for k, v in paper_summary.items())
        lines.append(f"📊 Study types: {breakdown}")
    if topic_summary:
        topic_breakdown = " / ".join(f"{k} ({v})" for k, v in topic_summary.items())
        lines.append(f"🏷️ Topics: {topic_breakdown}")

    r = requests.post(webhook_url, json={"content": "\n".join(lines)}, timeout=30)
    r.raise_for_status()

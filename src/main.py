"""メインエントリポイント。"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

# src/ を import path に追加
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DISCORD_WEBHOOK_URL,
    MAX_PAPERS_PER_RUN,
    POSTED_PMIDS_FILE,
    PUBMED_QUERY,
    validate,
)
from pubmed_client import fetch_paper_details, search_pubmed
from claude_client import summarize_paper
from discord_client import post_header, post_to_discord


def load_posted_pmids() -> set:
    p = Path(POSTED_PMIDS_FILE)
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[warn] posted_pmids.json の読み込みに失敗: {e}. 空集合で開始します。")
        return set()


def save_posted_pmids(pmids: set) -> None:
    p = Path(POSTED_PMIDS_FILE)
    p.parent.mkdir(parents=True, exist_ok=True)
    sorted_pmids = sorted(pmids, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)[:2000]
    p.write_text(
        json.dumps(sorted_pmids, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def summarize_paper_types(papers: list) -> dict:
    """論文タイプごとの件数を集計する。"""
    counter = Counter(p.get("primary_ptype", "Other") for p in papers)
    return dict(counter.most_common())


def summarize_topics(papers: list) -> dict:
    """CD トピックタグごとの件数を集計する（複数タグ持ちは重複カウント）。"""
    counter: Counter = Counter()
    for p in papers:
        for tag in p.get("topic_tags") or []:
            counter[tag] += 1
    return dict(counter.most_common())


def main() -> None:
    print("=== CD Paper Bot 起動 ===")
    validate()

    posted = load_posted_pmids()
    print(f"既投稿 PMID 数: {len(posted)}")

    pmids = search_pubmed(PUBMED_QUERY, max_results=50)
    print(f"PubMed 検索ヒット: {len(pmids)} 件")

    new_pmids = [p for p in pmids if p not in posted][:MAX_PAPERS_PER_RUN]
    print(f"新規処理対象: {len(new_pmids)} 件")

    if not new_pmids:
        print("新規論文なし。終了。")
        return

    papers = fetch_paper_details(new_pmids)
    print(f"詳細取得成功: {len(papers)} 件")
    if not papers:
        print("Abstract を持つ論文がありませんでした。終了。")
        return

    ptype_summary = summarize_paper_types(papers)
    topic_summary = summarize_topics(papers)
    post_header(DISCORD_WEBHOOK_URL, len(papers), ptype_summary, topic_summary)
    time.sleep(1)

    success_count = 0
    for paper in papers:
        pmid = paper.get("pmid", "?")
        title_preview = (paper.get("title") or "")[:60]
        tags_str = ",".join(paper.get("topic_tags") or []) or "general"
        try:
            print(f"[解説生成] PMID={pmid} [{paper.get('primary_ptype')}] <{tags_str}>: {title_preview}...")
            summary = summarize_paper(paper)
            post_to_discord(DISCORD_WEBHOOK_URL, paper, summary)
            posted.add(pmid)
            success_count += 1
            time.sleep(2)
        except Exception as e:
            print(f"[error] PMID={pmid}: {e}")
            continue

    save_posted_pmids(posted)
    print(f"=== 完了: {success_count}/{len(papers)} 件投稿 ===")


if __name__ == "__main__":
    main()

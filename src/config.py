"""設定ファイル。環境変数と検索クエリを一元管理。"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# PubMed 検索クエリ（CD: Crohn病）
# ------------------------------------------------------------
# CD は luminal / fistulizing / stricturing の病型別に研究が分かれ、
# さらに術後再発・小腸評価（MRE/CE）など研究対象が多岐にわたります。
# UC bot と同様に RCT / meta-analysis / 主要誌に絞った設計です。
#
# 代替クエリ例:
#   - 瘻孔性/肛門病変に絞る:
#       '("Crohn Disease"[MeSH]) AND '
#       '("rectal fistula"[MeSH] OR "perianal"[tiab] OR "fistulizing"[tiab])'
#   - 狭窄/術後再発に絞る:
#       '("Crohn Disease"[MeSH]) AND '
#       '("intestinal strictures"[tiab] OR "postoperative recurrence"[tiab])'
#   - 小腸画像・カプセル内視鏡:
#       '("Crohn Disease"[MeSH]) AND '
#       '("magnetic resonance enterography"[tiab] OR "MRE"[tiab] OR '
#       '"capsule endoscopy"[MeSH] OR "intestinal ultrasound"[tiab])'
# ============================================================
PUBMED_QUERY = (
    '('
    '"Crohn Disease"[MeSH Terms] '
    'OR "Crohn Disease"[Title/Abstract] '
    'OR "Crohn\'s Disease"[Title/Abstract] '
    'OR "Crohns Disease"[Title/Abstract]'
    ') '
    'AND ('
    'Randomized Controlled Trial[PT] '
    'OR Meta-Analysis[PT] '
    'OR Systematic Review[PT] '
    'OR Clinical Trial, Phase III[PT] '
    'OR Clinical Trial, Phase II[PT] '
    'OR "Gastroenterology"[Journal] '
    'OR "Gut"[Journal] '
    'OR "Lancet"[Journal] '
    'OR "Lancet Gastroenterol Hepatol"[Journal] '
    'OR "N Engl J Med"[Journal] '
    'OR "J Crohns Colitis"[Journal] '
    'OR "Am J Gastroenterol"[Journal] '
    'OR "Clin Gastroenterol Hepatol"[Journal] '
    'OR "Aliment Pharmacol Ther"[Journal] '
    'OR "Inflamm Bowel Dis"[Journal] '
    'OR "Dis Colon Rectum"[Journal] '
    'OR "Ann Surg"[Journal]'
    ') '
    'AND ("last 7 days"[PDat]) '
    'AND (English[Language] OR Japanese[Language])'
)

# 1回の実行で処理する最大論文数（コスト制御）
# CD も論文数が多いため 6 本程度を推奨
MAX_PAPERS_PER_RUN = 6

# ============================================================
# API 設定
# ============================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "")

# Claude モデル（最新の Sonnet）
CLAUDE_MODEL = "claude-sonnet-4-5"

# 投稿済み PMID を記録するファイル
POSTED_PMIDS_FILE = "data/posted_pmids.json"


def validate() -> None:
    """必須環境変数のチェック"""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not DISCORD_WEBHOOK_URL:
        missing.append("DISCORD_WEBHOOK_URL")
    if missing:
        raise RuntimeError(
            f"必須の環境変数が設定されていません: {', '.join(missing)}\n"
            f".env ファイルまたは GitHub Secrets を確認してください。"
        )

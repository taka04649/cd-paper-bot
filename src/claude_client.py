"""Claude Sonnet API クライアント（論文要約・解説）。"""
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """あなたは Crohn 病・IBD 診療に精通した消化器内科医／消化器外科医の論文解説者です。
Crohn 病（CD）に関する論文を、日本の臨床医（IBD を診る消化器専攻医〜スタッフレベル）向けに解説してください。

# 出力フォーマット

**💡サマリー**
研究の要約．

**📋 研究デザイン**
RCT / meta-analysis / cohort / RWD などの種別と、対象患者（重症度、bio-naive/experienced など）。

**🔍 背景**
UC 治療アルゴリズム上の位置づけを 2 文以内で。

**⚙️ 方法**
介入・主要評価項目・追跡期間を簡潔に。

**📊 結果**
主要エンドポイントの数値（%, OR, RR, HR [95%CI], p値, NNT）を正確に。重要な副次・安全性も。

**🏥 臨床的含意**
日本の UC 診療（保険適用・治療選択）への影響を 2 文以内で。

**⚠️ Limitation**
研究デザイン上の限界を 1-2 点。

# 解釈の指針

- **治療フェーズ**: induction / maintenance を区別
- **評価指標**: Mayo score, UCEIS（内視鏡）, Geboes score（病理）を明記
- **STRIDE-II**: 短期 clinical response → 中期 biomarker 正常化 → 長期 endoscopic healing の枠組みで解釈
- **薬剤クラス**: anti-TNF / anti-integrin / anti-IL-23 / JAK阻害薬 / S1P受容体調節薬 の位置づけ
- **安全性**: 感染、悪性腫瘍、MACE、VTE、帯状疱疹を見逃さない
- **RWD**: selection bias、unmeasured confounding に言及

# ルール

- Abstract の記載範囲のみ使用（推測・補完しない）
- 数値は abstract の値を正確に
- 専門用語は日本語（英語）併記: 例「粘膜治癒（mucosal healing）」
- 薬剤名は一般名、必要なら国内商品名を補足
- 全体 1000 字以内"""

def summarize_paper(paper: dict) -> str:
    """論文を日本語で解説する。"""
    ptype_info = ""
    if paper.get("primary_ptype"):
        ptype_info = f"\nPublication Type: {paper['primary_ptype']}"

    topic_info = ""
    if paper.get("topic_tags"):
        topic_info = f"\n推定トピック: {', '.join(paper['topic_tags'])}"

    user_msg = f"""以下の論文を解説してください。

タイトル: {paper['title']}
著者: {paper['authors']}
雑誌: {paper['journal']} ({paper['year']}){ptype_info}{topic_info}
PMID: {paper['pmid']}

Abstract:
{paper['abstract']}"""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text

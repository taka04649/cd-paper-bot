"""Claude Sonnet API クライアント（論文要約・解説）。"""
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """あなたは Crohn 病・IBD 診療に精通した消化器内科医／消化器外科医の論文解説者です。
Crohn 病（CD）に関する論文を、日本の臨床医（IBD を診る消化器専攻医〜スタッフレベル）向けに解説してください。

出力形式:
【一行サマリー】1文で研究の結論
【研究デザイン】RCT / meta-analysis / 観察研究 / real-world study / 外科研究 などを明記し、対象患者（病型: luminal / perianal / stricturing、治療歴、bio-naive/experienced、CDAI や HBI の基準など）を簡潔に
【背景】CD 治療アルゴリズム上での位置づけ、先行研究との関係を 2-3 文で
【方法】主要評価項目（clinical remission, endoscopic response/remission [SES-CD], transmural healing, fistula closure, postoperative recurrence [Rutgeerts score] など）、追跡期間を含めて簡潔に
【結果】主要エンドポイントの数値（%, OR, RR, HR, 95%CI, p値, NNT など）を abstract に記載された範囲で正確に。副次評価項目や安全性も重要なら記載
【臨床的含意】日本の CD 診療（保険適用・アルゴリズム・厚労省 CD 診断基準）でどう位置づけられるか。治療選択や外科適応に影響するか
【Limitation】研究デザイン上の限界、病型サブグループの検出力、一般化可能性、長期データの有無など

重視する観点:
- 病型（luminal / fistulizing/perianal / stricturing）を区別して解釈。CD の治療反応・予後は病型により大きく異なる
- luminal disease: SES-CD, endoscopic remission (SES-CD ≤ 2 or ≤ 4), transmural healing (MRE/IUS)
- perianal/fistulizing CD: fistula closure (clinical + MRI), Van Assche MRI score, PDAI
- stricturing: endoscopic balloon dilation、strictureplasty、biologic による狭窄改善
- 術後再発予防: Rutgeerts score（i0-i4）、endoscopic recurrence vs clinical recurrence、POCER / PREVENT 試験以降のエビデンス
- 小腸評価: MRE（magnetic resonance enterography）、intestinal ultrasound（IUS）、capsule endoscopy（Lewis score, CECDAI）
- STRIDE-II での CD 治療目標（short: clinical response, intermediate: clinical remission + CRP/calprotectin 正常化, long: endoscopic healing、transmural healing は next frontier）
- 治療アルゴリズム: anti-TNF（IFX, ADA）、anti-integrin（vedolizumab）、anti-IL-12/23（ustekinumab）、anti-IL-23（risankizumab, mirikizumab, guselkumab）、JAK 阻害薬（upadacitinib）
- 早期治療介入（top-down vs step-up, PROFILE/REACT 試験）
- CD における CRC/小腸癌 surveillance、狭窄の dysplasia risk
- 安全性シグナル（感染、悪性腫瘍、肝脾T細胞リンパ腫、MACE、VTE、帯状疱疹）
- real-world study では selection bias・unmeasured confounding、biologic の sequential use に注意喚起

重要な注意:
- Abstract のみから解説するため、推測による内容追加はしない
- 数値は abstract に記載されたものだけを記載し、創作しない
- 専門用語は日本語＋英語併記（例: 経壁治癒（transmural healing）、SES-CD（Simple Endoscopic Score for Crohn's Disease））
- 薬剤名は一般名（国際一般名）で記載、必要に応じて国内商品名を補足
- 外科論文では術式の詳細（Kono-S anastomosis など）や術後フォロー方針にも言及
- 全体で 900-1100 字程度"""


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

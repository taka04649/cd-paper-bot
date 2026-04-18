# CD Paper Bot

PubMed から Crohn 病（CD）関連の新着論文を自動取得し、Claude Sonnet で日本語解説を生成して Discord に投稿する bot です。

- **実行基盤**: GitHub Actions（cron 実行）
- **API**: PubMed E-utilities（無料）+ Anthropic Claude Sonnet 4.5
- **想定コスト**: 約 **$3〜6 / 月**（6 論文/日の場合）

## UC bot 版との違い

CD は UC と病態・治療・評価指標が大きく異なるため、以下の点を特化させています:

| 項目 | UC bot | CD bot |
|---|---|---|
| 対象疾患 | 潰瘍性大腸炎 | Crohn 病 |
| 病型タグ抽出 | なし | **luminal / perianal / stricturing / postop / imaging など自動分類** |
| 解説の焦点 | STRIDE-II、粘膜治癒、Mayo/UCEIS | **病型別治療、SES-CD、transmural healing、Rutgeerts score** |
| 画像評価 | 大腸内視鏡中心 | **MRE、IUS、capsule endoscopy も重視** |
| 外科的観点 | 手術は稀 | **術後再発予防、Kono-S、strictureplasty 等も対象** |
| ジャーナル | 消化器系中心 | **消化器系 + Dis Colon Rectum、Ann Surg 等の外科誌も含む** |
| ヘッダー | 研究タイプ内訳 | **研究タイプ + 病型内訳も表示** |

---

## CD 病型タグ機能

タイトル・abstract から以下のトピックを自動判定し、Discord embed に表示します:

| タグ | 判定キーワード |
|---|---|
| 🕳️ Perianal/Fistulizing | perianal, fistula, seton, rectal fistula |
| 🔒 Stricturing | stricture, stenosis, balloon dilation, strictureplasty |
| 🔪 Postoperative/Surgical | postoperative recurrence, ileocolic resection, anastomosis |
| 🖼️ Imaging (MRE/IUS) | MRE, intestinal ultrasound, capsule endoscopy |
| 🧫 Microbiome/Diet | microbiota, microbiome, enteral nutrition, CDED |
| 💊 Biologic/Small molecule | ustekinumab, vedolizumab, risankizumab, upadacitinib など |
| 🧬 Genetics/Biomarker | NOD2, GWAS, calprotectin, biomarker |
| 👶 Pediatric | pediatric, children, adolescent |

これにより、フィード内で「今日は perianal の RCT が来てる」などが一目でわかります。

---

## 構成

```
cd-paper-bot/
├── .github/
│   └── workflows/
│       └── daily_digest.yml     # GitHub Actions: 毎朝 JST 07:00 に実行
├── src/
│   ├── main.py                  # エントリポイント
│   ├── config.py                # 設定・検索クエリ
│   ├── pubmed_client.py         # PubMed API（病型タグ推定機能付き）
│   ├── claude_client.py         # Claude Sonnet API（CD 特化プロンプト）
│   └── discord_client.py        # Discord Webhook（病型タグ表示）
├── data/
│   └── posted_pmids.json        # 投稿済み PMID 管理
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 導入手順

### 1. Discord Webhook の作成

1. Discord で投稿先のサーバー／チャンネルを開く
2. チャンネル右の歯車アイコン（チャンネル編集）→ **連携サービス** → **ウェブフック**
3. **新しいウェブフック** をクリック → 名前を設定（例: `CD Paper Bot`）
4. **ウェブフック URL をコピー** ボタンで URL を控える

> 💡 appendix / UC / CD それぞれ **別チャンネル** を作ると情報が整理されて追いやすくなります。

### 2. Anthropic API キーの取得

既存の appendix / UC bot と同じ API キーで OK です。Usage はキー単位で集計されます。

新規発行する場合:

1. <https://console.anthropic.com/> にログイン
2. **API Keys** → **Create Key**
3. **Billing** で支払い方法を登録し、$10〜20 をチャージ
4. **Usage limits** で月額上限を設定（3 bot 合算で $15〜18 程度が目安）

### 3. PubMed API キー（任意・推奨）

他 bot と同じキーを使い回せます。

### 4. GitHub リポジトリの作成

別リポジトリとして作成を推奨:

```bash
cd cd-paper-bot
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/cd-paper-bot.git
git push -u origin main
```

### 5. GitHub Secrets の登録

| Secret 名 | 値 | 必須 |
|---|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | ✅ |
| `DISCORD_WEBHOOK_URL` | CD 用チャンネルの Webhook | ✅ |
| `PUBMED_API_KEY` | NCBI で発行したキー | 任意 |
| `PUBMED_EMAIL` | 自分のメールアドレス | 任意 |

### 6. 初回実行テスト

1. リポジトリの **Actions** タブへ移動
2. **Daily CD Paper Digest** を選択
3. **Run workflow** で手動実行
4. Discord に論文解説が流れてくれば成功 🎉

---

## ローカル動作確認（任意）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .env を編集して API キー等を記入

python src/main.py
```

---

## カスタマイズ

### 検索クエリの変更

`src/config.py` の `PUBMED_QUERY` を編集します。

- **IBD 全般（UC も含める）**:
  ```python
  '"inflammatory bowel diseases"[MeSH Terms]'
  ```

- **瘻孔性/肛門病変に絞る**:
  ```python
  '("Crohn Disease"[MeSH]) AND '
  '("rectal fistula"[MeSH] OR "perianal"[tiab] OR "fistulizing"[tiab] OR "seton"[tiab])'
  ```

- **狭窄・術後再発に絞る**:
  ```python
  '("Crohn Disease"[MeSH]) AND '
  '("intestinal strictures"[tiab] OR "postoperative recurrence"[tiab] OR '
  '"Rutgeerts"[tiab] OR "Kono-S"[tiab])'
  ```

- **小腸画像・新規評価法**:
  ```python
  '("Crohn Disease"[MeSH]) AND '
  '("magnetic resonance enterography"[tiab] OR "MRE"[tiab] OR '
  '"intestinal ultrasound"[tiab] OR "transmural healing"[tiab])'
  ```

- **腸内細菌/メタゲノム関連**（大学院研究テーマ候補）:
  ```python
  '"Crohn Disease"[MeSH] AND '
  '("gut microbiota"[MeSH] OR "microbiome"[Title/Abstract] OR '
  '"metagenomics"[Title/Abstract] OR "WGS"[Title/Abstract])'
  ```

- **小児 CD のみ**:
  ```python
  '"Crohn Disease"[MeSH] AND ("child"[MeSH] OR "pediatric"[tiab] OR "adolescent"[MeSH])'
  ```

### 実行頻度の変更

`.github/workflows/daily_digest.yml` の `cron` を編集:

| 用途 | cron 式 (UTC) | JST |
|---|---|---|
| 毎朝 7:00（デフォルト） | `0 22 * * *` | 毎日 07:00 |
| 週1（月曜朝） | `0 22 * * 1` | 月曜 07:00 |
| 平日のみ | `0 22 * * 1-5` | 平日 07:00 |

### 病型タグのカスタマイズ

`src/pubmed_client.py` の `CD_TOPIC_TAGS` リストを編集することで、判定するトピックや優先順位を変更できます。例えば、鷹将さんの関心に応じて以下を追加:

```python
("🔬 Genomics/WES/WGS",
 [r"\bwhole[- ]exome", r"\bwhole[- ]genome", r"\bexome sequenc", r"\bWES\b", r"\bWGS\b"]),
```

### 処理本数の変更

`src/config.py` の `MAX_PAPERS_PER_RUN` を変更。デフォルト 6。

### 解説の深さ変更

`src/claude_client.py` の `SYSTEM_PROMPT` を編集。外科論文を多く扱う場合は外科テクニックへの言及を増やすなど、関心に応じて調整可能です。

---

## コスト試算

Claude Sonnet 4.5 で概算:

| 項目 | 使用量/日 | 月額 |
|---|---|---|
| 入力トークン（abstract + prompt、6 論文/日） | ~7,500 tok | ~$0.68 |
| 出力トークン（日本語解説、6 論文/日） | ~5,500 tok | ~$2.48 |
| **合計** | | **~$3.16/月** |

### 3 bot 運用時の合算

| Bot | 月額 |
|---|---|
| Appendix | ~$2.25 |
| UC | ~$3.10 |
| CD | ~$3.16 |
| **合計** | **~$8.50/月** |

$20 予算の半分以下で 3 領域をカバーできます。

---

## 論文タイプ別の色分け（UC bot と共通）

| タイプ | 色 | バッジ |
|---|---|---|
| RCT | 🟢 緑 | 🎯 RCT |
| Meta-Analysis / Systematic Review | 🔵 青 | 📊 / 📚 |
| Phase III Trial | 🟢 濃い緑 | 💊 Phase III Trial |
| Multicenter Study | 🟣 紫 | 🏥 Multicenter |
| Observational Study | 🟠 オレンジ | 👁️ Observational |
| Review | ⚪ グレー | 📖 Review |
| Case Report | 🔴 赤 | 📝 Case Report |

---

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| Actions で `Missing ANTHROPIC_API_KEY` エラー | Secrets が正しく登録されているか確認 |
| Discord に何も投稿されない | Webhook URL が正しいか、チャンネル権限を確認 |
| `posted_pmids.json` が commit されない | Settings → Actions → General → Workflow permissions で **Read and write permissions** を有効化 |
| 論文が全部既読判定される | `data/posted_pmids.json` を空配列 `[]` にリセット |
| PubMed から 429 エラー | `PUBMED_API_KEY` を設定するか、実行頻度を下げる |
| 病型タグが付かない | abstract にキーワードが含まれていない場合は付かない（仕様）。`CD_TOPIC_TAGS` のパターンを追加・調整 |

---

## 発展案

CD bot 特有のアイデア:

- **外科 Journal Club bot**: Dis Colon Rectum / Ann Surg / JACS に絞った外科特化版
- **Fistula surveillance bot**: perianal CD 論文だけをフォローする専用 instance
- **Postoperative recurrence tracker**: 術後再発予防（Rutgeerts score, Kono-S anastomosis）に特化
- **Biosimilar watcher**: IFX/ADA バイオシミラーのスイッチング研究を追跡
- **IUS (Intestinal Ultrasound) bot**: 最近注目されている腸管エコー研究に特化（日本での普及途上）
- **Transmural healing bot**: MRE/IUS による transmural healing の概念・エビデンスを集中的に追跡

---

## ライセンス

MIT

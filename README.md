# Slack Daily Report AI 📊

Slack に投稿したメッセージを自動で読み取り、Amazon Bedrock Claude AI を使って日報を生成するツールです。

## 🌟 特徴

- **自動メッセージ収集**: 参加している全チャンネルから今日のメッセージを自動取得
- **AI による要約**: Amazon Bedrock Claude AI を使用して業務概要を生成
- **構造化された出力**: Markdown 形式のリストで読みやすい日報を生成
- **外部プロンプトテンプレート**: 外部ファイルから読み込み可能で管理しやすい
- **複数テンプレート対応**: 標準・ずんだもん風・シンプルの 3 種類のプロンプトテンプレートを付属
- **可愛い口調**: ずんだもん風の親しみやすい口調で日報を作成
- **複数出力対応**: Slack チャンネルへの投稿またはファイル保存が可能

## 📋 必要な環境

### Python

- Python 3.9 以上（推奨: Python 3.11 以上）
- 必要なライブラリ:
  ```bash
  pip install -r requirements.txt
  ```

**注意**: Python 3.7/3.8 はサポートが終了しているため、セキュリティとパフォーマンスの観点から Python 3.9 以上を使用してください。

### AWS

- AWS アカウント
- Amazon Bedrock へのアクセス権限
- リージョン: us-east-1 (バージニア北部)

### Slack

- Slack App の作成
- Bot Token の取得
- 必要なスコープの設定

## 🚀 セットアップ

### 1. Slack App の作成

1. [Slack API](https://api.slack.com/apps) にアクセス
2. "Create New App" をクリック
3. "From scratch" を選択
4. アプリ名とワークスペースを設定

### 2. Bot Token Scopes の設定

`OAuth & Permissions` → `Bot Token Scopes` で以下のスコープを追加：

- `channels:read` - パブリックチャンネル一覧の取得
- `groups:read` - プライベートチャンネル一覧の取得
- `channels:history` - パブリックチャンネルの履歴取得
- `groups:history` - プライベートチャンネルの履歴取得
- `chat:write` - メッセージの投稿
- `conversations:read` - チャンネル情報の取得（チャンネル ID 検証用）

### 3. Bot のインストール

1. `OAuth & Permissions` → `Install to Workspace` をクリック
2. Bot User OAuth Token (`xoxb-` で始まる文字列) をコピー

### 4. 環境変数の設定

#### 方法 1: .env ファイルを使用（推奨）

1. プロジェクトルートに`.env`ファイルを作成:

   ```bash
   touch .env
   ```

2. `.env`ファイルを作成（`.env.example`をベースに使用）:

   ```bash
   # .env.exampleをコピーして作成
   cp .env.example .env

   # エディタで編集
   nano .env  # または vim .env, code .env など
   ```

   または、手動で作成する場合は以下の内容を記述:

   ```bash
   # ==================================================
   # 環境変数設定ファイル
   # ==================================================

   # Slack設定（必須）
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_USER_ID=U1234567890
   SLACK_SUMMARY_CHANNEL_ID=C1234567890

   # AWS設定（必須）
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_DEFAULT_REGION=us-east-1

   # オプション設定
   DEFAULT_OUTPUT=file
   CHARACTER_NAME=AI
   CHARACTER_TONE=丁寧語
   CHARACTER_DESCRIPTION=親しみやすいAIアシスタント

   # プロンプトテンプレートファイル指定（省略可）
   # PROMPT_TEMPLATE_FILE=templates/prompt_template_zundamon.txt
   ```

3. 実際の値に置き換え:
   - `SLACK_BOT_TOKEN`: 実際の Slack Bot Token
   - `SLACK_USER_ID`: あなたの Slack User ID
   - `SLACK_SUMMARY_CHANNEL_ID`: 投稿先チャンネル ID
   - AWS 認証情報: 実際の値（または削除して CLI 認証を使用）
   - キャラクター設定: お好みのキャラクターに変更

#### 方法 2: 環境変数を直接設定

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_USER_ID="U1234567890"  # あなたのSlackユーザーID

# Slackに投稿する場合のみ設定（実行時に入力することも可能）
export SLACK_SUMMARY_CHANNEL_ID="C1234567890"  # 日報投稿先チャンネルID
```

**注意**:

- `SLACK_SUMMARY_CHANNEL_ID`が設定されていない場合、Slack 投稿を選択した際に実行時にチャンネル ID の入力を求められます。
- `DEFAULT_OUTPUT`を設定すると、コマンドライン引数が指定されていない場合のデフォルトの出力先になります。

### 5. AWS 認証情報の設定

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

または、AWS CLI を使用:

```bash
aws configure
```

### 6. ファイル構成

セットアップ完了後のプロジェクト構成は以下のようになります：

```
slack-daily-report-ai/
├── slack_daily_report.py          # メインプログラム
├── requirements.txt               # 必要なパッケージ
├── README.md                      # このファイル
├── .env                          # 環境変数設定（作成が必要）
├── .env.example                  # 環境変数設定例
├── .gitignore                    # Git除外設定
├── templates/                    # プロンプトテンプレートファイル
│   ├── prompt_template.txt       # デフォルトプロンプトテンプレート
│   ├── prompt_template_zundamon.txt  # ずんだもん風プロンプトテンプレート
│   └── prompt_template_simple.txt   # シンプルプロンプトテンプレート
└── docs/                         # ドキュメントファイル
    └── README_PROMPT_TEMPLATES.md   # プロンプトテンプレートの詳細説明
```

## 💫 使い方

### 基本的な使用方法

```bash
# デフォルト設定で実行（prompt_template.txtを使用）
python slack_daily_report.py

# コマンドライン引数で出力先を指定
python slack_daily_report.py --output slack    # Slackに投稿
python slack_daily_report.py --output file     # ファイルに保存
python slack_daily_report.py -o slack          # 短縮形

# 実行時に出力先を選択（DEFAULT_OUTPUTが未設定の場合）
python slack_daily_report.py
```

### プロンプトテンプレートファイルの使用方法

#### 付属のプロンプトテンプレートファイル

本ツールには 3 種類のプロンプトテンプレートファイルが付属しています：

- **`prompt_template.txt`** - 標準的な日報形式（デフォルト）
- **`prompt_template_zundamon.txt`** - ずんだもん風の可愛い口調
- **`prompt_template_simple.txt`** - シンプルで簡潔な形式

#### 使用方法

```bash
# デフォルト（prompt_template.txt）
python slack_daily_report.py

# ずんだもん風で生成
PROMPT_TEMPLATE_FILE=templates/prompt_template_zundamon.txt python slack_daily_report.py

# シンプル形式で生成
PROMPT_TEMPLATE_FILE=templates/prompt_template_simple.txt python slack_daily_report.py

# .envファイルで設定
echo "PROMPT_TEMPLATE_FILE=templates/prompt_template_zundamon.txt" >> .env
python slack_daily_report.py
```

#### プロンプトテンプレートの読み込み優先順位

1. **環境変数 `PROMPT_TEMPLATE`**（直接指定）
2. **環境変数 `PROMPT_TEMPLATE_FILE`**（ファイル指定）
3. **外部ファイル `templates/prompt_template.txt`**（デフォルト）
4. **コード内蔵のデフォルトプロンプトテンプレート**

### 実行結果

1. 参加している全チャンネルから今日のメッセージを取得
2. Claude AI が業務概要を生成
3. 結果をコンソールに表示
4. 選択した出力先に結果を保存/投稿
   - **Slack 投稿**: 指定したチャンネルに投稿
   - **ファイル保存**: `daily_summary_YYYY-MM-DD.txt` ファイルに保存
   - **デフォルト出力**: `.env`ファイルの`DEFAULT_OUTPUT`設定を使用

### 出力先の選択方法

#### 1. デフォルトの出力先を使用

`.env`ファイルで`DEFAULT_OUTPUT`を設定すると、自動的に使用されます：

```
💡 デフォルトの出力先を使用: file
```

#### 2. コマンドライン引数で指定

```bash
python slack_daily_report.py --output slack
```

#### 3. 実行時に選択

引数を指定せず、デフォルトの出力先も設定されていない場合、実行時に選択画面が表示されます：

```
📤 出力先を選択してください：
1. Slackチャンネルに投稿
2. ファイルに保存
選択してください (1/2): 1

❌ SLACK_SUMMARY_CHANNEL_ID が設定されていません
   投稿先のチャンネルIDを入力してください
   （例：C1234567890 または #general）
   ※ チャンネルIDの確認方法はREADMEを参照してください
チャンネルID: C1234567890
💡 チャンネルIDを確認中: C1234567890
✅ チャンネル確認: #general
```

### 出力例

```
📈日次業務概要 (生成日時: 2024-01-15 18:30)
メッセージ数: 23件
対象チャンネル: #development, #general, #project-a

1. 主要な作業内容:
• プロジェクトAのAPIドキュメント作成を進められました。技術文書の整備は重要な作業ですね！
• データベース設計の見直しを行われたようです。システムの基盤強化に取り組まれて素晴らしいです。
• チームミーティングでスケジュール調整をされました。チームワークを大切にされているのが伝わります。

2. 今後の予定や課題:
• 明日までにテストケースを作成する必要があります。品質向上への取り組みが素晴らしいです。
• 来週のリリースに向けて最終確認を行う予定です。着実にプロジェクトを進められていますね。

本日もお疲れ様でした！
```

## 🔧 設定のカスタマイズ

### ユーザー ID の確認方法

Slack 上で以下のいずれかの方法で確認できます：

1. **プロフィール確認**:

   - 自分のプロフィールをクリック
   - 「その他」→「メンバー ID をコピー」

2. **API で確認**:
   ```bash
   curl -H "Authorization: Bearer YOUR_BOT_TOKEN" \
        "https://slack.com/api/users.lookupByEmail?email=your@email.com"
   ```

### チャンネル ID の確認方法

1. Slack でチャンネルを開く
2. チャンネル名をクリック
3. 下部に表示されるチャンネル ID をコピー

### キャラクター設定のカスタマイズ

#### 基本設定

| 設定項目                | 説明               | 例                                                   |
| ----------------------- | ------------------ | ---------------------------------------------------- |
| `CHARACTER_NAME`        | キャラクター名     | "AI", "アシスタント", "ずんだもん"                   |
| `CHARACTER_TONE`        | 口調・話し方       | "丁寧語", "関西弁", "〜なのだ"                       |
| `CHARACTER_DESCRIPTION` | キャラクターの特徴 | "親しみやすい AI", "関西弁の AI", "可愛いマスコット" |

#### キャラクター設定例

##### 標準的な AI

```bash
CHARACTER_NAME=AI
CHARACTER_TONE=丁寧語
CHARACTER_DESCRIPTION=親しみやすいAIアシスタント
```

##### ずんだもん風

```bash
CHARACTER_NAME=ずんだもん
CHARACTER_TONE=〜なのだ、〜のだ
CHARACTER_DESCRIPTION=可愛いマスコットキャラクター
```

##### 関西弁 AI

```bash
CHARACTER_NAME=関西AI
CHARACTER_TONE=関西弁
CHARACTER_DESCRIPTION=関西弁で話す親しみやすいAI
```

#### デフォルトプロンプトテンプレート

`PROMPT_TEMPLATE`や`PROMPT_TEMPLATE_FILE`を設定しない場合は、`templates/prompt_template.txt`ファイルが自動的に読み込まれます。ファイルが存在しない場合は、以下のコード内蔵のデフォルトプロンプトが使用されます：

```
以下は今日のSlackでの業務メッセージです。これらのメッセージを分析して、以下の形式で業務概要を作成してください。

メッセージ内容:
{messages}

以下の形式で出力してください：

📈日次業務概要 (生成日時: {current_datetime})
メッセージ数: {message_count}件
対象チャンネル: {channel_list}

1. 主要な作業内容:
• [具体的な作業内容を自然な文章で説明。「〜されました」「〜のようです」など丁寧な敬語で]
• [具体的な作業内容を自然な文章で説明。感想やコメントも含める]
• [具体的な作業内容を自然な文章で説明。励ましや評価も含める]

2. 今後の予定や課題:
• [予定や課題を自然な文章で説明。「〜予定です」「〜する必要があります」など]
• [予定や課題を自然な文章で説明。応援メッセージも含める]

本日もお疲れ様でした！

{character_name}として、{character_tone}で回答してください。箇条書きは「•」を使用し、自然で丁寧な文章で説明してください。
```

#### カスタムプロンプトテンプレート

プロンプトテンプレートをカスタマイズする方法は 2 つあります：

##### 方法 1: プロンプトテンプレートファイルを作成（推奨）

1. 新しいファイルを作成（例: `my_prompt_template.txt`）
2. 使用可能な変数を使用してプロンプトを記述
3. 環境変数で指定

```bash
# .envファイルで設定
PROMPT_TEMPLATE_FILE=my_prompt_template.txt

# またはコマンドラインで指定
PROMPT_TEMPLATE_FILE=my_prompt_template.txt python slack_daily_report.py
```

##### 方法 2: 環境変数で直接指定

```bash
# .envファイルで設定
PROMPT_TEMPLATE="独自のプロンプトテンプレート文字列"
```

##### 使用可能な変数

- `{messages}` - 分析対象のメッセージ
- `{current_datetime}` - 現在の日時（YYYY-MM-DD HH:MM）
- `{message_count}` - メッセージ数
- `{channel_list}` - 対象チャンネル一覧
- `{character_name}` - キャラクター名
- `{character_tone}` - キャラクターの口調
- `{character_description}` - キャラクターの説明

##### カスタムプロンプトテンプレートファイルの例

```
今日のSlackメッセージを分析します。

メッセージ: {messages}

## 📋 業務レポート ({current_datetime})

**統計情報**
- メッセージ数: {message_count}件
- 対象チャンネル: {channel_list}

**今日の作業**
- 作業内容1
- 作業内容2

**明日の予定**
- 予定1
- 予定2

---
Generated by {character_name}
```

詳細については、[プロンプトテンプレートファイルの使用方法](docs/README_PROMPT_TEMPLATES.md)を参照してください。

## 📝 注意事項

- **レート制限**: Slack API のレート制限に注意してください
- **プライバシー**: 個人情報を含むメッセージの取り扱いに注意
- **費用**: Amazon Bedrock の使用料金が発生します
- **Bot 権限**: Bot が各チャンネルに招待されている必要があります

## 🐛 トラブルシューティング

### よくあるエラー

1. **`missing_scope` エラー**:

   - Bot Token Scopes が正しく設定されているか確認
   - アプリを再インストール

2. **`not_in_channel` エラー**:

   - Bot がチャンネル I に招待されているか確認

3. **AWS 認証エラー**:
   - AWS 認証情報が正しく設定されているか確認
   - Bedrock へのアクセス権限があるか確認

### デバッグ方法

コード内にデバッグ情報が含まれているため、実行時のログを確認してください。

## 🤝 コントリビューション

プルリクエストや Issue の報告をお待ちしています！

## 📄 ライセンス

MIT License

## 🙏 謝辞

- [Slack API](https://api.slack.com/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Claude AI](https://www.anthropic.com/)

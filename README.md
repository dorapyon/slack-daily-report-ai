# Slack Daily Report AI 📊

Slack に投稿したメッセージを自動で読み取り、Amazon Bedrock Claude AI を使って日報を生成するツールです。

## 🌟 特徴

- **自動メッセージ収集**: 参加している全チャンネルから今日のメッセージを自動取得
- **AI による要約**: Amazon Bedrock Claude AI を使用して業務概要を生成
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

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_USER_ID="U1234567890"  # あなたのSlackユーザーID

# Slackに投稿する場合のみ設定（実行時に入力することも可能）
export SLACK_SUMMARY_CHANNEL_ID="C1234567890"  # 日報投稿先チャンネルID
```

**注意**: `SLACK_SUMMARY_CHANNEL_ID`が設定されていない場合、Slack 投稿を選択した際に実行時にチャンネル ID の入力を求められます。

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

## 💫 使い方

### 基本的な使用方法

```bash
# 実行時に出力先を選択
python slack_daily_report.py

# コマンドライン引数で出力先を指定
python slack_daily_report.py --output slack    # Slackに投稿
python slack_daily_report.py --output file     # ファイルに保存
python slack_daily_report.py -o slack          # 短縮形
```

### 実行結果

1. 参加している全チャンネルから今日のメッセージを取得
2. Claude AI が業務概要を生成
3. 結果をコンソールに表示
4. 選択した出力先に結果を保存/投稿
   - **Slack 投稿**: 指定したチャンネルに投稿
   - **ファイル保存**: `daily_summary_YYYY-MM-DD.txt` ファイルに保存

### 出力先の選択方法

#### 1. コマンドライン引数で指定

```bash
python slack_daily_report.py --output slack
```

#### 2. 実行時に選択

引数を指定しない場合、実行時に選択画面が表示されます：

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
📊 **日次業務概要** (2024-01-15)
メッセージ数: 23件
生成日時: 2024-01-15 18:30:00

こんにちはなのだ！今日の業務概要をまとめたのだ。

**主要な作業内容:**
- プロジェクトAのAPIドキュメント作成を進めたのだ
- データベース設計の見直しを行ったのだ
- チームミーティングでスケジュール調整をしたのだ

**今後の予定や課題:**
- 明日までにテストケースを作成する必要があるのだ
- 来週のリリースに向けて最終確認をする予定なのだ

お疲れ様でしたなのだ！
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

#!/usr/bin/env python3
"""
Slack Daily Report AI

Slackに投稿したメッセージを自動で読み取り、Amazon Bedrock Claude AIを使って日報を生成するツールです。

必要な環境変数:
- SLACK_BOT_TOKEN: SlackのBotトークン
- SLACK_USER_ID: あなたのSlackユーザーID
- SLACK_SUMMARY_CHANNEL_ID: 日報投稿先チャンネルID（オプション）
- AWS認証情報: Amazon Bedrock用
"""

import os
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()


class SlackMessageFetcher:
    """Slackからメッセージを取得し、投稿を行うクラス"""
    
    def __init__(self, token: str, user_id: str):
        self.token = token
        self.user_id = user_id
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """参加チャンネル一覧を取得"""
        url = f"{self.base_url}/users.conversations"
        params = {
            "types": "public_channel,private_channel",
            "limit": 1000,
            "exclude_archived": True,
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        time.sleep(0.5)  # レート制限対策
        
        if not data.get("ok"):
            error_message = data.get('error', '不明なエラー')
            if error_message == "missing_scope":
                raise Exception("""
必要なSlackスコープが不足しています。
以下のスコープをSlack Appに追加してください：
- channels:read
- groups:read
- channels:history
- groups:history
- chat:write
- conversations:read
""")
            raise Exception(f"Slack API エラー: {error_message}")
        
        return data.get("channels", [])
    
    def get_messages_from_channel(self, channel_id: str, oldest: float, latest: float) -> List[Dict[str, Any]]:
        """特定チャンネルからメッセージを取得"""
        url = f"{self.base_url}/conversations.history"
        params = {
            "channel": channel_id,
            "oldest": oldest,
            "latest": latest,
            "limit": 1000
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("ok"):
            error_message = data.get('error', '不明なエラー')
            if error_message == "missing_scope":
                raise Exception("チャンネル履歴の取得に必要なスコープが不足しています")
            raise Exception(f"Slack API エラー: {error_message}")
        
        messages = data.get("messages", [])
        return [msg for msg in messages if msg.get("user") == self.user_id]
    
    def get_daily_messages(self, target_date: datetime = None) -> List[Dict[str, Any]]:
        """指定日の全メッセージを取得"""
        if target_date is None:
            target_date = datetime.now()
        
        print(f"📅 {target_date.strftime('%Y年%m月%d日')} のメッセージを取得中...")
        
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        oldest = start_of_day.timestamp()
        latest = end_of_day.timestamp()
        
        all_messages = []
        channels = self.get_channels()
        
        print(f"🔄 {len(channels)} 個のチャンネルを処理中...")
        
        for channel in channels:
            channel_id = channel["id"]
            channel_name = channel.get("name", "Unknown")
            
            try:
                messages = self.get_messages_from_channel(channel_id, oldest, latest)
                
                for message in messages:
                    message["channel_name"] = channel_name
                    all_messages.append(message)
                
                if messages:
                    print(f"   ✅ #{channel_name}: {len(messages)} 件")
                
                time.sleep(0.1)  # レート制限対策
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Too Many Requests" in error_str:
                    print(f"   ⚠️ #{channel_name}: レート制限エラー、スキップ")
                    time.sleep(1)
                elif "not_in_channel" in error_str:
                    print(f"   ⚠️ #{channel_name}: ボット未参加、スキップ")
                else:
                    print(f"   ⚠️ #{channel_name}: エラー発生、スキップ")
                continue
        
        print(f"✅ 合計 {len(all_messages)} 件のメッセージを取得")
        return all_messages
    
    def validate_channel_id(self, channel_id: str) -> bool:
        """チャンネルIDの有効性をチェック"""
        try:
            # チャンネル情報を取得してIDの有効性をチェック
            url = f"{self.base_url}/conversations.info"
            params = {"channel": channel_id}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            time.sleep(0.1)  # レート制限対策
            
            if data.get("ok"):
                channel_info = data.get("channel", {})
                channel_name = channel_info.get("name", "Unknown")
                print(f"✅ チャンネル確認: #{channel_name}")
                return True
            else:
                error_message = data.get('error', '不明なエラー')
                if error_message == "channel_not_found":
                    print(f"❌ チャンネルが見つかりません: {channel_id}")
                elif error_message == "not_in_channel":
                    print(f"❌ ボットがチャンネルに参加していません: {channel_id}")
                    print("   ボットをチャンネルに招待してください")
                else:
                    print(f"❌ チャンネルエラー: {error_message}")
                return False
                
        except Exception as e:
            print(f"❌ チャンネル確認エラー: {e}")
            return False

    def post_message(self, channel_id: str, text: str) -> bool:
        """Slackチャンネルにメッセージを投稿"""
        url = f"{self.base_url}/chat.postMessage"
        data = {
            "channel": channel_id,
            "text": text,
            "username": "日報Bot",
            "icon_emoji": ":robot_face:"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if not result.get("ok"):
                print(f"❌ Slack投稿エラー: {result.get('error', '不明なエラー')}")
                return False
            
            print("✅ Slackへの投稿完了")
            time.sleep(0.5)  # レート制限対策
            return True
            
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return False


class BedrockSummarizer:
    """Amazon Bedrockを使用して業務概要を生成するクラス"""
    
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name="us-east-1")
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
        
        # AWS認証確認
        try:
            sts_client = boto3.client("sts", region_name="us-east-1")
            identity = sts_client.get_caller_identity()
            print(f"🔐 AWS認証確認 - アカウントID: {identity.get('Account')}")
        except Exception as e:
            print(f"⚠️ AWS認証エラー: {e}")
    
    def format_messages_for_analysis(self, messages: List[Dict[str, Any]]) -> str:
        """メッセージを分析用形式に変換"""
        formatted_messages = []
        
        for message in messages:
            timestamp = datetime.fromtimestamp(float(message.get("ts", 0)))
            channel = message.get("channel_name", "Unknown")
            text = message.get("text", "")
            
            formatted_line = f"[{timestamp.strftime('%H:%M')}] #{channel}: {text}"
            formatted_messages.append(formatted_line)
        
        return "\n".join(formatted_messages)
    
    def generate_summary(self, messages: List[Dict[str, Any]]) -> str:
        """メッセージから業務概要を生成"""
        if not messages:
            return "今日の業務メッセージはありませんでした。"
        
        print("🤖 AI による業務概要生成中...")
        
        formatted_messages = self.format_messages_for_analysis(messages)
        
        prompt = f"""以下は今日のSlackでの業務メッセージです。これらのメッセージを分析して、業務の概要を日本語で簡潔にまとめてください。

メッセージ内容:
{formatted_messages}

以下の観点で整理してください：
1. 主要な作業内容
2. 今後の予定や課題

箇条書きで分かりやすく整理してください。
最初の挨拶と最後の挨拶は必ず「なのだ」「のだ」「だなのだ」などの口調で回答してください。ずんだもんのような可愛らしい口調で業務概要を作成してください。"""
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response["body"].read())
            summary_text = response_body["content"][0]["text"]
            
            print("✅ 業務概要生成完了")
            return summary_text
        
        except ClientError as e:
            raise Exception(f"Bedrock API エラー: {e}")


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="Slack Daily Report AI - Slackメッセージから日報を自動生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python slack_daily_report.py --output slack    # Slackに投稿
  python slack_daily_report.py --output file     # ファイルに保存
  python slack_daily_report.py                   # 実行時に選択
        """
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["slack", "file"],
        help="出力先を指定: slack (Slackに投稿) または file (ファイルに保存)"
    )
    
    return parser.parse_args()

def get_output_choice():
    """出力先の選択を取得（インタラクティブモード）"""
    print("\n📤 出力先を選択してください：")
    print("1. Slackチャンネルに投稿")
    print("2. ファイルに保存")
    
    while True:
        try:
            choice = input("選択してください (1/2): ").strip()
            if choice == "1":
                return "slack"
            elif choice == "2":
                return "file"
            else:
                print("❌ 1 または 2 を入力してください")
        except KeyboardInterrupt:
            print("\n\n⚠️ 処理を中断しました")
            return None

def main():
    """メイン処理"""
    # コマンドライン引数を解析
    args = parse_arguments()
    
    print("=" * 60)
    print("📊 Slack Daily Report AI 開始")
    print("=" * 60)
    
    # 環境変数の取得
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_user_id = os.getenv("SLACK_USER_ID")
    slack_summary_channel_id = os.getenv("SLACK_SUMMARY_CHANNEL_ID")
    default_output = os.getenv("DEFAULT_OUTPUT", "file")
    
    # 必須環境変数のチェック
    if not slack_token or not slack_user_id:
        print("❌ 必須の環境変数が設定されていません")
        print("   SLACK_BOT_TOKEN と SLACK_USER_ID を設定してください")
        return
    
    try:
        # Slackメッセージを取得
        print("\n🔍 Slackメッセージの取得")
        slack_fetcher = SlackMessageFetcher(slack_token, slack_user_id)
        messages = slack_fetcher.get_daily_messages()
        
        # AI で業務概要を生成
        print("\n🤖 AI による業務概要生成")
        summarizer = BedrockSummarizer()
        summary = summarizer.generate_summary(messages)
        
        # 結果表示
        print("\n" + "=" * 60)
        print("📋 今日の業務概要")
        print("=" * 60)
        print(summary)
        print("=" * 60)
        
        # 出力先の決定
        output_choice = args.output
        if output_choice is None:
            # デフォルトの出力先が設定されている場合は使用
            if default_output in ["slack", "file"]:
                output_choice = default_output
                print(f"💡 デフォルトの出力先を使用: {output_choice}")
            else:
                output_choice = get_output_choice()
                if output_choice is None:  # ユーザーが中断した場合
                    print("処理を終了します")
                    return
        
        # 結果をSlackに投稿またはファイルに保存
        today = datetime.now().strftime("%Y-%m-%d")
        formatted_summary = f"""📊 **日次業務概要** ({today})
メッセージ数: {len(messages)}件
生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{summary}"""
        
        if output_choice == "slack":
            if not slack_summary_channel_id:
                print("❌ SLACK_SUMMARY_CHANNEL_ID が設定されていません")
                print("   投稿先のチャンネルIDを入力してください")
                print("   （例：C1234567890 または #general）")
                print("   ※ チャンネルIDの確認方法はREADMEを参照してください")
                
                try:
                    slack_summary_channel_id = input("チャンネルID: ").strip()
                    
                    if not slack_summary_channel_id:
                        print("❌ チャンネルIDが入力されませんでした")
                        print("   代わりにファイルに保存しますか？ (y/n)")
                        
                        fallback_choice = input().strip().lower()
                        if fallback_choice in ['y', 'yes']:
                            output_choice = "file"
                        else:
                            print("処理を終了します")
                            return
                    else:
                        print(f"💡 チャンネルIDを確認中: {slack_summary_channel_id}")
                        
                        # チャンネルIDの有効性をチェック
                        if not slack_fetcher.validate_channel_id(slack_summary_channel_id):
                            print("❌ チャンネルIDが無効です")
                            print("   代わりにファイルに保存しますか？ (y/n)")
                            
                            fallback_choice = input().strip().lower()
                            if fallback_choice in ['y', 'yes']:
                                output_choice = "file"
                            else:
                                print("処理を終了します")
                                return
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️ 処理を中断しました")
                    return
            
            if output_choice == "slack":
                print("\n📤 Slackへの投稿")
                success = slack_fetcher.post_message(slack_summary_channel_id, formatted_summary)
                
                if not success:
                    print("❌ Slack投稿に失敗しました")
                    print("   代わりにファイルに保存しますか？ (y/n)")
                    
                    try:
                        fallback_choice = input().strip().lower()
                        if fallback_choice in ['y', 'yes']:
                            output_choice = "file"
                        else:
                            print("処理を終了します")
                            return
                    except KeyboardInterrupt:
                        print("\n\n⚠️ 処理を中断しました")
                        return
        
        if output_choice == "file":
            print("\n💾 ファイルに保存中...")
            filename = f"daily_summary_{today}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"日付: {today}\n")
                f.write(f"メッセージ数: {len(messages)}\n")
                f.write(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "=" * 60 + "\n")
                f.write("業務概要\n")
                f.write("=" * 60 + "\n")
                f.write(summary)
            
            print(f"✅ 概要を {filename} に保存しました")
        
        print("\n🎉 処理が正常に完了しました！")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("💡 トラブルシューティング:")
        print("   - Slack/AWS認証情報を確認してください")
        print("   - 必要なスコープが設定されているか確認してください")
        print("   - インターネット接続を確認してください")


if __name__ == "__main__":
    main() 
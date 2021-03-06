# get_all_message_from_slack

本リポジトリは Slack の public チャンネルから全てのメッセージを取得するためのリポジトリです

## 環境詳細

- Python : 3.8
  - 開発時の DatabricksRuntime の最新 LTS が 3.8 であるため

### 事前準備

- Docker インストール
- VSCode インストール
- VSCode の拡張機能「Remote - Containers」インストール
  - https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
- 本リポジトリの clone
- `.env` ファイルを空ファイルでプロジェクト直下に作成

### 環境変数設定

```
SLACK_TOKEN=xoxp-xxxxxxxx
```

### 開発手順

1. VS Code 起動
2. 左下の緑色のアイコンクリック
3. 「Remote-Containersa: Reopen in Container」クリック
4. しばらく待つ
   - 初回の場合コンテナー image の取得や作成が行われる
5. 起動したら開発可能

## SlackAPI で必要な権限

※Bot Token だと各チャンネルに Join する必要があるため User Token を使用します

```
channels:history
groups:history
im:history
mpim:history
channels:read
groups:read
im:read
mpim:read
users:read
```

## 実行

`python -m get_all_message_from_slack.main`

## pip install して実行

- `pip install git+https://github.com/yamap55/get_all_message_from_slack`

```python
import os
os.environ["SLACK_TOKEN"] = "xoxp-xxxxxxxx"
from get_all_message_from_slack.main import main
main()
```

※ `SLACK_TOKEN` をコード内で設定する場合のサンプル

## Slack 設定

- アプリ作成
  - Your Apps 画面 → Create New App → From scratch
  - https://api.slack.com/apps
- 権限設定
  - サイドメニュー → OAuth & Permissions
  - Scopes -> **User Token Scopes**
  - 上記「SlackAPI で必要な権限」を追加
- インストール
  - サイドメニュー → Basic Infomation → Install your app
- Token 取得
  - サイドメニュー → OAuth & Permissions → OAuth Tokens for Your Workspace
  - **User OAuth Token** をコピー
    - `xoxp-` からはじまる Token

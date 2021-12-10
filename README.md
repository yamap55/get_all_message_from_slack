# get_all_message_from_slack

本リポジトリは Slack の public チャンネルから全てのメッセージを取得するためのリポジトリです

## 環境詳細

- Python : 3.9

### 事前準備

- Docker インストール
- VSCode インストール
- VSCode の拡張機能「Remote - Containers」インストール
  - https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
- 本リポジトリの clone
- `.env` ファイルを空ファイルでプロジェクト直下に作成

### 環境変数設定

```
SLACK_TOKEN=xxxxxxxx
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

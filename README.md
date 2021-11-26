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

TODO: 下記は適当なので変更が必要

```
channels:history
channels:read
chat:write
chat:write.public
groups:history
groups:read
im:read
mpim:history
mpim:read
users:read
```

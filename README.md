# 就活 Gmail 整理システム

Gmail 上の就活メールを取得し、ルールベースで分類して Gmail ラベルと SQLite に保存し、Flask で見やすく管理するローカル Web アプリです。

## 技術構成

- Python 3.11 以上
- Flask
- Flask-SQLAlchemy / SQLite
- Gmail API
- Jinja2 + CSS

## セットアップ

1. 仮想環境を作成します。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 依存関係をインストールします。

```powershell
pip install -r requirements.txt
```

3. `.env.example` を元に `.env` を作ります。
4. Google Cloud で Gmail API を有効化し、OAuth クライアント JSON を取得します。
5. `credentials/credentials.json` に配置します。

## Google Cloud 側の準備

1. Google Cloud Console でプロジェクトを作成
2. `Gmail API` を有効化
3. OAuth 同意画面を設定
4. `OAuth クライアント ID` を作成
   - 推奨: `デスクトップ アプリ`
5. ダウンロードした JSON を `credentials/credentials.json` に保存

初回同期時にブラウザ認証が実行され、`credentials/token.json` が自動生成されます。

## 実行手順

DB 初期化:

```powershell
python scripts/init_db.py
```

ラベル作成:

```powershell
python scripts/create_labels.py
```

Gmail 同期:

```powershell
python scripts/sync_gmail.py
```

Flask 起動:

```powershell
python app.py
```

## 主要機能

- Gmail API から就活メールを取得
- HTML メール本文を可能な範囲でテキスト化
- 件名、本文、送信元によるルールベース分類
- Gmail ラベル自動作成 / 自動付与
- 企業名推定
- 企業 / thread 単位での集約
- SQLite 保存
- 重複 message_id 防止

## 後で自分で追加するもの

- `credentials/credentials.json`
  - Google Cloud からダウンロードした OAuth クライアント情報
- `.env`
  - 必要に応じて環境変数を設定
- `credentials/token.json`
  - 初回認証後に自動生成

主に編集対象になる設定:

- `SECRET_KEY`
- `DATABASE_URL`
- `GMAIL_CREDENTIALS_PATH`
- `GMAIL_TOKEN_PATH`
- `JOBMAIL_LABEL_PREFIX`
- `GMAIL_QUERY`
- `MAIL_FETCH_MAX_RESULTS`

## 画面

- `/` ダッシュボード
- `/emails` メール一覧
- `/emails/<id>` メール詳細
- `/companies` 企業一覧
- `/companies/<id>` 企業詳細
- `/sync` Gmail 再同期
"# gmail-" 

# 📠 FAX営業用ドキュメント自動生成ツール

外国人材紹介業向けの FAX 営業ドキュメント自動生成ツールです。
履歴書と手紙を結合し、FAX 送信用の PDF を一括生成します。

## 機能一覧

| ページ | 機能 |
|---|---|
| **FAX文書生成**（トップ） | 履歴書（Excel/PDF）+ 手紙（JPEG/PDF）→ FAX用PDF結合 |
| **履歴書編集** | 既存の Excel 履歴書を読み込んで編集・保存 |
| **テンプレート管理** | 手紙・履歴書テンプレートの追加・削除 |
| **新規履歴書作成** | 入力情報から履歴書 PDF をゼロから作成 |
| **リスト結合** | 複数の Excel リストを1つに結合（列維持） |

## セットアップ

### 必要なもの

- Python 3.9+
- pip

### インストール

```bash
git clone https://github.com/AnyCinc/fax-tool.git
cd fax-tool
pip install -r requirements.txt
```

### 起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が開きます。

## 使い方

### FAX文書生成（メイン機能）

1. **履歴書を選択** — PDF または Excel ファイルをアップロード
   - Excel は自動で PDF に変換されます
2. **手紙を選択** — JPEG/PNG/PDF をアップロード、またはテンプレートから選択
3. **出力設定** — 地域・業種・国籍・年齢を選択（ファイル名に反映）
4. **FAX PDF を生成** — 履歴書 + 手紙を結合した PDF をダウンロード

### リスト結合

1. 複数の Excel ファイルをドラッグ＆ドロップ
2. プレビューで件数を確認
3. 結合して1つの Excel ファイルをダウンロード

## Google Drive 連携（オプション）

生成した PDF を Google Drive に自動保存できます。

### 設定手順

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. Google Drive API を有効化
3. OAuth クライアント ID を作成（デスクトップアプリ）
4. JSON をダウンロードして `credentials/client_secret.json` に配置
5. 初回実行時にブラウザで認証

### フォルダ構造

```
Google Drive 共有フォルダ/
├── 3/9~3/15/          ← 日付範囲フォルダ
│   ├── 1/             ← PC番号
│   ├── 2/
│   ├── ...
│   └── 23/
└── 3/16~3/22/
    └── ...
```

## ファイル構成

```
fax-tool/
├── app.py                      # メインアプリ（FAX文書生成）
├── config.json                 # 地域・業種・国籍・テンプレート設定
├── requirements.txt            # Python依存パッケージ
├── packages.txt                # Streamlit Cloudシステムパッケージ
├── pages/
│   ├── 1_📝_履歴書編集.py       # 履歴書Excel編集
│   ├── 2_📁_テンプレート管理.py  # テンプレート管理
│   ├── 3_🆕_新規履歴書作成.py   # 新規履歴書PDF作成
│   └── 4_📋_リスト結合.py       # 複数Excelリスト結合
├── utils/
│   ├── pdf_generator.py        # PDF変換・結合
│   ├── excel_handler.py        # 履歴書Excelの読み書き
│   ├── resume_builder.py       # 履歴書PDF生成（fpdf2）
│   ├── template_manager.py     # テンプレートCRUD
│   └── gdrive_uploader.py      # Google Drive API連携
├── credentials/                # 認証情報（.gitignore対象）
└── templates/                  # テンプレートファイル格納
```

## 技術スタック

- **UI**: Streamlit
- **Excel処理**: openpyxl
- **PDF生成**: fpdf2, Pillow
- **PDF結合**: pypdf
- **Excel→PDF変換**: qlmanage（macOS） / LibreOffice（Linux）
- **Google連携**: google-api-python-client, google-auth-oauthlib

## デプロイ

Streamlit Community Cloud にデプロイ済みです。
`packages.txt` に Linux 用システムパッケージ（LibreOffice, Noto CJK フォント）を指定しています。

## 開発

株式会社ヒトキワ

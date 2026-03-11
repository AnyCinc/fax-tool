"""Google Drive アップロードモジュール（OAuth2認証）"""
import os
import json
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDS_DIR = Path(__file__).parent.parent / "credentials"
CLIENT_SECRET_PATH = CREDS_DIR / "client_secret.json"
TOKEN_PATH = CREDS_DIR / "token.json"


def is_configured():
    """クライアントシークレットが配置済みか"""
    return CLIENT_SECRET_PATH.exists()


def get_service():
    """認証済みのDriveサービスを取得"""
    creds = None

    # 保存済みトークンがあれば読み込み
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # トークンがない or 期限切れ
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_PATH), SCOPES
            )
            creds = flow.run_local_server(port=8600)

        # トークンを保存
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def get_week_folder_name(start_date, end_date):
    """日付範囲からフォルダ名を生成（例: 3/9~3/15）"""
    return f"{start_date.month}/{start_date.day}~{end_date.month}/{end_date.day}"


def find_or_create_folder(service, name, parent_id):
    """既存フォルダを探すか、なければ作成"""
    query = (
        f"name='{name}' and '{parent_id}' in parents "
        f"and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id,name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_to_drive(file_path, parent_folder_id, start_date, end_date, pc_number):
    """
    ファイルをGoogle Driveにアップロード
    構造: parent_folder / 日付範囲 / PC番号 / ファイル名
    """
    service = get_service()

    # 日付範囲フォルダ
    week_name = get_week_folder_name(start_date, end_date)
    week_folder_id = find_or_create_folder(service, week_name, parent_folder_id)

    # PC番号フォルダ
    pc_folder_id = find_or_create_folder(service, str(pc_number), week_folder_id)

    # ファイルアップロード
    filename = os.path.basename(file_path)
    metadata = {"name": filename, "parents": [pc_folder_id]}
    media = MediaFileUpload(file_path, mimetype="application/pdf")
    uploaded = (
        service.files()
        .create(body=metadata, media_body=media, fields="id,webViewLink")
        .execute()
    )
    return uploaded


def create_week_folders(parent_folder_id, start_date, end_date):
    """日付範囲フォルダと1~23のサブフォルダを一括作成"""
    service = get_service()
    week_name = get_week_folder_name(start_date, end_date)
    week_folder_id = find_or_create_folder(service, week_name, parent_folder_id)

    for i in range(1, 24):
        find_or_create_folder(service, str(i), week_folder_id)

    return week_folder_id

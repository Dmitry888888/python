#!/usr/bin/env python3
"""
Скачивание всех изображений с Google Drive.
Использует: google-auth, google-api-python-client
"""

import os
import sys
import io
from pathlib import Pathpth

from google.auth.exceptions import RefreshError
# Google API
# ✅ CORRECT - imports from installed packages
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Настройки
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = 'credentials_google_table/credentials.json'
TOKEN_FILE = 'token.json'
DOWNLOAD_DIR = Path('T:/downloaded_photos_from_google_drive')
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Логирование
def log(message: str, level: str = "INFO"):
    print(f"[{level}] {message}", file=sys.stderr)


def get_authenticated_service():
    """Получение авторизованного сервиса Google Drive."""
    creds = None

    # 1. Загрузить токен, если он есть
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            log("Токен авторизации загружен.")
        except Exception as e:
            log(f"Ошибка чтения токена: {e}", "ERROR")

    # 2. Проверить валидность токена
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                log("Токен устарел. Обновляем...")
                creds.refresh(Request())
                log("Токен успешно обновлён.")
            except RefreshError:
                log("Не удалось обновить токен. Требуется повторная авторизация.", "WARNING")
                creds = None
            except (ConnectionError, TimeoutError) as e:
                log(f"Ошибка сети при обновлении токена: {e}", "ERROR")
                sys.exit(1)

        # 3. Авторизация через браузер
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                log(f"Файл {CREDENTIALS_FILE} не найден. Скачайте его из Google Cloud Console.", "ERROR")
                sys.exit(1)

            log("Открываем браузер для авторизации...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True, success_message="Авторизация успешна! Можно закрывать браузер.")

            # Сохранить токен для следующих запусков
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            log("Токен сохранён в 'token.json'.")

    return build('drive', 'v3', credentials=creds)


def make_unique_path(directory: Path, name: str) -> Path:
    """Создать уникальное имя файла, если файл уже существует."""
    counter = 1
    stem = Path(name).stem
    suffix = Path(name).suffix
    new_path = directory / name

    while new_path.exists():
        new_name = f"{stem}_{counter}{suffix}"
        new_path = directory / new_name
        counter += 1

    return new_path


def download_all_images():
    """Скачать все изображения с Google Drive."""
    try:
        service = get_authenticated_service()
    except Exception as e:
        log(f"Не удалось подключиться к Google Drive: {e}", "ERROR")
        sys.exit(1)

    try:
        query = "mimeType contains 'image/' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            log("На Google Drive не найдено ни одного изображения.", "WARNING")
            return

        log(f"Найдено {len(files)} изображений. Начинаем загрузку...")

        for i, file in enumerate(files, start=1):
            file_id = file['id']
            file_name = file['name']
            log(f"[{i}/{len(files)}] Обработка: {file_name}")

            request = service.files().get_media(fileId=file_id)
            file_path = make_unique_path(DOWNLOAD_DIR, file_name)

            try:
                fh = io.BytesIO()  # Читаем в память, потом пишем на диск
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        percent = int(status.progress() * 100)
                        sys.stdout.write(f"\r    Прогресс: {percent}%")
                        sys.stdout.flush()

                # Запись на диск
                with open(file_path, 'wb') as f:
                    f.write(fh.getvalue())

                print()  # новая строка после прогресс-бара
                log(f"✓ Успешно скачано: {file_name} → {file_path.relative_to(Path.cwd())}")

            except Exception as e:
                log(f"✗ Ошибка при скачивании '{file_name}': {e}", "ERROR")

    except Exception as e:
        log(f"Ошибка при работе с API: {e}", "ERROR")
        sys.exit(1)



if __name__ == '__main__':
    log("Запуск скрипта скачивания фото с Google Drive")
    download_all_images()
    log("Готово!")
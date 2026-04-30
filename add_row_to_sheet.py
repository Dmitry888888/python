#!/usr/bin/env python3
"""
Добавление строки в Google Таблицу.
Использует: google-auth, google-api-python-client
"""

import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# Настройки
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # Для редактирования таблиц
CREDENTIALS_FILE = 'credentials_google_table/credentials.json'
TOKEN_FILE = 'token.json'
SPREADSHEET_ID = '1B6mZR3tBle-U2_Mk8Ah6fkoztVVOH9rB8FjHgCMVBOc'  # Из URL
RANGE_NAME = 'Лист1!A:A'  # Диапазон первого столбца — чтобы определить номер строки


def log(message: str, level: str = "INFO"):
    print(f"[{level}] {message}", file=sys.stderr)


def get_authenticated_service():
    """Получение авторизованного сервиса Google Sheets."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            log("Токен авторизации загружен.")
        except Exception as e:
            log(f"Ошибка чтения токена: {e}", "ERROR")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                log("Токен устарел. Обновляем...")
                creds.refresh(Request())
                log("Токен успешно обновлён.")
            except Exception as e:
                log(f"Не удалось обновить токен: {e}", "WARNING")
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                log(f"Файл {CREDENTIALS_FILE} не найден.", "ERROR")
                sys.exit(1)

            log("Открываем браузер для авторизации...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            log("Токен сохранён в 'token.json'.")

    return build('sheets', 'v4', credentials=creds)


def get_next_row(service) -> int:
    """Определяет следующую свободную строку в столбце A."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        rows = result.get('values', [])
        return len(rows) + 1  # Первая пустая строка
    except Exception as e:
        log(f"Ошибка при определении строки: {e}", "ERROR")
        return 1  # На всякий случай


def add_name_to_sheet():
    """Добавляет 'Дмитрий' в следующую строку таблицы."""
    try:
        service = get_authenticated_service()
    except Exception as e:
        log(f"Не удалось подключиться к Google Sheets: {e}", "ERROR")
        sys.exit(1)

    try:
        next_row = get_next_row(service)
        log(f"Добавляем 'Дмитрий' в строку {next_row}")

        values = [['Дмитрий']]  # Одна ячейка в строке
        body = {'values': values}

        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Лист1!A{next_row}',
            valueInputOption='RAW',
            body=body
        ).execute()

        log(f"✓ Успешно добавлено: 'Дмитрий' → строка {next_row}")

    except Exception as e:
        log(f"✗ Ошибка при записи в таблицу: {e}", "ERROR")
        sys.exit(1)


if __name__ == '__main__':
    log("Запуск скрипта добавления строки в Google Таблицу")
    add_name_to_sheet()
    log("Готово!")
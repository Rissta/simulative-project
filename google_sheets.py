import logging
from collections import Counter
from datetime import date

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def aggregate_daily(records: list[dict]) -> dict:
    """Считает агрегаты по уже провалидированным записям."""
    total_attempts = len(records)
    successful = sum(1 for r in records if r["is_correct"] is True)
    runs = sum(1 for r in records if r["attempt_type"] == "run")
    submits = sum(1 for r in records if r["attempt_type"] == "submit")
    unique_users = len({r["user_id"] for r in records})

    users_counter = Counter(r["user_id"] for r in records)
    top_user, top_attempts = users_counter.most_common(1)[0] if users_counter else ("—", 0)

    success_rate = (successful / submits * 100) if submits else 0.0

    return {
        "date": date.today().isoformat(),
        "total_attempts": total_attempts,
        "successful_attempts": successful,
        "success_rate_percent": round(success_rate, 2),
        "unique_users": unique_users,
        "runs": runs,
        "submits": submits,
        "top_user": top_user,
        "top_user_attempts": top_attempts,
    }


def upload_aggregates_to_sheet(stats: dict, cfg) -> None:
    """Пишет строку со статистикой в Google-таблицу."""
    if not cfg.GOOGLE_SHEET_ID:
        logger.info("GOOGLE_SHEET_ID не задан — пропускаем выгрузку в Google Sheets")
        return

    logger.info("Начало выгрузки агрегатов в Google Sheets")
    try:
        creds = Credentials.from_service_account_file(
            cfg.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(cfg.GOOGLE_SHEET_ID).worksheet(cfg.GOOGLE_SHEET_NAME)

        if not sheet.row_values(1):
            headers = list(stats.keys())
            sheet.append_row(headers, value_input_option="USER_ENTERED")

        sheet.append_row(list(stats.values()), value_input_option="USER_ENTERED")
        logger.info("Агрегаты успешно выгружены в Google Sheets")
    except Exception as exc:
        logger.exception("Ошибка при выгрузке в Google Sheets: %s", exc)
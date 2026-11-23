import logging
import time

from config import Config
from logger_setup import setup_logging
from api_client import fetch_statistics
from parser import parse_records
from database import load_to_db
from google_sheets import aggregate_daily, upload_aggregates_to_sheet
from email_notifier import send_email

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    started = time.time()
    logger.info("========== Запуск пайплайна ==========")

    raw = fetch_statistics(
        api_url=Config.API_URL,
        client=Config.API_CLIENT,
        client_key=Config.API_CLIENT_KEY,
        start=Config.API_START,
        end=Config.API_END,
    )

    records = parse_records(raw)

    inserted = load_to_db(records, Config)

    stats = aggregate_daily(records)
    logger.info("Агрегаты за день: %s", stats)
    upload_aggregates_to_sheet(stats, Config)

    elapsed = round(time.time() - started, 2)
    body = (
        "Пайплайн успешно завершён.\n\n"
        f"Всего записей из API : {len(raw)}\n"
        f"Валидных записей      : {len(records)}\n"
        f"Вставлено в БД        : {inserted}\n"
        f"Уникальных юзеров     : {stats['unique_users']}\n"
        f"Успешных попыток      : {stats['successful_attempts']} "
        f"({stats['success_rate_percent']}%)\n"
        f"Время выполнения      : {elapsed} сек.\n"
    )
    send_email(subject="Grader ETL: SUCCESS", body=body, cfg=Config)

    logger.info("========== Пайплайн завершён за %.2f сек ==========", elapsed)


def main() -> None:
    setup_logging(Config.LOG_DIR, Config.LOG_RETENTION_DAYS)
    try:
        run_pipeline()
    except Exception as exc:
        logger.exception("Критическая ошибка в пайплайне: %s", exc)
        send_email(
            subject="Grader ETL: FAILED",
            body=f"Пайплайн упал с ошибкой:\n\n{exc}",
            cfg=Config,
        )
        raise


if __name__ == "__main__":
    main()
import ast
import logging
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

VALID_ATTEMPT_TYPES = {"run", "submit"}


def _parse_passback_params(raw) -> dict:
    """Безопасно преобразует строку вида "{'a': 1, 'b': 'x'}" в dict."""
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = ast.literal_eval(raw)
    except (ValueError, SyntaxError) as exc:
        logger.warning("Не удалось распарсить passback_params: %s", exc)
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _is_valid_url(url) -> bool:
    if not isinstance(url, str) or not url:
        return False
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def parse_record(record: dict) -> dict | None:
    """Валидирует и нормализует одну запись. Возвращает dict или None."""
    try:
        user_id = record.get("lti_user_id")
        if not isinstance(user_id, str) or not user_id.strip():
            logger.warning("Пропуск записи: некорректный lti_user_id=%r", user_id)
            return None

        passback = _parse_passback_params(record.get("passback_params"))

        oauth_consumer_key = passback.get("oauth_consumer_key", "")
        if not isinstance(oauth_consumer_key, str):
            logger.warning("Пропуск записи user_id=%s: "
                           "некорректный oauth_consumer_key", user_id)
            return None

        lis_result_sourcedid = passback.get("lis_result_sourcedid")
        if not isinstance(lis_result_sourcedid, str) or not lis_result_sourcedid:
            logger.warning("Пропуск записи user_id=%s: "
                           "отсутствует lis_result_sourcedid", user_id)
            return None

        lis_outcome_service_url = passback.get("lis_outcome_service_url")
        if not _is_valid_url(lis_outcome_service_url):
            logger.warning("Пропуск записи user_id=%s: "
                           "некорректный lis_outcome_service_url", user_id)
            return None

        is_correct = record.get("is_correct")
        if is_correct is None or isinstance(is_correct, bool):
            pass
        elif isinstance(is_correct, int) and is_correct in (0, 1):
            is_correct = bool(is_correct)
        else:
            logger.warning("Пропуск записи user_id=%s: "
                           "некорректный is_correct=%r", user_id, is_correct)
            return None

        attempt_type = record.get("attempt_type")
        if attempt_type not in VALID_ATTEMPT_TYPES:
            logger.warning("Пропуск записи user_id=%s: "
                           "некорректный attempt_type=%r", user_id, attempt_type)
            return None

        created_at_raw = record.get("created_at")
        try:
            created_at = datetime.strptime(created_at_raw, "%Y-%m-%d %H:%M:%S.%f")
        except (TypeError, ValueError):
            logger.warning("Пропуск записи user_id=%s: "
                           "некорректный created_at=%r", user_id, created_at_raw)
            return None

        return {
            "user_id": user_id,
            "oauth_consumer_key": oauth_consumer_key,
            "lis_result_sourcedid": lis_result_sourcedid,
            "lis_outcome_service_url": lis_outcome_service_url,
            "is_correct": is_correct,
            "attempt_type": attempt_type,
            "created_at": created_at,
        }

    except Exception as exc:
        logger.exception("Неожиданная ошибка при разборе записи: %s", exc)
        return None


def parse_records(records: list[dict]) -> list[dict]:
    logger.info("Начало обработки данных. Всего записей: %d", len(records))
    processed, skipped = [], 0
    for rec in records:
        parsed = parse_record(rec)
        if parsed is None:
            skipped += 1
        else:
            processed.append(parsed)
    logger.info("Обработка завершена. Валидных: %d, пропущено: %d",
                len(processed), skipped)
    return processed
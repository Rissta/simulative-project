import logging
import requests

logger = logging.getLogger(__name__)

def fetch_statistics(api_url: str, client: str, client_key: str, start: str, end: str) -> list[dict]:
    params = {
        "client": client,
        "client_key": client_key,
        "start": start,
        "end": end,
    }

    logger.info("Начало скачивания данных из API: %s (start=%s, end=%s)", api_url, start, end)

    try:
        response = requests.get(api_url, params=params, timeout=120)
    except requests.RequestException as exc:
        logger.error("Ошибка сети при обращении к API: %s", exc)
        raise

    if response.status_code != 200:
        logger.error("API вернул статус-код %s. Тело ответа: %s", response.status_code, response.text)
        response.raise_for_status()

    try:
        data = response.json()
    except ValueError as exc:
        logger.error("Не удалось распарсить JSON-ответ API. Текст ответа: %s", response.text)
        raise

    if not isinstance(data, list):
        logger.error("Неожиданный формат ответа API: ожидался список (list), получен %s. Полное содержимое: %s", type(data).__name__, data)
        raise ValueError(f"API вернул не список. Ответ сервера: {data}")

    logger.info("Скачивание завершено. Получено записей: %d", len(data))
    return data
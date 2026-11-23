import logging
import psycopg

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_activity (
    id                      SERIAL PRIMARY KEY,
    user_id                 VARCHAR(255) NOT NULL,
    oauth_consumer_key      VARCHAR(255),
    lis_result_sourcedid    TEXT NOT NULL,
    lis_outcome_service_url TEXT NOT NULL,
    is_correct              BOOLEAN,
    attempt_type            VARCHAR(20) NOT NULL,
    created_at              TIMESTAMP NOT NULL,
    loaded_at               TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_attempt UNIQUE (user_id, lis_result_sourcedid, created_at, attempt_type)
)
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON user_activity (created_at)",
]

INSERT_SQL = """
INSERT INTO user_activity
    (user_id, oauth_consumer_key, lis_result_sourcedid,
     lis_outcome_service_url, is_correct, attempt_type, created_at)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (user_id, lis_result_sourcedid, created_at, attempt_type) DO NOTHING
"""


def load_to_db(records: list[dict], cfg) -> int:
    """Загружает записи в PostgreSQL. Возвращает число реально вставленных строк."""
    if not records:
        logger.info("Нет данных для загрузки в БД — пропускаем шаг")
        return 0

    logger.info("Начало загрузки в БД PostgreSQL. Записей: %d", len(records))

    try:
        with psycopg.connect(
            host=cfg.DB_HOST,
            port=cfg.DB_PORT,
            dbname=cfg.DB_NAME,
            user=cfg.DB_USER,
            password=cfg.DB_PASSWORD,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
                for idx_sql in CREATE_INDEXES_SQL:
                    cur.execute(idx_sql)

                values = [
                    (
                        r["user_id"],
                        r["oauth_consumer_key"],
                        r["lis_result_sourcedid"],
                        r["lis_outcome_service_url"],
                        r["is_correct"],
                        r["attempt_type"],
                        r["created_at"],
                    )
                    for r in records
                ]

                cur.executemany(INSERT_SQL, values)
                inserted = cur.rowcount if cur.rowcount >= 0 else len(records)

        logger.info("Загрузка в БД завершена. Реально вставлено строк: %d", inserted)
        return inserted

    except Exception as exc:
        logger.exception("Ошибка при работе с БД: %s", exc)
        raise
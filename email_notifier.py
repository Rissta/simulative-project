import logging
import smtplib
import ssl
from email.message import EmailMessage

import certifi

logger = logging.getLogger(__name__)


def send_email(subject: str, body: str, cfg) -> None:
    if not (cfg.SENDER_EMAIL and cfg.SENDER_PASSWORD and cfg.RECIPIENT_EMAIL):
        logger.info("Данные для e-mail не заданы — пропускаем отправку")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = cfg.SENDER_EMAIL
    msg["To"] = cfg.RECIPIENT_EMAIL

    context = ssl.create_default_context(cafile=certifi.where())

    logger.info("Отправка e-mail на %s", cfg.RECIPIENT_EMAIL)
    try:
        with smtplib.SMTP_SSL(cfg.SMTP_SERVER, cfg.SMTP_PORT,
                              context=context, timeout=30) as server:
            server.login(cfg.SENDER_EMAIL, cfg.SENDER_PASSWORD)
            server.send_message(msg)
        logger.info("E-mail успешно отправлен")
    except Exception as exc:
        logger.exception("Ошибка при отправке e-mail: %s", exc)
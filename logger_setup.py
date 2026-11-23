import logging
import os
from datetime import datetime, timedelta


def cleanup_old_logs(log_dir: str, retention_days: int) -> None:
    """Удаляет лог-файлы старше retention_days дней."""
    if not os.path.isdir(log_dir):
        return
    cutoff = datetime.now() - timedelta(days=retention_days)
    for filename in os.listdir(log_dir):
        if not filename.endswith(".log"):
            continue
        date_str = filename[:-4]
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        if file_date < cutoff:
            try:
                os.remove(os.path.join(log_dir, filename))
            except OSError:
                pass


def setup_logging(log_dir: str, retention_days: int) -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    cleanup_old_logs(log_dir, retention_days)

    log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
    log_path = os.path.join(log_dir, log_filename)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger
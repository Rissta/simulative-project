import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_URL = os.getenv("API_URL", "https://api.itresume.ru/statistics/")
    API_CLIENT = os.getenv("API_CLIENT", "Skillfactory")
    API_CLIENT_KEY = os.getenv("API_CLIENT_KEY", "M2MGWS")
    API_START = os.getenv("API_START", "2023-04-01 12:46:47.860798")
    API_END = os.getenv("API_END", "2026-06-01 00:00:00.000000")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "grader_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    LOG_DIR = os.getenv("LOG_DIR", "logs")
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "3"))

    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Статистика грейдера")

    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.mail.ru")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")
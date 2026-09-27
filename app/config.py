from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "vending.db"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

APP_NAME = "ตู้เครื่องเขียนอัตโนมัติ"
CURRENCY = "บาท"
HOST = "0.0.0.0"
PORT = 8000

from pathlib import Path
import os

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

# Lädt die Variablen aus .env
load_dotenv()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = BASE_DIR / "Documents"
GENERATED_DIR = BASE_DIR / "generated"
LOG_DIR = BASE_DIR / "logs"

for directory in (
    DATA_DIR,
    DOCUMENTS_DIR,
    GENERATED_DIR,
    LOG_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# APPLICATION
# ============================================================

ZIP_PREFIX = "Bewerbung"

# ZIP standardmäßig alleine verschicken.
SEND_ZIP_ONLY = True

# Maximale Größe des E-Mail-Anhangs in MB.
MAX_ATTACHMENT_SIZE_MB = 20


# ============================================================
# SMTP
# ============================================================

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "",
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587",
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    "",
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    "",
)

SMTP_USE_TLS = os.getenv(
    "SMTP_USE_TLS",
    "true",
).lower() == "true"

MAIL_FROM = os.getenv(
    "MAIL_FROM",
    SMTP_USERNAME,
)


# ============================================================
# LOGGING
# ============================================================

LOG_FILE = LOG_DIR / "applications.log"
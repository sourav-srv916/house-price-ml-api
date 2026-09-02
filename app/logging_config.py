import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import settings


# ---------------------------------------------------------
# LOG DIRECTORY
# ---------------------------------------------------------

# Create a "logs" folder in the project directory
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


# ---------------------------------------------------------
# LOG FORMAT
# ---------------------------------------------------------

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "request_id=%(request_id)s | %(message)s"
)


# ---------------------------------------------------------
# REQUEST ID FILTER
# ---------------------------------------------------------

class RequestIdFilter(logging.Filter):

    def filter(self, record):

        # If a log message does not have a request_id,
        # use "-"
        if not hasattr(record, "request_id"):
            record.request_id = "-"

        return True


# ---------------------------------------------------------
# CREATE LOGGER
# ---------------------------------------------------------

logger = logging.getLogger("house_price_api")

logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))


# Prevent duplicate log messages
logger.propagate = False


# ---------------------------------------------------------
# FORMATTER
# ---------------------------------------------------------

formatter = logging.Formatter(LOG_FORMAT)


# ---------------------------------------------------------
# CONSOLE HANDLER
# ---------------------------------------------------------

console_handler = logging.StreamHandler()

console_handler.setFormatter(formatter)

console_handler.addFilter(RequestIdFilter())


# ---------------------------------------------------------
# ROTATING FILE HANDLER
# ---------------------------------------------------------

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

file_handler.addFilter(RequestIdFilter())


# ---------------------------------------------------------
# ADD HANDLERS TO LOGGER
# ---------------------------------------------------------

logger.addHandler(console_handler)
logger.addHandler(file_handler)
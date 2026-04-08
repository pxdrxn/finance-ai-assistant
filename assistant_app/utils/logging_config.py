import logging

from assistant_app.config import DEFAULT_LOG_FILE, LOGS_DIR


def configure_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(DEFAULT_LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

import asyncio
import os

from .app import OwnMoveDetector
from .config import Settings
from .storage import Storage


def _load_settings() -> Settings:
    return Settings(
        websocket_url=os.getenv("WEBSOCKET_URL", Settings().websocket_url),
        reg_window_seconds=int(os.getenv("REG_WINDOW_SECONDS", "86400")),
        alert_window_seconds=int(os.getenv("ALERT_WINDOW_SECONDS", "3600")),
        alert_threshold=float(os.getenv("ALERT_THRESHOLD", "0.01")),
        heartbeat_seconds=int(os.getenv("HEARTBEAT_SECONDS", "60")),
        enable_db=os.getenv("ENABLE_DB", "0") == "1",
        database_url=os.getenv("DATABASE_URL", ""),
    )


def main() -> None:
    settings = _load_settings()
    storage = None
    if settings.enable_db:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required when ENABLE_DB=1")
        storage = Storage.from_url(settings.database_url)
    detector = OwnMoveDetector(settings=settings, storage=storage)
    asyncio.run(detector.run())


if __name__ == "__main__":
    main()


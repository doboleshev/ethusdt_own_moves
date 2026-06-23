import asyncio
import os

from .app import OwnMoveDetector
from .config import Settings
from .storage import Storage


def _load_settings() -> Settings:
    defaults = Settings()
    data_source = os.getenv("DATA_SOURCE", defaults.data_source)
    if data_source not in ("auto", "websocket", "rest"):
        raise RuntimeError("DATA_SOURCE must be auto, websocket, or rest")
    return Settings(
        websocket_url=os.getenv("WEBSOCKET_URL", defaults.websocket_url),
        rest_url=os.getenv("REST_URL", defaults.rest_url),
        data_source=data_source,
        ws_fallback_seconds=float(os.getenv("WS_FALLBACK_SECONDS", "30")),
        rest_poll_seconds=float(os.getenv("REST_POLL_SECONDS", "1")),
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
    print(
        "[START] ETH own-moves detector",
        f"source={settings.data_source}",
        f"reg={settings.reg_window_seconds}s",
        f"alert={settings.alert_window_seconds // 60}m",
        f"threshold={settings.alert_threshold:.1%}",
        flush=True,
    )
    detector = OwnMoveDetector(settings=settings, storage=storage)
    asyncio.run(detector.run())


if __name__ == "__main__":
    main()


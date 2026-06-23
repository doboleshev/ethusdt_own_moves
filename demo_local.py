"""Local demo: simulated mark prices when Binance WebSocket is unavailable."""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

from eth_own_moves.app import OwnMoveDetector
from eth_own_moves.config import Settings
from eth_own_moves.stream import MarkPriceEvent


def main() -> None:
    settings = Settings(
        reg_window_seconds=300,
        alert_window_seconds=60,
        alert_threshold=0.005,
        heartbeat_seconds=10,
        enable_db=False,
    )
    detector = OwnMoveDetector(settings=settings, storage=None)

    start = datetime.now(tz=timezone.utc).replace(microsecond=0)
    eth = 2500.0
    btc = 65000.0
    rng = random.Random(42)

    print("Demo mode: simulated ETH/BTC mark prices (1 tick/sec)", flush=True)
    print(
        f"Windows: reg={settings.reg_window_seconds}s, "
        f"alert={settings.alert_window_seconds}s, "
        f"threshold={settings.alert_threshold:.1%}",
        flush=True,
    )
    print("-" * 60, flush=True)

    for i in range(420):
        ts = start + timedelta(seconds=i)
        btc *= 1.0 + rng.gauss(0, 0.00015)
        eth *= 1.0 + rng.gauss(0, 0.00015)

        # Inject a strong ETH-only move in the last minute.
        if i >= 360:
            eth *= 1.0 + 0.00035

        for symbol, price in (("btcusdt", btc), ("ethusdt", eth)):
            message = detector._handle_event(
                MarkPriceEvent(symbol=symbol, price=price, ts=ts)
            )
            if message:
                print(message, flush=True)

    print("-" * 60, flush=True)
    print("Demo finished.", flush=True)


if __name__ == "__main__":
    main()

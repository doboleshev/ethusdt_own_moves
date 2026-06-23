from datetime import datetime, timedelta, timezone

from eth_own_moves.app import OwnMoveDetector
from eth_own_moves.config import Settings
from eth_own_moves.stream import MarkPriceEvent


def test_detector_alert_on_own_move():
    settings = Settings(
        reg_window_seconds=300,
        alert_window_seconds=60,
        alert_threshold=0.009,
        enable_db=False,
    )
    detector = OwnMoveDetector(settings=settings, storage=None)

    ts = datetime(2026, 2, 6, tzinfo=timezone.utc)
    detector._handle_event(MarkPriceEvent(symbol="btcusdt", price=100.0, ts=ts))
    detector._handle_event(MarkPriceEvent(symbol="ethusdt", price=100.0, ts=ts))

    message = None
    eth_price = 100.0
    btc_price = 100.0
    for i in range(1, 65):
        tick_ts = ts + timedelta(seconds=i)
        btc_price *= 1.0001
        eth_price *= 1.002
        detector._handle_event(
            MarkPriceEvent(symbol="btcusdt", price=btc_price, ts=tick_ts)
        )
        message = detector._handle_event(
            MarkPriceEvent(symbol="ethusdt", price=eth_price, ts=tick_ts)
        )

    assert message is not None


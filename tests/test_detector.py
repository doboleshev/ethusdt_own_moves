from datetime import datetime, timezone

from eth_own_moves.app import OwnMoveDetector
from eth_own_moves.config import Settings
from eth_own_moves.stream import MarkPriceEvent


def test_detector_alert_on_own_move():
    settings = Settings(
        reg_window_seconds=2,
        alert_window_seconds=1,
        alert_threshold=0.009,
        enable_db=False,
    )
    detector = OwnMoveDetector(settings=settings, storage=None)

    ts = datetime(2026, 2, 6, tzinfo=timezone.utc)
    detector._handle_event(MarkPriceEvent(symbol="btcusdt", price=100.0, ts=ts))
    detector._handle_event(MarkPriceEvent(symbol="ethusdt", price=100.0, ts=ts))
    detector._handle_event(
        MarkPriceEvent(symbol="btcusdt", price=100.0, ts=ts.replace(second=1))
    )
    message = detector._handle_event(
        MarkPriceEvent(symbol="ethusdt", price=101.0, ts=ts.replace(second=1))
    )
    assert message is not None


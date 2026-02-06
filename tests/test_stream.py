from datetime import timezone

from eth_own_moves.stream import _parse_event


def test_parse_event():
    payload = {
        "data": {
            "e": "markPriceUpdate",
            "s": "ETHUSDT",
            "p": "2500.5",
            "E": 1700000000000,
        }
    }
    event = _parse_event(payload)
    assert event is not None
    assert event.symbol == "ethusdt"
    assert event.price == 2500.5
    assert event.ts.tzinfo == timezone.utc


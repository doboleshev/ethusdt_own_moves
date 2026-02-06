from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import AsyncIterator

import websockets


@dataclass(frozen=True)
class MarkPriceEvent:
    symbol: str
    price: float
    ts: datetime


def _parse_event(payload: dict) -> MarkPriceEvent | None:
    data = payload.get("data")
    if not data or data.get("e") != "markPriceUpdate":
        return None
    symbol = data.get("s")
    price = data.get("p")
    event_time = data.get("E")
    if symbol is None or price is None or event_time is None:
        return None
    return MarkPriceEvent(
        symbol=symbol.lower(),
        price=float(price),
        ts=datetime.fromtimestamp(event_time / 1000, tz=timezone.utc),
    )


async def stream_mark_prices(url: str) -> AsyncIterator[MarkPriceEvent]:
    async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
        async for message in ws:
            payload = json.loads(message)
            event = _parse_event(payload)
            if event is not None:
                yield event


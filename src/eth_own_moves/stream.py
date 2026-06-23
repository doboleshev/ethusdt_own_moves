from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import AsyncIterator, Literal

import websockets

DataSource = Literal["auto", "websocket", "rest"]


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


def _parse_rest_premium_index(payload: dict) -> MarkPriceEvent:
    return MarkPriceEvent(
        symbol=str(payload["symbol"]).lower(),
        price=float(payload["markPrice"]),
        ts=datetime.fromtimestamp(payload["time"] / 1000, tz=timezone.utc),
    )


def _fetch_mark_price(rest_url: str, symbol: str) -> MarkPriceEvent:
    url = f"{rest_url}?symbol={symbol.upper()}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        payload = json.loads(resp.read())
    return _parse_rest_premium_index(payload)


async def stream_mark_prices(url: str) -> AsyncIterator[MarkPriceEvent]:
    print("[WS] connecting to Binance Futures...", flush=True)
    async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
        print("[WS] connected, waiting for mark price ticks...", flush=True)
        first_tick = True
        async for message in ws:
            payload = json.loads(message)
            event = _parse_event(payload)
            if event is not None:
                if first_tick:
                    print(
                        f"[WS] first tick: {event.symbol.upper()} @ {event.price}",
                        flush=True,
                    )
                    first_tick = False
                yield event


async def stream_mark_prices_rest(
    rest_url: str,
    interval: float = 1.0,
    symbols: tuple[str, ...] = ("ETHUSDT", "BTCUSDT"),
) -> AsyncIterator[MarkPriceEvent]:
    print(f"[REST] polling mark prices every {interval:.0f}s...", flush=True)
    first_tick = True
    while True:
        for symbol in symbols:
            try:
                event = await asyncio.to_thread(_fetch_mark_price, rest_url, symbol)
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                print(f"[REST] fetch failed for {symbol}: {exc}", flush=True)
                continue
            if first_tick:
                print(
                    f"[REST] first tick: {event.symbol.upper()} @ {event.price}",
                    flush=True,
                )
                first_tick = False
            yield event
        await asyncio.sleep(interval)


async def stream_mark_prices_auto(
    websocket_url: str,
    rest_url: str,
    *,
    ws_timeout: float = 30.0,
    rest_interval: float = 1.0,
) -> AsyncIterator[MarkPriceEvent]:
    try:
        async with asyncio.timeout(ws_timeout):
            async for event in stream_mark_prices(websocket_url):
                yield event
        return
    except TimeoutError:
        print(
            "[REST] WebSocket silent — switching to REST polling...",
            flush=True,
        )
    async for event in stream_mark_prices_rest(rest_url, rest_interval):
        yield event


async def iter_mark_prices(
    *,
    data_source: DataSource,
    websocket_url: str,
    rest_url: str,
    ws_fallback_seconds: float = 30.0,
    rest_poll_seconds: float = 1.0,
) -> AsyncIterator[MarkPriceEvent]:
    if data_source == "rest":
        async for event in stream_mark_prices_rest(rest_url, rest_poll_seconds):
            yield event
    elif data_source == "websocket":
        async for event in stream_mark_prices(websocket_url):
            yield event
    else:
        async for event in stream_mark_prices_auto(
            websocket_url,
            rest_url,
            ws_timeout=ws_fallback_seconds,
            rest_interval=rest_poll_seconds,
        ):
            yield event

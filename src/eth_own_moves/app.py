from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta

from .analysis import RollingRegression, RollingSum, cumulative_return, log_return
from .config import Settings
from .storage import Storage
from .stream import MarkPriceEvent, iter_mark_prices


@dataclass
class State:
    last_eth_price: float | None = None
    last_btc_price: float | None = None
    prev_eth_price: float | None = None
    prev_btc_price: float | None = None
    last_eth_return: float | None = None
    last_btc_return: float | None = None
    eth_updated: bool = False
    btc_updated: bool = False
    last_calc_ts: datetime | None = None
    last_heartbeat_ts: datetime | None = None


class OwnMoveDetector:
    def __init__(self, settings: Settings, storage: Storage | None = None) -> None:
        self.settings = settings
        self.storage = storage
        self.state = State()
        self.regression = RollingRegression(settings.reg_window_seconds)
        self.alert_window = RollingSum(settings.alert_window_seconds)

    def _handle_event(self, event: MarkPriceEvent) -> str | None:
        if event.symbol == "ethusdt":
            if self.state.last_eth_price is None:
                self.state.last_eth_price = event.price
                return None
            self.state.prev_eth_price = self.state.last_eth_price
            self.state.last_eth_price = event.price
            self.state.last_eth_return = log_return(
                self.state.prev_eth_price, self.state.last_eth_price
            )
            self.state.eth_updated = True
        elif event.symbol == "btcusdt":
            if self.state.last_btc_price is None:
                self.state.last_btc_price = event.price
                return None
            self.state.prev_btc_price = self.state.last_btc_price
            self.state.last_btc_price = event.price
            self.state.last_btc_return = log_return(
                self.state.prev_btc_price, self.state.last_btc_price
            )
            self.state.btc_updated = True
        else:
            return None

        if event.symbol == "ethusdt":
            symbol = "ethusdt"
        else:
            symbol = "btcusdt"

        if self.storage is not None:
            self.storage.write_price(symbol, event.ts, event.price)

        if not (self.state.eth_updated and self.state.btc_updated):
            return None

        if self.state.last_calc_ts is not None and event.ts <= self.state.last_calc_ts:
            return None

        if self.state.last_eth_return is None or self.state.last_btc_return is None:
            return None

        eth_ret = self.state.last_eth_return
        btc_ret = self.state.last_btc_return

        stats = self.regression.add(btc_ret, eth_ret)
        residual = eth_ret - stats.beta * btc_ret
        total = self.alert_window.add(residual)
        self.state.last_calc_ts = event.ts
        self.state.eth_updated = False
        self.state.btc_updated = False

        if self.storage is not None:
            self.storage.write_residual(event.ts, residual, stats.beta)

        if self.alert_window.count >= self.settings.alert_window_seconds:
            move = cumulative_return(total)
            if abs(move) >= self.settings.alert_threshold:
                return (
                    f"[ALERT] own ETH move {move:.2%} over last "
                    f"{self.settings.alert_window_seconds // 60} minutes "
                    f"(beta={stats.beta:.3f})"
                )
        if self._heartbeat_due(event.ts):
            move = cumulative_return(total)
            print(
                f"[HEARTBEAT] beta={stats.beta:.3f} "
                f"own_move_60m={move:.2%} "
                f"samples={self.alert_window.count}",
                flush=True,
            )
        return None

    def _heartbeat_due(self, ts: datetime) -> bool:
        if self.state.last_heartbeat_ts is None:
            self.state.last_heartbeat_ts = ts
            return True
        if ts - self.state.last_heartbeat_ts >= timedelta(
            seconds=self.settings.heartbeat_seconds
        ):
            self.state.last_heartbeat_ts = ts
            return True
        return False

    async def run(self) -> None:
        async for event in iter_mark_prices(
            data_source=self.settings.data_source,
            websocket_url=self.settings.websocket_url,
            rest_url=self.settings.rest_url,
            ws_fallback_seconds=self.settings.ws_fallback_seconds,
            rest_poll_seconds=self.settings.rest_poll_seconds,
        ):
            message = self._handle_event(event)
            if message:
                print(message, flush=True)
            await asyncio.sleep(0)


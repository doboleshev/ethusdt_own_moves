from typing import Literal

from pydantic import BaseModel, Field

DataSource = Literal["auto", "websocket", "rest"]


class Settings(BaseModel):
    websocket_url: str = Field(
        default="wss://fstream.binance.com/stream?streams=ethusdt@markPrice@1s/btcusdt@markPrice@1s"
    )
    rest_url: str = Field(default="https://fapi.binance.com/fapi/v1/premiumIndex")
    data_source: DataSource = Field(default="auto")
    ws_fallback_seconds: float = Field(default=30.0, ge=5)
    rest_poll_seconds: float = Field(default=1.0, ge=0.2)
    reg_window_seconds: int = Field(default=86400, ge=300)
    alert_window_seconds: int = Field(default=3600, ge=60)
    alert_threshold: float = Field(default=0.01, gt=0)
    heartbeat_seconds: int = Field(default=60, ge=10)
    enable_db: bool = Field(default=False)
    database_url: str = Field(default="")


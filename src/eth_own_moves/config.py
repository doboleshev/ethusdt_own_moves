from pydantic import BaseModel, Field


class Settings(BaseModel):
    websocket_url: str = Field(
        default="wss://fstream.binance.com/stream?streams=ethusdt@markPrice@1s/btcusdt@markPrice@1s"
    )
    reg_window_seconds: int = Field(default=86400, ge=300)
    alert_window_seconds: int = Field(default=3600, ge=60)
    alert_threshold: float = Field(default=0.01, gt=0)
    heartbeat_seconds: int = Field(default=60, ge=10)
    enable_db: bool = Field(default=False)
    database_url: str = Field(default="")


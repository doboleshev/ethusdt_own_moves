from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, PricePoint, ResidualPoint


@dataclass
class Storage:
    session_factory: sessionmaker

    @classmethod
    def from_url(cls, url: str) -> "Storage":
        engine = create_engine(url, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        return cls(session_factory=sessionmaker(bind=engine))

    def write_price(self, symbol: str, ts: datetime, price: float) -> None:
        with self.session_factory() as session:
            session.add(PricePoint(symbol=symbol, ts=ts, price=price))
            session.commit()

    def write_residual(self, ts: datetime, residual_return: float, beta: float) -> None:
        with self.session_factory() as session:
            session.add(
                ResidualPoint(ts=ts, residual_return=residual_return, beta=beta)
            )
            session.commit()


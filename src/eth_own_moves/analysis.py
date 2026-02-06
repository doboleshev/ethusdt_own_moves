from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass


@dataclass
class RegressionStats:
    beta: float
    count: int


class RollingRegression:
    def __init__(self, maxlen: int) -> None:
        if maxlen < 2:
            raise ValueError("maxlen must be >= 2")
        self.maxlen = maxlen
        self._x = deque(maxlen=maxlen)
        self._y = deque(maxlen=maxlen)
        self._sum_x = 0.0
        self._sum_y = 0.0
        self._sum_x2 = 0.0
        self._sum_xy = 0.0

    def add(self, x: float, y: float) -> RegressionStats:
        if len(self._x) == self.maxlen:
            old_x = self._x.popleft()
            old_y = self._y.popleft()
            self._sum_x -= old_x
            self._sum_y -= old_y
            self._sum_x2 -= old_x * old_x
            self._sum_xy -= old_x * old_y
        self._x.append(x)
        self._y.append(y)
        self._sum_x += x
        self._sum_y += y
        self._sum_x2 += x * x
        self._sum_xy += x * y
        return self.stats()

    def stats(self) -> RegressionStats:
        n = len(self._x)
        if n < 2:
            return RegressionStats(beta=0.0, count=n)
        mean_x = self._sum_x / n
        mean_y = self._sum_y / n
        cov = self._sum_xy - n * mean_x * mean_y
        var = self._sum_x2 - n * mean_x * mean_x
        if abs(var) < 1e-12:
            return RegressionStats(beta=0.0, count=n)
        return RegressionStats(beta=cov / var, count=n)


class RollingSum:
    def __init__(self, maxlen: int) -> None:
        if maxlen < 1:
            raise ValueError("maxlen must be >= 1")
        self.maxlen = maxlen
        self._values = deque(maxlen=maxlen)
        self._total = 0.0

    def add(self, value: float) -> float:
        if len(self._values) == self.maxlen:
            old = self._values.popleft()
            self._total -= old
        self._values.append(value)
        self._total += value
        return self._total

    @property
    def total(self) -> float:
        return self._total

    @property
    def count(self) -> int:
        return len(self._values)


def log_return(prev_price: float, price: float) -> float:
    if prev_price <= 0 or price <= 0:
        raise ValueError("price must be positive")
    return math.log(price / prev_price)


def cumulative_return(log_return_sum: float) -> float:
    return math.exp(log_return_sum) - 1.0


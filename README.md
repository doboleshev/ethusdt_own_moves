# ETHUSDT own moves detector

## Методика анализа (часть 1)

Цель — выделить собственные движения цены ETHUSDT, исключив влияние BTCUSDT.

Выбранная методика: **регрессия доходностей (hedge ratio)**.

- Используем лог-доходности:  
  `r_eth = ln(P_eth / P_eth_prev)`, `r_btc = ln(P_btc / P_btc_prev)`
- Оцениваем чувствительность ETH к BTC через коэффициент `beta`:
  `beta = cov(r_btc, r_eth) / var(r_btc)`
- Собственное движение ETH определяется как остаток:
  `r_own = r_eth - beta * r_btc`

Такой подход отделяет общерыночное движение (BTC) от idiosyncratic компоненты ETH.

### Подбор параметров

- **Окно регрессии:** `86400` наблюдений (≈ 24 часа при частоте 1 секунда).  
  Достаточно длинное окно снижает шум и позволяет стабильно оценивать `beta`.
- **Окно для алерта:** `3600` наблюдений (60 минут).  
  Требование задачи — изменение за последние 60 минут.
- **Порог алерта:** `1%` по собственному движению (`abs(cum_return) >= 0.01`).
- **Источник данных:** Binance Futures **mark price** с частотой 1 секунда  
  (`@markPrice@1s`) — минимальная задержка и устойчивость к спайкам.

### Обоснование

Регрессия на BTC лог-доходности — стандартный способ выделения нейтрального к рынку
движения. Использование скользящих сумм позволяет обновлять `beta` за `O(1)` на тик,
что оптимально для realtime задач.

## Структура проекта

- `src/eth_own_moves/analysis.py` — регрессия, окна, математика
- `src/eth_own_moves/stream.py` — WebSocket и REST потоки Binance
- `src/eth_own_moves/app.py` — логика realtime детектора
- `src/eth_own_moves/storage.py` — хранение в PostgreSQL (опционально)
- `tests/` — тесты основных компонентов

## Установка и запуск

### Локально (Python 3.11+)

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m eth_own_moves
```

По умолчанию используется режим `auto`: WebSocket, с автоматическим переходом на REST,
если тики не приходят 30 секунд. Для немедленного REST-режима:

```bash
set DATA_SOURCE=rest
python -m eth_own_moves
```

Локальная демонстрация без Binance:

```bash
python demo_local.py
```

### Docker + PostgreSQL

```bash
docker compose up --build
```

## Переменные окружения

- `WEBSOCKET_URL` — URL Binance WebSocket
- `DATA_SOURCE` — `auto` (по умолчанию), `websocket` или `rest`
- `REST_URL` — REST endpoint mark price (по умолчанию `https://fapi.binance.com/fapi/v1/premiumIndex`)
- `WS_FALLBACK_SECONDS` — таймаут перед переходом на REST (по умолчанию 30)
- `REST_POLL_SECONDS` — интервал REST-опроса в секундах (по умолчанию 1)
- `REG_WINDOW_SECONDS` — окно регрессии (по умолчанию 86400)
- `ALERT_WINDOW_SECONDS` — окно алерта (по умолчанию 3600)
- `ALERT_THRESHOLD` — порог алерта (по умолчанию 0.01)
- `HEARTBEAT_SECONDS` — период heartbeat-лога (по умолчанию 60)
- `ENABLE_DB` — `1` для включения PostgreSQL
- `DATABASE_URL` — строка подключения для SQLAlchemy

## Тесты

```bash
pytest
```


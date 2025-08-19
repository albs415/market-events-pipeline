# Market Events ETL (GDELT + Polygon + SEC) → Labeled Parquet

This is a **self-running pipeline** that ingests market-moving events and joins them to minute bars to produce **ML-ready labels** (gap, 30m/1h/1d returns, abnormal returns vs sector/SPY, volume z-score, etc.).

Deploy with Docker or run locally with Python 3.11+.

## Quick start (Docker)
```bash
cp .env.example .env
# edit .env with your keys

docker compose up --build
```

## Quick start (Local Python)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m etl.main
```

## Configuration (.env)
- `POLYGON_API_KEY=` your Polygon key
- `UNIVERSE=NVDA,TSLA,MSFT,AMD,UNH,AAPL,TSM,SPY,QQQ,SMH`
- `DATA_DIR=./data`
- `TIMEZONE=America/New_York`
- `ENABLE_DUCKDB=true` (optional)

Outputs go to `data/parquet/` and optional DuckDB at `data/db/labels.duckdb`.

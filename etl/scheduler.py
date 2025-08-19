import asyncio, pandas as pd, os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .sources.gdelt import run_gdelt_ingest
from .sources.polygon_news import run_polygon_news_ingest
from .sources.sec_daily import run_sec_daily_index
from .config import DATA_DIR
from .storage import write_parquet
from .price.polygon_prices import fetch_window_prices
from .labeling import compute_basic_labels

EVENTS_PATH = os.path.join(DATA_DIR, "parquet", "events_master.parquet")

async def job_gdelt():
    path = await run_gdelt_ingest()
    print("GDELT ingest →", path)

async def job_polygon_news():
    path = await run_polygon_news_ingest()
    print("Polygon News ingest →", path)

async def job_sec_daily():
    path = await run_sec_daily_index()
    print("SEC daily index →", path)

async def job_labeler():
    if not os.path.exists(EVENTS_PATH): return
    events = pd.read_parquet(EVENTS_PATH)
    unlabeled = events.tail(200).copy()
    rows = []
    for _, ev in unlabeled.iterrows():
        ticker = ev.get("primary_ticker","") or ""
        if not ticker: continue
        ts = pd.to_datetime(ev["datetime_utc"], utc=True)
        price_df = await fetch_window_prices(ticker, ts)
        if price_df is None: continue
        labels = compute_basic_labels(price_df, ts)
        if labels is None: continue
        labels["event_id"] = ev["event_id"]
        labels["primary_ticker"] = ticker
        rows.append(labels)
    if rows:
        df = pd.DataFrame(rows)
        write_parquet(df, "computed_labels")
        print(f"Labeled {len(df)} events.")

def start_scheduler():
    sched = AsyncIOScheduler()
    sched.add_job(job_gdelt, "interval", minutes=15, next_run_time=None)
    sched.add_job(job_polygon_news, "interval", minutes=2, next_run_time=None)
    sched.add_job(job_sec_daily, "interval", minutes=60, next_run_time=None)
    sched.add_job(job_labeler, "interval", minutes=1, next_run_time=None)
    sched.start()
    return sched

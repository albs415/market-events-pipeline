import aiohttp, pandas as pd, datetime as dt
from ..config import POLYGON_API_KEY, UNIVERSE
from ..storage import append_parquet

BASE = "https://api.polygon.io/v2/reference/news"

async def run_polygon_news_ingest():
    if not POLYGON_API_KEY:
        return None
    async with aiohttp.ClientSession() as session:
        params = {
            "apiKey": POLYGON_API_KEY,
            "limit": 100,
            "order": "desc",
            "tickers": ",".join(UNIVERSE[:50]) if UNIVERSE else None
        }
        async with session.get(BASE, params=params, timeout=60) as resp:
            resp.raise_for_status()
            data = await resp.json()
    results = data.get("results", [])
    rows = []
    for r in results:
        dt_utc = r.get("published_utc") or dt.datetime.utcnow().isoformat()+"Z"
        url = r.get("article_url") or r.get("amp_url") or ""
        tickers = ",".join([t.get("ticker","") for t in r.get("tickers",[])])
        title = r.get("title","")
        eid = f"POLYNEWS-{abs(hash(url))%10**10}"
        rows.append({
            "event_id": eid,
            "datetime_utc": dt_utc,
            "event_type": "Follow-on/Media",
            "cause": title[:120],
            "action_summary": title,
            "primary_ticker": r.get("tickers",[{"ticker":""}])[0].get("ticker",""),
            "related_tickers": tickers,
            "source_url": url,
            "adjacency_window_min": 60,
            "adjacency_event_ids": "",
            "notes": "Polygon News"
        })
    if rows:
        df = pd.DataFrame(rows).drop_duplicates(subset=["event_id"])
        return append_parquet(df, "events_master")

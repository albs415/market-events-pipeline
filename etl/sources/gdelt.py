import aiohttp, pandas as pd, datetime as dt
from ..storage import append_parquet

GKG_LATEST = "http://api.gdeltproject.org/api/v2/gkg/lastupdate-translation.txt"
EVENTS_LATEST = "http://api.gdeltproject.org/api/v2/events/lastupdate.txt"

async def _download_text(session, url):
    async with session.get(url, timeout=60) as resp:
        resp.raise_for_status()
        return await resp.text()

async def fetch_gdelt_latest(session) -> dict:
    latest = {}
    for url in (GKG_LATEST, EVENTS_LATEST):
        text = await _download_text(session, url)
        lines = [x for x in text.strip().splitlines() if x]
        files = [l.split()[-1] for l in lines if l.startswith("http")]
        latest[url] = files[:10]
    return latest

async def run_gdelt_ingest():
    async with aiohttp.ClientSession() as session:
        latest = await fetch_gdelt_latest(session)
        rows = []
        now = dt.datetime.utcnow().isoformat() + "Z"
        for kind, files in latest.items():
            for f in files:
                rows.append({
                    "event_id": f"GDELT-{abs(hash(f))%10**10}",
                    "datetime_utc": now,
                    "event_type": "Follow-on/Media",
                    "cause": "GDELT item",
                    "action_summary": f"See {f}",
                    "primary_ticker": "",
                    "related_tickers": "",
                    "source_url": f,
                    "adjacency_window_min": 60,
                    "adjacency_event_ids": "",
                    "notes": "GDELT ingest metadata"
                })
        if rows:
            df = pd.DataFrame(rows)
            return append_parquet(df, "events_master")

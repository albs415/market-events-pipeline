import aiohttp, pandas as pd
from ..config import POLYGON_API_KEY

async def polygon_agg_minutes(session, ticker: str, start: str, end: str, limit=5000):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start}/{end}"
    params = {"adjusted":"true","sort":"asc","limit":limit,"apiKey":POLYGON_API_KEY}
    async with session.get(url, params=params, timeout=60) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get("results", [])

async def fetch_window_prices(ticker: str, event_ts: pd.Timestamp):
    if not POLYGON_API_KEY: return None
    start = (event_ts - pd.Timedelta("2D")).strftime("%Y-%m-%d")
    end   = (event_ts + pd.Timedelta("5D")).strftime("%Y-%m-%d")
    async with aiohttp.ClientSession() as session:
        res = await polygon_agg_minutes(session, ticker, start, end)
    if not res: return None
    df = pd.DataFrame(res)
    df["datetime_utc"] = pd.to_datetime(df["t"], unit="ms", utc=True)
    df.rename(columns={"o":"open","h":"high","l":"low","c":"close","v":"volume"}, inplace=True)
    return df[["datetime_utc","open","high","low","close","volume"]]

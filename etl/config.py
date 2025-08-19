import os
from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY","")
UNIVERSE = [x.strip() for x in os.getenv("UNIVERSE","NVDA,TSLA,MSFT,AMD,UNH").split(",") if x.strip()]
DATA_DIR = os.getenv("DATA_DIR","./data")
TIMEZONE = os.getenv("TIMEZONE","America/New_York")
ENABLE_DUCKDB = os.getenv("ENABLE_DUCKDB","true").lower() == "true"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "parquet"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "raw"), exist_ok=True)

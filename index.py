"""Vercel entrypoint for the QQQ Reversal Engine."""

from pathlib import Path
import sys

ENGINE_DIR = Path(__file__).resolve().parent / "qqq-reversal-engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from app.main import app  # noqa: E402,F401

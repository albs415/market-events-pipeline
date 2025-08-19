from dataclasses import dataclass, asdict

EVENT_TYPES = [
    "Earnings","FOMC Decision","Macro Data","Institutional Filing/13F",
    "Policy Announcement","Regulatory Approval/Delay","Company Update",
    "Analyst Commentary","Tech Breakthrough/AI","Earnings Preview",
    "Follow-on/Media","Earnings Calendar","Macro Calendar"
]

@dataclass
class EventRow:
    event_id: str
    datetime_utc: str
    event_type: str
    cause: str
    action_summary: str
    primary_ticker: str
    related_tickers: str
    source_url: str
    adjacency_window_min: int
    adjacency_event_ids: str
    notes: str = ""

def to_dict(obj): return asdict(obj)

LABEL_FIELDS = [
    "gap_pct","ret_30m","ret_1h","ret_1d","ret_5d",
    "abnormal_ret_1h","vol_zscore_30m","direction",
    "impact_level","breakout_flag"
]

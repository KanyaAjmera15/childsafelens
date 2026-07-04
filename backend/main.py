"""
main.py — ChildSafeLens demo backend.

Three endpoints, matching the API contract in the July 9 Demo Implementation
Guide:

    POST /predict     -> score a message for risk
    POST /log-event    -> log a risk event (risk level + timestamp only, never text)
    GET  /events        -> aggregated counts for the dashboard

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Then B (input app) and D (dashboard) point their API_BASE_URL at wherever
this ends up deployed (see README.md for Render/Railway steps).
"""

import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import score_text

app = FastAPI(title="ChildSafeLens Demo API")

# Wide-open CORS for the demo — both the input app and the dashboard app
# call this from Expo Go / emulators on different origins. Tighten this
# before any real deployment beyond the demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory event store — fine for a demo. Swap for SQLite/Postgres later
# (see README.md) without changing the endpoints below.
_events = []

RiskLevel = Literal["low_risk", "medium_risk", "high_risk"]


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class PredictResponse(BaseModel):
    risk_score: float
    is_risky: bool
    label: RiskLevel


class LogEventRequest(BaseModel):
    risk_level: RiskLevel
    timestamp: str | None = None  # ISO 8601; server fills this in if omitted


class LogEventResponse(BaseModel):
    status: str
    event_id: str


class EventsResponse(BaseModel):
    total_events: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    risk_score, label, is_risky = score_text(req.text)
    return PredictResponse(risk_score=round(risk_score, 4), is_risky=is_risky, label=label)


@app.post("/log-event", response_model=LogEventResponse)
def log_event(req: LogEventRequest):
    timestamp = req.timestamp or datetime.now(timezone.utc).isoformat()
    event_id = f"evt_{uuid.uuid4().hex[:8]}"

    _events.append({
        "event_id": event_id,
        "risk_level": req.risk_level,
        "timestamp": timestamp,
    })

    return LogEventResponse(status="ok", event_id=event_id)


@app.get("/events", response_model=EventsResponse)
def get_events():
    high = sum(1 for e in _events if e["risk_level"] == "high_risk")
    medium = sum(1 for e in _events if e["risk_level"] == "medium_risk")
    low = sum(1 for e in _events if e["risk_level"] == "low_risk")

    return EventsResponse(
        total_events=len(_events),
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
    )


@app.delete("/events")
def clear_events():
    """Handy during rehearsal to reset the dashboard between test runs."""
    _events.clear()
    return {"status": "cleared"}

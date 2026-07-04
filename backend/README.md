# ChildSafeLens Demo Backend

FastAPI service for the July 9 demo. Implements `/predict`, `/log-event`,
and `/events` exactly as specified in the API contract.

## 1. Run it locally

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` — FastAPI gives you a free interactive
test page for all three endpoints, no need to write curl commands to try it.

## 2. Plug in the real trained model (optional for early testing)

Until you add a real model file, the API runs on a small built-in keyword
fallback (see `model.py`) so B and D are never blocked. To use the real
97.52%-accuracy pipeline:

1. In your training notebook/script, save the fitted vectorizer(s) and
   classifier together:
   ```python
   import joblib
   joblib.dump(
       {"word_vectorizer": word_tfidf, "classifier": clf},
       "model.pkl",
   )
   ```
2. Drop `model.pkl` into this `backend/` folder.
3. Restart the server — `model.py` auto-detects it and switches over. The
   console will print `Loaded real trained model from ...` when it works.

If your production pipeline also uses a character-level vectorizer or
custom behavioural features, see the `ADAPT HERE` comment in `model.py` —
you need to reproduce the same feature assembly at inference time as you
used during training.

## 3. Deploy so B and D can reach it from their phones

Render (free tier, simplest for a 5-day demo):

1. Push this `backend/` folder to a GitHub repo.
2. On [render.com](https://render.com) → New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy. Render gives you a public URL like `https://childsafelens-api.onrender.com`.
6. Share that URL with B and D immediately — they set it as `API_BASE_URL`
   in their apps (see the mobile-app README).

Railway works the same way if you prefer it instead.

## 4. Quick manual test

```bash
curl -X POST https://<your-url>/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "you are so stupid, i hate you"}'

curl -X POST https://<your-url>/log-event \
  -H "Content-Type: application/json" \
  -d '{"risk_level": "high_risk"}'

curl https://<your-url>/events
```

## 5. Resetting between rehearsals

`DELETE /events` wipes the in-memory event list so the dashboard starts
from zero counts before a demo run-through.

## Notes

- Events store only `risk_level` and `timestamp` — never message text —
  matching the privacy principle in the full Implementation Plan.
- The in-memory list resets whenever the server restarts. That's fine for
  the demo; swap in SQLite (a few lines with `sqlite3` or `SQLModel`) if you
  want counts to survive restarts during rehearsal week.

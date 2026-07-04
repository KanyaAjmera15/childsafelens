"""
model.py — wraps the risk-scoring model behind one function: score_text(text).

HOW TO PLUG IN YOUR REAL TRAINED MODEL (the 97.52% accuracy TF-IDF + LinearSVC
pipeline from the Base Paper Analysis):

1. In your training script, after fitting, save both the vectorizer(s) and the
   classifier together in one file:

       import joblib
       joblib.dump(
           {
               "word_vectorizer": word_tfidf,      # your word-level TfidfVectorizer
               "char_vectorizer": char_tfidf,      # your char-level TfidfVectorizer
               "classifier": clf,                  # your tuned LinearSVC
           },
           "model.pkl",
       )

   (If you only used one vectorizer, just drop the char_vectorizer key and
   the corresponding line below — search for "ADAPT HERE".)

2. Copy model.pkl into this backend/ folder (same directory as this file).

3. Restart the server. On startup this file will detect model.pkl and use
   your real model automatically. Until then, it runs on a small built-in
   fallback so the API works out of the box for integration testing.
"""

import os
import math
import joblib

MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(os.path.dirname(__file__), "model.pkl"))

_model_bundle = None
_using_real_model = False

if os.path.exists(MODEL_PATH):
    try:
        _model_bundle = joblib.load(MODEL_PATH)
        _using_real_model = True
        print(f"[model.py] Loaded real trained model from {MODEL_PATH}")
    except Exception as e:
        print(f"[model.py] Found {MODEL_PATH} but failed to load it: {e}")
        print("[model.py] Falling back to the built-in placeholder scorer.")
else:
    print(f"[model.py] No model.pkl found at {MODEL_PATH}.")
    print("[model.py] Using the built-in placeholder scorer until the real model is dropped in.")


# ---------------------------------------------------------------------------
# Real model path
# ---------------------------------------------------------------------------
def _score_with_real_model(text: str):
    word_vec = _model_bundle["word_vectorizer"]
    clf = _model_bundle["classifier"]

    # ADAPT HERE: if you also trained a character-level vectorizer and
    # concatenated features (word TF-IDF + char TF-IDF + custom features)
    # before fitting LinearSVC, reproduce that exact same feature assembly
    # here so the shapes match what the classifier expects. Example:
    #
    #   from scipy.sparse import hstack
    #   char_vec = _model_bundle["char_vectorizer"]
    #   X = hstack([word_vec.transform([text]), char_vec.transform([text])])
    #
    X = word_vec.transform([text])

    # LinearSVC has no predict_proba by default. decision_function gives a
    # signed distance from the boundary; squashing it through a sigmoid
    # gives a usable 0-1 "risk score" for the nudge threshold and dashboard.
    raw_score = clf.decision_function(X)[0]
    risk_score = 1 / (1 + math.exp(-raw_score))

    return risk_score


# ---------------------------------------------------------------------------
# Fallback path (used only until model.pkl is provided)
# ---------------------------------------------------------------------------
_FALLBACK_FLAG_WORDS = [
    "kill", "die", "hate", "ugly", "stupid", "idiot", "loser", "worthless",
    "kameena", "kameenaa", "kameenaaa", "chutiya", "gadha", "g@dha",
    "bakwaas", "nikamma", "besharam", "harami",
]


def _score_with_fallback(text: str):
    lowered = text.lower()
    hits = sum(1 for w in _FALLBACK_FLAG_WORDS if w in lowered)

    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    exclaim_count = text.count("!")

    score = 0.15  # baseline
    score += 0.35 * min(hits, 2)
    score += 0.15 if caps_ratio > 0.4 else 0
    score += 0.05 * min(exclaim_count, 2)

    return min(score, 0.98)


def _label_for(score: float) -> str:
    if score >= 0.7:
        return "high_risk"
    if score >= 0.4:
        return "medium_risk"
    return "low_risk"


def score_text(text: str):
    """
    Returns (risk_score: float in [0, 1], label: str, is_risky: bool)
    """
    if not text or not text.strip():
        return 0.0, "low_risk", False

    if _using_real_model:
        risk_score = _score_with_real_model(text)
    else:
        risk_score = _score_with_fallback(text)

    label = _label_for(risk_score)
    is_risky = risk_score >= 0.5

    return risk_score, label, is_risky

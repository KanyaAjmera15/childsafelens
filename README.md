# ChildSafeLens

An AI-powered, pre-emptive, on-device system to nudge senders away from
cyberbullying / harmful messages before they're sent — built for Hinglish
and code-mixed Indian social text.

Background and research context: see `docs/`.

## Repo layout

```
childsafelens/
├── backend/              FastAPI service — /predict, /log-event, /events
├── mobile-dashboard/     Parent dashboard (Expo / React Native) — real product
├── mobile-input-demo/    DEMO ONLY prototype for the July 9 milestone — see note below
├── android-app/          Real child-facing native Android app (Phase 2+) — placeholder for now
├── ml/                   Model training scripts, notebooks, dataset notes
├── docs/                 Base paper analysis, implementation plan, demo guide
└── README.md             this file
```

## ⚠️ Important: demo prototype vs. real product

`mobile-input-demo/` is a throwaway Expo prototype built only to prove the
concept end-to-end for the July 9 milestone (cloud-hosted model, simple text
box instead of real interception). It is **not** the final child-facing app.

The real product needs native Android (Kotlin) to hook into the
`AccessibilityService` / `InputMethodService` layer and intercept text
*inside other apps* before it's sent — something Expo/React Native cannot
do. That work lives in `android-app/` and starts in Phase 2 of the full
Implementation Plan (see `docs/`).

`backend/` and `mobile-dashboard/`, by contrast, **are** the real product —
what gets built for the demo directly becomes the production version, no
rewrite needed.

## Where to start

| I am... | Go to | 
|---|---|
| Working on the model | `ml/README.md` |
| Working on the backend API | `backend/README.md` |
| Working on the parent dashboard | `mobile-dashboard/README.md` |
| Working on the demo input prototype | `mobile-input-demo/README.md` |
| Working on the real Android app | `android-app/README.md` (Phase 2+) |
| Looking for the research/background docs | `docs/` |

## Architecture (current — demo phase)

```
[Input app] --POST /predict--> [Backend + model] --risk score-->
   -> if risky: show nudge
   -> POST /log-event --> [Backend stores event]

[Dashboard app] --GET /events--> renders counts/trend
```

This evolves per the full Implementation Plan into: on-device inference
(no network call per message), real AccessibilityService-based interception,
encrypted local event logs, and real parent–child pairing.

## Branching workflow

- `main` should always be in a working/deployable state.
- Work on `feature/<your-name>-<short-description>` branches.
- Open a PR into `main` even for small changes — keeps a record of who
  built what, useful once this becomes a submitted project.

## Team

| Area | Owner |
|---|---|
| ML (model training, benchmarking) | A |
| Backend | C |
| Parent dashboard | D |
| Android / input app | B |

## Docs

- `docs/ChildSafeLens_BasePaper_Analysis.docx` — base paper study, research gaps, finalised system
- `docs/ChildSafeLens_Implementation_Plan.docx` — full architecture, tech stack, roadmap
-base paper

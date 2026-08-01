# CLAUDE.md & Coding Rules

**Clinic-Specific AI Dental Screening** — Academic Prototype
Revised for: Solo, 4th-Year Capstone Project
Constraints: Free-tier infrastructure only · ~4 week timeline
Volume 0 of 5 — Coding Rules & Project Conventions (Revised)

## Scope Statement (Read First)

This is a solo, unfunded, 4th-year academic capstone prototype. It uses public/synthetic dental image datasets, not real patient records or PHI. Clinical-compliance language (HIPAA/GDPR/FDA) from earlier drafts has been removed from day-to-day engineering rules and is discussed only as future work in Volume 4. Treat this document as internal engineering conventions for a demo-grade system, not a production clinical product.

## 1. Project Overview & Stack

Clinic-AI is a demo dental screening & patient-record prototype. A dentist uploads an intraoral photo; a fine-tuned YOLOv8n model detects likely conditions (cavity, plaque, gingivitis); the dentist reviews/corrects the result; a simple PDF report is generated.

- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS. Hosted free on Vercel.
- **Backend:** FastAPI (Python 3.12). Hosted free on Render or Railway.
- **Database:** MongoDB Atlas, free M0 tier (512MB).
- **Image storage:** Cloudinary free tier.
- **AI/ML:** Ultralytics YOLOv8n, trained on Google Colab / Kaggle free GPU.
- **Roles:** Dentist, Receptionist, Admin (simplified RBAC — no MFA, no audit-log retention requirement).

> **Note:** YOLOv8 is licensed AGPL-3.0. For a non-commercial student prototype this is not a blocker. If you ever turn this into a commercial product, revisit the license (Ultralytics Enterprise license, or switch detectors).

## 2. Common Commands

| Area | Command | Where |
|---|---|---|
| Frontend install | `npm install` | `/frontend` |
| Frontend dev server | `npm run dev` | `/frontend` |
| Frontend lint | `npm run lint --fix` | `/frontend` |
| Backend install | `pip install -r requirements.txt` | `/backend` |
| Backend dev server | `uvicorn app.main:app --reload` | `/backend` |
| Backend tests | `pytest` | `/backend` |
| AI — train (Colab) | `yolo detect train data=data.yaml model=yolov8n.pt epochs=40 imgsz=640` | Colab notebook |
| AI — quick local test | `python ai_model/predict.py --source sample.jpg` | `/ai_model` |

## 3. Architecture Decisions

- Single backend language: Python 3.12 (FastAPI). Single frontend framework: Next.js 15. Do not mix in Express, Flask, or Vite mid-project.
- REST only, JSON everywhere. No GraphQL.
- JWT auth stored in an httpOnly, Secure, SameSite cookie — not localStorage (avoids XSS token theft).
- One MongoDB database on the free Atlas M0 cluster. Keep documents small; free tier caps storage at 512MB, so store only image URLs (Cloudinary), never binary image blobs, in MongoDB.
- AI inference runs inside the FastAPI backend process (load model once at startup) — no separate microservice, to keep the free-tier deployment simple.
- No Kubernetes, no separate GPU inference server. Free-tier web hosts are CPU-only; YOLOv8n is chosen specifically because it is fast enough on CPU for a demo.

## 4. Code Style & Linting

- **Frontend:** TypeScript, ESLint + Prettier, functional React components + hooks, Tailwind utility classes (no inline CSS).
- **Backend:** PEP8, Black + Flake8, Pydantic v2 models with full type hints on every route.
- **Commit messages:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).

## 5. Branching & Workflow (Solo)

A simplified trunk-based flow, adjusted for a solo developer on a tight timeline:

- `main` is always the last known-working state.
- Create a short-lived `feature/<name>` branch per task (e.g. `feature/patient-crud`). Merge to `main` once it runs locally and passes lint.
- Formal PR review is skipped (solo project) but each merge should be a single, working, buildable commit — treat your own merge as the code review checkpoint.
- Tag a release only at the end (`v1.0`) for submission/demo purposes.

## 6. Quality Requirements

- Every new API route should have at least one happy-path pytest test before moving to the next task — don't let tests pile up at the end.
- Run lint before every commit.
- HTTPS is provided automatically by Vercel/Render — no manual TLS setup needed.

## 7. Secrets & Environment

| Variable | Purpose | Where |
|---|---|---|
| `MONGODB_URI` | Atlas connection string | `backend/.env` |
| `JWT_SECRET` | Sign/verify auth tokens | `backend/.env` |
| `CLOUDINARY_URL` | Image upload/storage | `backend/.env` |
| `NEXT_PUBLIC_API_URL` | Backend base URL | `frontend/.env.local` |

> **Note:** Never commit `.env` files. Provide a checked-in `.env.example` with empty values as a template.

## 8. UI Design Tokens (Summary)

Full design system is in Volume 3 (UI/UX Spec, Revised). Core tokens:

- Primary `#1976D2`, Secondary `#26A69A`, Error `#F44336`, Success `#4CAF50`
- Font: Inter/system sans-serif. Base spacing unit: 8px grid.
- Use the shared Button, TextInput, Card, Modal, and Table components everywhere — no raw HTML form elements.

## 9. Realistic Solo Timeline (~4 Weeks)

| Week | Focus |
|---|---|
| 1 | Project setup, auth, Patient & Visit CRUD (backend + frontend) |
| 2 | Image upload (Cloudinary) + YOLOv8n training on Colab + inference API |
| 3 | Dentist review/correction UI, PDF report generation, (stretch) Grad-CAM |
| 4 | Polish, basic tests, free-tier deployment, write-up/demo prep |

See Volume 5 (Implementation Backlog, Revised) for the full day-by-day task list.

## 10. What Was Removed From The Original Plan

For transparency — the earlier draft of this plan assumed a funded team with paid cloud infra and real patient data. These items were cut or deferred to a "Future Work" section rather than attempted on a free/solo budget:

- Multi-agent Claude Code "teams" workflow (only relevant with multiple parallel developers)
- Kubernetes / managed cloud GPU inference, Prometheus + Grafana monitoring stack
- Automated retraining pipeline / MLOps CI
- Multi-language (i18n) support, full analytics dashboard, appointment scheduling
- HIPAA/GDPR compliance infrastructure (BAAs, KMS encryption, 6-year audit retention, MFA) — not applicable while using non-PHI demo data

## 11. Sources

Based on standard Claude Code / CLAUDE.md conventions, trunk-based development practice, and Material Design system principles, adapted down to a free-tier, solo, time-boxed academic context.

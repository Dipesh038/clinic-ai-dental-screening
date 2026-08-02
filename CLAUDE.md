# Repository Structure & Development Commands

This repository contains the **Clinic-Specific AI Dental Screening** application.

## Architecture
- **Frontend (Root `/`)**: Next.js 15 (App Router), TypeScript, Tailwind CSS v4, React 19.
- **Backend (`/backend`)**: FastAPI, Python 3.12+, MongoDB (Motor), Ultralytics YOLOv8 + Grad-CAM AI inference engine.

## Local Development Commands

### Frontend (run from root `/`)
- Install dependencies: `npm install`
- Run dev server: `npm run dev` (starts on `http://localhost:3000`)
- Production build test: `npm run build`

### Backend (run from `/backend`)
- Activate venv: `source .venv/bin/activate` (or `.venv/bin/python`)
- Run API server: `uvicorn app.main:app --reload` (starts on `http://localhost:8000`)
- Run pytest suite: `pytest`
- Seed users (admin, dentist, receptionist): `python scripts/seed_users.py`

## Live Deployment Links
- **Frontend (Vercel)**: `https://clinic-ai-dental-screening.vercel.app`
- **Backend (Render)**: `https://ai-dental-screening-backend.onrender.com`

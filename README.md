# Clinic-Specific AI Dental Screening

An AI-assisted dental screening system for small clinics. Dentists and receptionists manage
patients and visits, upload intraoral photos, and get automatic cavity/plaque detection
(YOLOv8) with bounding-box overlays — which the dentist can review, correct, and turn into a
downloadable PDF report.

**Live app:** [clinic-ai-dental-screening.vercel.app](https://clinic-ai-dental-screening.vercel.app)
**Backend API:** [ai-dental-screening-backend.onrender.com](https://ai-dental-screening-backend.onrender.com)

> The backend runs on Render's free tier, so the first request after a period of inactivity
> can be slow to wake up. See [Known limitations](#known-limitations) below.

---

## Screenshots

| Login | Visit detail & upload |
|---|---|
| ![Login screen](docs/report/01-login.png) | ![Visit detail with uploaded dental image](docs/report/05-visit-detail.png) |

| AI review — detections & Grad-CAM |
|---|
| ![AI review page showing cavity/plaque bounding boxes and detection list](docs/report/06-ai-review.png) |

---

## Features

- **Patient & visit management** — searchable patient list, visit timeline per patient,
  soft-delete, role-restricted access.
- **AI-powered screening** — upload an intraoral JPEG/PNG and a YOLOv8n model automatically
  detects cavities and plaque, drawing bounding boxes on the image.
- **Explainability (Grad-CAM)** — per-detection heatmap overlay showing which pixels drove a
  prediction (implemented end-to-end; see [AI model](#ai-model) for where it runs).
- **Dentist review workflow** — accept, edit, add, or delete AI-predicted bounding boxes;
  corrections are saved separately from the raw AI output so both are always available.
- **PDF reports** — one-click, per-visit report generation (patient info, image, findings)
  for printing or download.
- **Role-based access** — `admin` (read-only oversight), `dentist` (full review/edit/report
  access), `receptionist` (patient/visit intake) enforced on both the API and the UI.
- **Dashboard** — clinic-wide totals: patients, visits, pending AI reviews.
- **Dark mode**, responsive layout (mobile/tablet/desktop), and a WCAG AA-checked UI.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS v4, React 19 |
| Backend | FastAPI, Python 3.12+ |
| Database | MongoDB (via Motor, async driver) |
| Image storage | Cloudinary |
| AI inference | Ultralytics YOLOv8n |
| Explainability | Grad-CAM (`pytorch-grad-cam`) over a ResNet18 classifier |
| Auth | JWT in an httpOnly cookie, bcrypt-hashed passwords |
| Reports | ReportLab (PDF generation) |
| Testing | pytest (backend) |
| CI/CD | GitHub Actions (lint + test on push), Vercel (frontend), Render (backend) |

---

## AI model

Trained YOLOv8n model, validated on a held-out set:

| Metric | Value |
|---|---|
| Overall mAP50 | 0.837 (83.7%) |
| Cavity mAP50 | 0.910 (91.0%) |
| Plaque mAP50 | 0.763 (76.3%) |
| Inference speed | 2.6 ms/image |
| Weights size | ~6.2 MB (`best.pt`) |

Full write-up: [`docs/AI_Results.md`](docs/AI_Results.md).

**Grad-CAM note:** the heatmap pipeline (crop → classify → Grad-CAM → overlay) is fully
implemented and works when run locally. It's disabled on the hosted Render backend
(`ENABLE_GRAD_CAM=false`) because it needs gradient computation and keeps a second model
resident in memory, which reproducibly exceeds the free tier's 512 MB limit. The frontend
detects this automatically and hides the "Show Heatmap" option when it isn't available.

---

## Project structure

```
.
├── app/                  # Next.js App Router pages (frontend)
├── components/           # Shared React components (UI, layout, forms)
├── lib/                  # Frontend API client + typed fetch helpers
├── backend/
│   ├── app/
│   │   ├── routers/      # FastAPI route modules (auth, patients, visits, images, dashboard)
│   │   ├── models/       # Pydantic models
│   │   ├── ai.py         # YOLO model loading + inference
│   │   ├── grad_cam.py   # Grad-CAM heatmap generation
│   │   └── report.py     # PDF report generation
│   ├── ai_model/weights/ # Trained YOLOv8n weights (best.pt)
│   ├── scripts/          # Admin/user seed scripts
│   └── tests/            # pytest suite
└── docs/                 # Model results, roadmap, internship report
```

---

## Getting started

### Prerequisites
- Node.js 20+
- Python 3.12+
- A MongoDB Atlas connection string (free M0 tier is enough)
- A Cloudinary account (free tier is enough)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then fill in MONGODB_URI, JWT_SECRET, CLOUDINARY_URL
uvicorn app.main:app --reload    # http://localhost:8000
```

Seed the default users (admin / dentist / receptionist):

```bash
python scripts/seed_users.py
```

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `JWT_SECRET` | Secret used to sign/verify auth tokens |
| `CLOUDINARY_URL` | Cloudinary connection URL |
| `COOKIE_SECURE` | `false` for local HTTP dev, `true` in production (default) |
| `FRONTEND_ORIGIN` | Origin allowed to call the API with credentials |
| `ENABLE_GRAD_CAM` | Enable the Grad-CAM heatmap endpoint (default `true`) |

### Frontend

```bash
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                        # http://localhost:3000
```

### Tests

```bash
cd backend
pytest
```

---

## Known limitations

- **Cold starts:** the backend runs on Render's free tier, which spins down after ~15
  minutes idle and takes ~110s to wake (it loads PyTorch + the YOLO model at startup). A
  scheduled GitHub Action pings `/health` every 10 minutes to keep it warm, but an
  occasional cold start is still possible.
- **Grad-CAM is production-disabled:** see [AI model](#ai-model) above — it's a genuine,
  working part of the project, just memory-gated on the free hosting tier.
- **Grad-CAM uses a generic classifier:** the heatmap model is a pretrained ImageNet
  ResNet18, not a dental-specific model, so heatmaps demonstrate the pipeline rather than
  giving medically fine-tuned explanations. Tracked in [`docs/Future_Work.md`](docs/Future_Work.md).
- **Single clinic only:** there's no multi-tenant/clinic entity yet — all data belongs to
  one clinic.

---

## Roadmap

See [`docs/Future_Work.md`](docs/Future_Work.md) for the full list, including an automated
model-retraining pipeline from dentist corrections, a dental-specific Grad-CAM classifier,
trend/analytics reporting, and multi-tenant clinic support.

---
title: "Weekly Internship Report"
author: "Dipesh Kunwar"
date: "27 July 2026"
---

# WEEKLY INTERNSHIP REPORT

**Intern:** Dipesh Kunwar
**Reference ID:** SMM2026INT13073
**Organization:** Suvidha Mahila Mandal, Walni (Suvidha Foundation)
**Role:** Web Development Intern
**Duration:** 27 May 2026 – 27 July 2026
**Project:** Clinic-Specific AI Dental Screening

*Note: The internship's granular day-to-day log was tracked internally as a task-ID-based backlog (`T101`–`T412`) rather than dated diary entries. The breakdown below maps that backlog structure onto the internship's calendar weeks as accurately as the available project documentation allows; where an exact week-by-week date split was not separately recorded, work is grouped by its documented development phase and flagged accordingly.*

---

## Week 1–2 (approx. 27 May – 09 June 2026): Project Setup, Authentication & Core CRUD

| Day(s) | Work Performed |
|---|---|
| Setup | Repository scaffolding (`frontend/`, `backend/`, `ai_model/`, `docs/`); `CLAUDE.md` project conventions established |
| | Next.js 15 frontend initialized (TypeScript, Tailwind CSS, App Router) |
| | FastAPI backend initialized with a working `/health` endpoint |
| | Backend connected to MongoDB Atlas on startup |
| | User model and bcrypt password hashing implemented |
| | `POST /api/auth/login` implemented, issuing JWT in an httpOnly cookie |
| | Role-check dependency added for dentist/receptionist/admin roles |
| | Admin user seed script written |
| | Frontend login page and cookie-based auth flow built |
| | Protected frontend routes via an auth-aware proxy/middleware |
| | Patient model and full CRUD (with soft-delete) implemented |
| | Patient List page (with search) and Add/Edit forms built |
| | Visit model and CRUD endpoints implemented |
| | Visit timeline UI on the Patient Profile page, plus a New Visit form |
| | Automated tests added for auth/patient/visit endpoints |
| | Route-level role restrictions applied to patient/visit endpoints |

**Milestone:** Week 1 backlog (Authentication, Patient & Visit CRUD) completed and verified running locally.

---

## Week 3–4 (approx. 10 – 23 June 2026): Image Upload & AI Integration

| Day(s) | Work Performed |
|---|---|
| | Cloudinary SDK configured in the backend |
| | Multipart image-upload endpoint built, persisting Cloudinary URLs against visits |
| | Frontend image-upload component with preview, wired into the visit detail page |
| | Server-side upload validation added (JPEG/PNG only, 5 MB max) |
| | YOLOv8n model training run on Google Colab (free-tier GPU) |
| | Validation metrics recorded (`docs/AI_Results.md`) |
| | Trained weights (`best.pt`) integrated into the backend AI module |
| | Backend startup updated to load the YOLO model once, with graceful degradation if unavailable |
| | `POST /api/images/{image_id}/predict` endpoint implemented |
| | YOLO class indices mapped to disease names (cavity/plaque/gingivitis) |
| | Prediction schema and MongoDB persistence added |
| | Upload flow updated to auto-trigger AI prediction after storage |
| | AI Review page built, with detection overlays and a bounding-box list |
| | JPEG/PNG EXIF metadata stripped from uploads prior to storage (privacy safeguard) |
| | Basic inference logging added (latency, detection count) |
| | Contract tests added for the prediction API response shape |
| | macOS Python 3.9 compatibility fixes and cross-domain cookie auth fix applied |

**Milestone:** Week 2 backlog (Image Upload + AI Integration) completed.

---

## Week 5–6 (approx. 24 June – 07 July 2026): Dentist Review, PDF Reporting & Dashboard

| Day(s) | Work Performed |
|---|---|
| | Correction model and endpoints built (`POST`/`GET` corrections per image) |
| | Correction UI added — bounding-box edit/draw/delete on the AI Review page |
| | "Mark as Reviewed" endpoint and button implemented |
| | PDF report generator built with ReportLab; `GET /api/visits/{id}/report` endpoint added |
| | Identified and fixed a data-model mismatch bug that would have made every real PDF report download fail |
| | Extended the backend test double (`FakeCollection`) to support `sort=` and `count_documents()`, and added the missing report/dashboard tests this bug exposed |
| | "Download Report" button added to the visit detail page |
| | Grad-CAM heatmap generation pipeline implemented (stretch goal) with a frontend toggle |
| | Dashboard statistics endpoint and UI built (total patients, total visits, pending reviews) |
| | Full responsive-design pass at 375px/768px/1440px; two real layout bugs found and fixed |
| | Full accessibility audit (`@axe-core/playwright`); four violations found and fixed, reaching zero violations |
| | Backend test suite expanded to 46 passing tests |
| | Toast notification component added for review/save feedback |

**Milestone:** Week 3 backlog (Dentist Review, PDF Report, Dashboard) completed, including the stretch-goal Grad-CAM feature.

---

## Week 7–9 (approx. 08 – 27 July 2026): Hardening, Deployment, Documentation & Final Polish

| Day(s) | Work Performed |
|---|---|
| | Continuous manual run-through and bug-fixing across the application |
| | Backend deployed to Render (live at `ai-dental-screening-backend.onrender.com`) |
| | Frontend deployed to Vercel (live at `clinic-ai-dental-screening.vercel.app`) |
| | Production connectivity to MongoDB Atlas and Cloudinary verified |
| | GitHub Actions CI pipeline added (lint + pytest on every push) |
| | README rewritten with full setup/run instructions |
| | `docs/AI_Results.md` updated with Grad-CAM explainability notes |
| | `docs/Future_Work.md` written, documenting the post-internship roadmap |
| | Repository restructuring (frontend moved to repo root) and deployment-config fixes (Vercel/Render routing, CORS, ESLint flat-config) |
| | Final cleanup — unused code and raw datasets removed |
| | Breadcrumb navigation and a print-optimized PDF report layout added |
| | Global light/dark theme implemented (`next-themes`), with design tokens re-tuned for WCAG AA contrast in both modes |
| | Admin access extended to patients/visits routes; minor bug fixes |
| | Final internship report compiled |

**Milestone:** Week 4 backlog (CI, Deployment, Documentation) completed; project reached a stable, deployed, documented state ahead of internship completion on 27 July 2026.

---

## Summary of Weekly Effort

| Metric | Value |
|---|---|
| Total internship duration | 27 May 2026 – 27 July 2026 (~9 weeks) |
| Minimum daily commitment | 4 hours/day, 6 days/week (per offer letter) |
| Backend automated tests (final) | 46 passing |
| Accessibility violations (final scan) | 0 |
| AI model validation mAP50 | 0.837 (83.7%) |
| Defects identified & resolved | 9 |
| Production deployments | 2 (frontend on Vercel, backend on Render) |

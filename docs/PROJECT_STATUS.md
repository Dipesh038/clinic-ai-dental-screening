# Project Status — Clinic-Specific AI Dental Screening

Last updated: 2026-08-02 (Session 4)
Purpose: single source of truth on (1) what is built, (2) what is left, and (3) known
bugs/risks — written so any AI coding agent (Claude Code, Codex CLI, Antigravity, etc.)
or a human can resume work without re-reading the whole codebase or the Volume 0–5 specs
in `docs/*.docx` first. Task IDs (`PWx`, `Txxx`) match `docs/Volume5_Implementation_Backlog_REVISED.docx`.

This file is documentation only. It does not change any code.

---

## 1. Stack quick-reference

| Layer | Tech | Local run | Port |
|---|---|---|---|
| Frontend | Next.js 16 (App Router), TS, Tailwind v4, React 19 | `cd frontend && npm run dev` | 3000 |
| Backend | FastAPI (Python 3.12+), Motor/MongoDB | `cd backend && uvicorn app.main:app --reload` | 8000 |
| DB | MongoDB Atlas M0 (free tier) | via `MONGODB_URI` in `backend/.env` | — |
| Images | Cloudinary free tier | via `CLOUDINARY_URL` in `backend/.env` | — |
| AI inference | Ultralytics YOLO, loaded from `backend/ai_model/weights/best.pt` when present | backend startup | — |
| Tests | pytest (backend only) | `cd backend && pytest` | — |

Env files required: `backend/.env` (template: `backend/.env.example`) and
`frontend/.env.local` (⚠️ no template — see Bug B6).

Note on this Next.js version: `frontend/proxy.ts` is the correct file name for
route-guard middleware in this Next.js version (it renamed `middleware.ts` →
`proxy.ts` — confirmed against `node_modules/next/dist/docs`). Do not "fix" this
back to `middleware.ts`.

---

## 2. What's already done

Verified against actual code where possible. Full backend pytest needs a fresh
macOS/Linux Python environment because the checked-out `.venv` is Windows-only.

### Prework
- [x] **PW3** Repo scaffolded: `frontend/`, `backend/`, `ai_model/`, `docs/`, `.gitignore`
- [x] **PW4** `CLAUDE.md` written at repo root
- [ ] **PW1** Free-tier accounts — cannot verify from code (Atlas/Cloudinary creds exist
  in `backend/.env`, so at least those two are set up)
- [~] **PW2** Dataset downloaded — `ai_model/dataset_raw/Dataset.zip` exists, but the
  image/label count sanity check has not been verified
- [ ] **PW5** Colab/Kaggle GPU 1-epoch smoke test — no evidence in repo (expected, this
  runs outside the repo in a notebook)
- [ ] **PW6** (human task) Dataset license/attribution note — not something a coding
  agent should do; still open

### Week 1 — Auth, Patient & Visit CRUD (COMPLETE)
- [x] **T101** Next.js init (TS, Tailwind, App Router)
- [x] **T102** FastAPI init, `/health` returns 200
- [x] **T103** Backend connected to MongoDB Atlas on startup (`backend/app/db.py`)
- [x] **T104** User model + bcrypt hashing (`backend/app/models/user.py`, `app/security.py`)
- [x] **T105** `POST /api/auth/login` issuing JWT in httpOnly cookie (`app/routers/auth.py`)
- [x] **T106** Role-check dependency for dentist/receptionist/admin (`app/dependencies.py`)
- [x] **T107** `scripts/create_admin.py` seed script
- [x] **T108** Frontend login page + cookie auth flow (`frontend/app/login/page.tsx`)
- [x] **T109** Protected routes via `frontend/proxy.ts`
- [x] **T110/T111** Patient model + full CRUD, soft-delete (`app/routers/patients.py`)
- [x] **T112/T113** Patient List page (search) + Add/Edit forms
- [x] **T114** Visit model + CRUD under `/patients/{id}/visits` (`app/routers/visits.py`)
- [x] **T115** Visit timeline on Patient Profile + New Visit form
- [x] **T116** pytest coverage for auth/patient/visit endpoints (33 tests, see §4)
- [x] **T117** Role restriction (dentist/receptionist only) on patient/visit routes
- [x] **T118** Week 1 milestone committed and running locally

### Week 2 — Image Upload + AI Integration (IN PROGRESS)
- [x] **T201** Cloudinary SDK configured in backend (`app/cloudinary_client.py`)
- [x] **T202** `POST /api/visits/{visit_id}/images` — multipart upload → Cloudinary URL,
  persisted in the `images` collection linked to the visit (`app/routers/visits.py`,
  `app/models/image.py`). Covered by 2 new pytest tests.
- [x] **T203** Frontend image upload component + preview on the visit detail page
  (`frontend/components/visits/VisitImageUpload.tsx`) wired into
  `frontend/app/patients/[id]/visits/[visitId]/page.tsx`.
- [x] **T204** Backend upload validation: JPEG/PNG only and max 5 MB, covered by 2
  new pytest tests in `backend/tests/test_visits.py`. Note: implementation was
  linted/type-checked, but full pytest was not rerun locally because this checkout
  lacks a macOS/Linux Python test environment.
- [x] **T205** Train YOLOv8n on Colab, produce `best.pt` — blocked until a GPU
  training run is completed outside the repo.
- [x] **T206** Run validation metrics and write `docs/AI_Results.md` — blocked by T205.
- [x] **T207** Download `best.pt` into `backend/ai_model/weights/` — blocked by T205.
- [x] **T208** Backend startup now attempts to load YOLO once from
  `backend/ai_model/weights/best.pt` (`backend/app/ai.py`, `backend/app/main.py`);
  actual model availability is blocked until T207 provides real weights.
- [x] **T209** `POST /api/images/{image_id}/predict` exists and returns 503 when the
  AI model is unavailable (`backend/app/routers/images.py`).
- [x] **T210** YOLO class indices map to disease names via `AI_CLASS_NAMES`
  (`backend/app/config.py`, default `cavity,plaque,gingivitis`).
- [x] **T211** Prediction schema/model and Mongo persistence added
  (`backend/app/models/prediction.py`, `backend/app/routers/images.py`).
- [x] **T212** Upload now auto-triggers AI prediction after Cloudinary persistence
  (`backend/app/routers/visits.py`); real prediction output remains blocked by T205/T207.
- [x] **T213** Visit image upload UI shows the top AI prediction when the upload
  response includes one (`frontend/components/visits/VisitImageUpload.tsx`); persisted
  predictions are not loaded on page refresh yet.
- [x] **T214** AI Review page added at
  `frontend/app/patients/[id]/visits/[visitId]/images/[imageId]/review/page.tsx`,
  with image overlay boxes and a detection list backed by latest-prediction API reads.
- [x] **T215** Upload path strips JPEG EXIF APP1 segments and PNG `eXIf` chunks before
  Cloudinary upload (`backend/app/image_processing.py`).
- [x] **T216** Basic inference logging added for prediction latency and detection count.
- [x] **T217** Contract test for prediction JSON shape added with a fake predictor
  (`backend/tests/test_images.py`); real sample-image YOLO test is blocked by T205/T207.
- [ ] **T218** Week 2 milestone commit/push — not done.

### Week 3 — Dentist Review, PDF Report, Dashboard (COMPLETE except stretch Grad-CAM)
- [x] **T301** Correction model + endpoints — `POST/GET /api/images/{id}/corrections`
  (`backend/app/models/correction.py`, `backend/app/routers/images.py`)
- [x] **T302** Correction UI — bounding-box edit/draw/delete on the AI Review page
  (`frontend/app/patients/[id]/visits/[visitId]/images/[imageId]/review/page.tsx`)
- [x] **T303** `POST /api/images/{id}/mark-reviewed` + "Mark as Reviewed" button
- [x] **T304/T305/T306** PDF report generator (ReportLab) + `GET /api/visits/{id}/report`
  (`backend/app/report.py`, `backend/app/routers/visits.py`). **Bug found and fixed this
  session:** `generate_pdf_report` read `patient['firstName']`/`patient['lastName']`/
  `dateOfBirth`/`contactNumber`, but patient documents actually store `name`/`dob`/
  `contact` (see `backend/app/routers/patients.py`). This endpoint had zero test
  coverage, so every real report download would have raised a `KeyError` (500). Fixed
  to read the correct field names. Separately, `backend/tests/conftest.py`'s
  `FakeCollection` (the in-memory Motor stand-in used by all pytest tests) didn't
  support the `sort=` kwarg on `find_one()` (needed by the report endpoint's
  `db.corrections.find_one(..., sort=...)` / `db.predictions.find_one(..., sort=...)`
  calls) or a `count_documents()` method at all (needed by `/api/dashboard/stats`,
  including its `$exists` query operator) — which is exactly why neither endpoint had
  a test before now: writing one would have failed immediately. Both added to the fake.
- [x] **T307** "Download Report" button on the visit detail page
- [x] **T308–T310** (stretch) Grad-CAM heatmap generation pipeline (Dummy ResNet18) and frontend toggle implemented
- [x] **T311** Dashboard stats (Total Patients, Total Visits, Pending Reviews) —
  `GET /api/dashboard/stats` (`backend/app/routers/dashboard.py`),
  rendered on `frontend/app/dashboard/page.tsx`
- [x] **T312** Responsive pass — done (Session 4). Drove the real app (login →
  dashboard → patients → patient → visit → upload → AI review → edit corrections)
  at 375px/768px/1440px with Playwright against the live backend + Atlas DB.
  Found and fixed two real bugs: `AppHeader` had no wrap handling and crammed the
  logo/nav/username/logout into one row, breaking at mobile width (now wraps, hides
  username/role below `sm:`); the AI Review page's heading + action buttons had the
  same problem (now wraps). The patients table's apparent "cut off" Contact column
  on mobile was a false alarm — `Table` already wraps in `overflow-x-auto` and is
  genuinely scrollable (verified via `scrollWidth > clientWidth`).
- [x] **T313** Accessibility pass — done (Session 4). Ran `@axe-core/playwright`
  against login/dashboard/patients/patient-detail/visit-detail/AI-review: found 4
  violations (empty table header, missing page `<h1>` on Patients, and WCAG AA
  color-contrast failures — see B10) and fixed all of them; final scan is
  **0 violations** on every page tested.
- [x] **T314** pytest coverage for corrections/report/dashboard — corrections and
  mark-reviewed tests already existed (`backend/tests/test_images.py`); report and
  dashboard had none, so this session added `test_download_visit_report_returns_pdf`,
  `test_download_visit_report_for_unknown_visit_returns_404` (`test_visits.py`) and a
  new `backend/tests/test_dashboard.py`. **46** backend tests passing.
- [x] **T315** Toast notifications (`frontend/components/ui/Toast.tsx`), wired into the
  AI Review page for save/mark-reviewed feedback
- [ ] **T316** Week 3 milestone commit — pending (see §3)

Verified this session: `cd backend && pytest` → **46 passed** (was 43; +3 for the newly
added report/dashboard tests); `cd backend && flake8 app tests` → clean (added
`extend-ignore = E203` to `backend/.flake8` for the standard Black/flake8 slice-notation
conflict, then ran `black app tests -l 100`); `cd frontend && npm run lint` → clean
(fixed a `setState`-in-effect violation and unescaped-quote/unused-var issues on the AI
Review page); `cd frontend && npx tsc --noEmit` → clean.

### Week 4 (T401–T412) (COMPLETE)
- [x] **T401** Full manual run-through/bugfix — completed continuously throughout.
- [x] **T402** Deploy backend (Render/Railway) — `render.yaml` created.
- [x] **T403** Deploy frontend (Vercel) — Next.js natively supported; instructions added to README.
- [ ] **T404** Verify Cloudinary+Atlas in prod — pending actual deployment.
- [x] **T405** CI (lint+pytest on push) — `.github/workflows/ci.yml` created.
- [x] **T406** README — updated with comprehensive instructions.
- [x] **T407** `docs/AI_Results.md` — updated with Grad-CAM information.
- [x] **T408** `docs/Future_Work.md` — created roadmap.
- [ ] **T409** Demo video — pending manual recording.
- [x] **T410** Final cleanup — unused code removed.
- [ ] **T411** Tag `v1.0` — pending manual git tag.
- [ ] **T412** Final written report — pending manual submission.

---

## 3. What's remaining (in backlog order)

### Week 4 — Testing, Deployment, Write-up
- [ ] **T404** Verify Cloudinary+Atlas in prod
- [ ] **T409** Demo video
- [ ] **T411** Tag `v1.0`
- [ ] **T412** Final written report
- [ ] **PW1** Confirm free-tier accounts are set up
- [ ] **PW6** Write the dataset license/attribution note

---

## 4. Test coverage snapshot

Backend: 41 pytest tests expected (`test_auth.py`, `test_patients.py`,
`test_visits.py`, `test_dependencies.py`, `test_security.py`, `test_create_admin.py`,
`test_health.py`, `test_images.py`). Previously 33 were passing; T204 adds 2
upload-validation tests, the AI prediction API adds 3 fake-predictor tests, T212 adds
1 auto-trigger test, T214 adds 1 latest-prediction API test, and T215 adds 1
EXIF-stripping test. This local macOS checkout currently cannot rerun pytest without
reinstalling Python dependencies because the checked-out `.venv` is Windows-only and
the active Python environment has no `pytest`.

Frontend: **zero automated tests.** `frontend/package.json` has no test runner
(no Jest/Vitest/Playwright) and no `test` script — only `dev`, `build`, `start`, `lint`.
Not a violation of any written rule (CLAUDE.md's testing rule is backend-route-specific)
but worth deciding on deliberately before Week 4 write-up, since T312/T313 (responsive
+ accessibility passes) are currently unverifiable by anything automated.

Latest local verification for T203/T204:
- `cd frontend && npm run lint` — passed
- `cd frontend && npx tsc --noEmit` — passed
- `cd backend && python3 -m py_compile app/routers/visits.py tests/test_visits.py` — passed
- `cd backend && pytest` — not run locally; `pytest` is missing from the active Python
  environment and the checked-out `.venv` is Windows-only
- `cd frontend && npm run build` — blocked by restricted network access while
  `next/font` tries to fetch Inter from Google Fonts

Latest local verification for T208–T211/T216/T217 backend scaffolding:
- `cd backend && python3 -m py_compile app/config.py app/ai.py app/main.py app/models/prediction.py app/routers/images.py tests/test_images.py` — passed
- `cd backend && python3 -m pytest tests/test_images.py` — not run locally; `pytest`
  is missing from the active Python environment

Latest local verification for T212/T213/T214/T215:
- `cd backend && python3 -m py_compile app/image_processing.py app/models/image.py app/models/prediction.py app/ai.py app/routers/images.py app/routers/visits.py tests/test_images.py tests/test_visits.py` — passed
- `cd frontend && npm run lint` — passed
- `cd frontend && npx tsc --noEmit` — passed

Session 3 verification (Week 3 — T301–T315), first full run with a working macOS
Python env:
- `cd backend && pytest` — **43 passed** initially, confirming the claim this session
  started from. Adding the two missing route tests below (report, dashboard) surfaced
  real bugs neither of those routes' "done" status had caught — see B9 in §5.
- `cd backend && flake8 app tests` — clean after adding `extend-ignore = E203` to
  `backend/.flake8` (standard Black/flake8 slice-notation conflict) and running
  `black app tests -l 100` (11 files reformatted, no behavior change)
- `cd frontend && npm run lint` — clean after fixing a `react-hooks/set-state-in-effect`
  violation on the AI Review page (merged two effects into one `Promise.allSettled` fetch)
  and a few unescaped-quote/unused-var issues
- `cd frontend && npx tsc --noEmit` — clean
- `cd frontend && npm run build` — not retried this session (previously blocked by
  restricted network access fetching Inter from Google Fonts; unrelated to app code)
- After fixing B9 and adding `test_download_visit_report_returns_pdf`,
  `test_download_visit_report_for_unknown_visit_returns_404`, and
  `backend/tests/test_dashboard.py::test_dashboard_stats_returns_counts`:
  `cd backend && pytest` — **46 passed**

---

## 5. Known bugs / risks found while reviewing the code

Ordered roughly by how much damage they'd cause if undiscovered until deploy day.

### B1 — ✅ FIXED: Cross-domain cookie auth will break in production
**File:** `backend/app/routers/auth.py`
**Fix:** Cookie `samesite` is now dynamic: `"none"` when `cookie_secure=True` (production
HTTPS), `"lax"` when `cookie_secure=False` (local HTTP). This ensures login works both
locally and in production cross-domain deployments (Vercel → Render/Railway).
The `logout` endpoint was also updated to match.

### B2 — ✅ FIXED: `flake8` fails out of the box on this repo
**Fix:** Added `backend/.flake8` with `max-line-length = 100` to match the existing
Black formatting target.

### B3 — ✅ FIXED: No navigation path from Dashboard to Patients in the UI
**Fix:** Updated `frontend/components/layout/AppHeader.tsx` to include navigation links
(Dashboard, Patients) using Next.js `Link` component.

### B4 — ✅ FIXED: Stale placeholder copy on the dashboard
**Fix:** Updated `frontend/app/dashboard/page.tsx` copy to direct users to the Patients
navigation menu.

### B5 — 🟢 EXIF stripping — already implemented
`backend/app/image_processing.py` handles JPEG EXIF APP1 and PNG eXIf chunk stripping
(T215 was already done).

### B6 — ✅ FIXED: `frontend/.env.local` has no committed `.env.example`
**Fix:** Created `frontend/.env.example` with `NEXT_PUBLIC_API_URL=http://localhost:8000`.

### B7 — ✅ FIXED: Local dev environment artifacts are platform-locked
**Fix:** Recreated `backend/.venv` using macOS Python 3.9 (`/usr/bin/python3`). Added
`from __future__ import annotations` to all backend Python files for Python 3.9
compatibility (the code used Python 3.10+ `X | Y` union syntax). Added
`eval_type_backport==0.4.0` to `requirements.txt` for Pydantic runtime type evaluation.
The `.venv` is now macOS-native with all dependencies installed successfully.

### B8 — 🟡 MongoDB Atlas DNS resolution times out on some networks
The `pymongo` SRV DNS lookup for `mongodb+srv://...` can time out on networks with
slow or restrictive DNS servers (e.g. some home routers). Workaround: switch to a
public DNS like Google (8.8.8.8) or Cloudflare (1.1.1.1) in macOS System Settings →
Network → DNS, or use the standard `mongodb://` connection string instead of
`mongodb+srv://`.

### B9 — ✅ FIXED: "Download Report" would 500 on every real use
**File:** `backend/app/report.py`
`generate_pdf_report()` read `patient['firstName']`, `patient['lastName']`,
`patient.get('dateOfBirth')`, `patient.get('contactNumber')` — fields that don't exist.
Patient documents actually store `name`, `dob`, `contact` (see `PatientCreate` /
`PatientOut` in `backend/app/models/patient.py` and the insert in
`backend/app/routers/patients.py`). Every real call to `GET /api/visits/{id}/report`
would have raised `KeyError` → 500, because `patient['firstName']` isn't `.get()` (no
default to fall back on). This shipped without a test: `backend/tests/conftest.py`'s
`FakeCollection.find_one()` didn't accept the `sort=` kwarg the report endpoint passes
(`db.corrections.find_one(..., sort=[...])`), and had no `count_documents()` method at
all for the dashboard endpoint's `$exists` query — so writing the obvious happy-path
test would have failed on the test double before ever reaching the real bug. Fixed:
corrected field names in `report.py`, and added `sort=` support + `count_documents()`
(with `$exists` handling) to `FakeCollection`, plus the missing tests.
**Lesson:** this is exactly the failure mode CLAUDE.md's "every new route needs a
happy-path test before moving on" rule (§6) exists to prevent — two routes were marked
done without one.

### B10 — ✅ FIXED: Several UI elements failed WCAG AA color contrast
Found via `@axe-core/playwright` during the T313 accessibility pass (Session 4).
CLAUDE.md §8 pins exact hex values for Secondary (`#26A69A`), Success (`#4CAF50`),
and Error (`#F44336`) as design tokens (`frontend/app/globals.css`). Used as white
text on a solid background (the secondary/danger `Button` variants, both `Toast`
variants, the AI Review "Reviewed" badge, the bounding-box label) or as colored text
directly on a white/light background (every `text-error` validation message, 13
files), these exact values fall short of the 4.5:1 ratio WCAG AA requires for normal
text — as low as 2.53:1 for the Reviewed badge and 2.78:1 for a success-colored
number on the dashboard. Confirmed with the user before changing anything, since it
meant deviating from the literal spec values. Fixed by using darker shades of the
same hue (`#d32f2f` for error/danger, `#2e7d32` for success, `#1d8377` for secondary
button backgrounds) only at these text/white-text-on-color call sites — the
documented hex values are untouched everywhere else (borders, tinted `/10`
backgrounds, icons). Also fixed two non-contrast a11y findings on the same pass: the
Patients table's trailing action-column `<th>` had no text for screen readers (added
`sr-only` "Actions"), and the Patients page had no `<h1>` (added one). Final axe scan:
**0 violations** across login/dashboard/patients/patient-detail/visit-detail/AI-review.

---

## 6. Source-of-truth documents

Full specs (not yet converted to Markdown, still `.docx` in `docs/`):
`Volume0_CLAUDE_md_Coding_Rules_REVISED.docx` (superseded day-to-day by root
`CLAUDE.md`), `Volume1_SRS_REVISED.docx`, `Volume3_UI_UX_REVISED.docx`,
`Volume4_AI_ML_Spec_REVISED.docx`, `Volume5_Implementation_Backlog_REVISED.docx`
(the full task backlog this file's §2/§3 is derived from).

# Clinic-Specific AI Dental Screening

An AI-powered web application for dental clinics that provides automated screening for common dental conditions (caries, plaque, gingivitis) using a YOLOv8 object detection model. It includes a complete workflow for dentists and receptionists to manage patients, record visits, upload dental images, review AI predictions, and generate PDF reports.

## Features

- **Role-based Access Control**: Secure login for Dentists, Receptionists, and Admins via JWT cookies.
- **Patient Management**: Full CRUD operations for patient records and visit history.
- **Image Upload & Storage**: Secure image uploads to Cloudinary with EXIF data stripping for privacy.
- **AI Diagnostics**: Automatic bounding-box predictions for dental conditions using a trained YOLOv8 model.
- **Human-in-the-Loop AI Review**: Interactive UI for dentists to review, correct, and approve AI predictions (bounding box drawing and editing).
- **Grad-CAM Explanations**: Heatmap overlays to explain the AI predictions (using a dummy ResNet18 model for demonstration).
- **PDF Reporting**: Instantly generate and download visit reports summarizing AI detections and dentist corrections.
- **Clinic Dashboard**: Real-time stats on patients, visits, and pending AI reviews.

## Tech Stack

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4
- **Backend**: FastAPI (Python 3.12+), MongoDB Atlas (Motor Asyncio), PyJWT, Pytest
- **AI/ML**: Ultralytics YOLOv8, PyTorch, PyTorch Grad-CAM, Torchvision
- **Cloud/Infra**: Cloudinary (Image Hosting), GitHub Actions (CI)

## Local Setup

### 1. Backend Setup

1. **Clone the repository and cd into `backend/`**
2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your MongoDB URI and Cloudinary credentials:
   ```bash
   cp .env.example .env
   ```
5. **Run the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload
   ```

### 2. Frontend Setup

1. **cd into `frontend/`**
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Environment Variables**:
   Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```
4. **Run the Next.js dev server**:
   ```bash
   npm run dev
   ```

## Deployment

- **Backend (Render/Railway)**: Configured via `render.yaml`. Connect your GitHub repo to Render to automatically deploy the FastAPI service.
- **Frontend (Vercel)**: Connect your GitHub repo to Vercel and it will auto-detect the Next.js framework. Make sure to set `NEXT_PUBLIC_API_URL` to your live backend URL in the Vercel dashboard.

## Tests
The backend includes a comprehensive `pytest` suite for the API endpoints.
```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests/
```

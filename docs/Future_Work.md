# Future Work

This document outlines the proposed roadmap for scaling and improving the Clinic-Specific AI Dental Screening application beyond the current MVP phase.

## 1. Automated Retraining Pipeline (MLOps)
Currently, dentists can manually correct AI predictions via the AI Review UI. These corrections are securely saved to the database. The next step is to close the loop:
- **Data Pipeline**: Set up a CRON job to automatically export verified corrections from MongoDB.
- **Model Fine-Tuning**: Periodically retrain the YOLOv8 model using the new ground-truth labels provided by dentists.
- **Canary Deployments**: Automate the deployment of the new weights, serving a small percentage of requests to the new model first (shadow mode) before rolling it out clinic-wide.

## 2. Improved Grad-CAM Accuracy
The current implementation of Grad-CAM successfully demonstrates the engineering pipeline (cropping a detection, running a classifier, and generating a heatmap overlay). However, it uses a generic ImageNet `ResNet18` model.
- **Next Step**: Train a small, lightweight classifier (e.g., a custom MobileNet or ResNet) specifically on dental caries and plaque. Replace the generic model with this specialized one to produce medically relevant and interpretable heatmaps that highlight the exact features the AI used for its diagnosis.

## 3. Advanced Reporting
- **Analytics Dashboard**: Expand the existing dashboard to include trend analysis (e.g., disease frequency over time).
- **Patient History Comparisons**: Allow side-by-side comparisons of a patient's historical scans to track the progression or regression of caries/periodontitis automatically.

## 4. Multi-Tenant Clinic Architecture
The app is currently designed for a single clinic.
- Introduce a `Clinic` entity and link all Users, Patients, and Visits to a specific clinic.
- Enable a SaaS business model where multiple clinics can sign up and manage their data independently in isolated tenant views.

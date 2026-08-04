# AI Model Validation Results (YOLOv8n)

## Overall Metrics
- **Overall mAP50:** 0.837 (83.7%)
- **Inference Speed:** 2.6 ms per image

## Class-Specific Metrics
- **Cavity (mAP50):** 0.910 (91.0%)
- **Plaque (mAP50):** 0.763 (76.3%)

## Model Information
- **Base Model:** YOLOv8n
- **Size:** ~6.2 MB (`best.pt`)

*These metrics were obtained from the final Colab validation run during Week 2.*

## Explainability (Grad-CAM)
We have successfully implemented a Grad-CAM pipeline to provide explainability for the AI predictions. 
- For the MVP, we use a pretrained `ResNet18` on the ImageNet dataset to generate heatmaps for the YOLO bounding-box crops.
- While this proves the end-to-end technical pipeline (crop -> classify -> heatmap -> overlay), future work will involve lightly fine-tuning a classifier specifically on dental images for medically accurate visual explanations.

### Deployment note
Grad-CAM is **disabled on the hosted (Render free-tier) backend** via the
`ENABLE_GRAD_CAM` environment variable, and the heatmap endpoint returns HTTP 503
there. The feature is fully functional when run locally.

The reason is a hard memory limit rather than a defect: Grad-CAM requires gradient
computation (unlike plain YOLO inference, which runs without gradients) and keeps a
second model resident in memory for the lifetime of the process once a first heatmap
is requested. Measured on the free tier's 512 MB ceiling, the backend sits at ~310 MB
after startup and plateaus around ~460 MB under normal detection traffic, leaving
insufficient headroom; heatmap requests reproducibly triggered an out-of-memory kill
of the whole service. Disabling the feature in that one environment keeps the core
screening workflow reliable, and it can be re-enabled by setting `ENABLE_GRAD_CAM=true`
on any host with more memory available.

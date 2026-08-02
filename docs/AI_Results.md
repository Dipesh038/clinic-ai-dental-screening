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

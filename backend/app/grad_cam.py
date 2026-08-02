from __future__ import annotations

import io
from PIL import Image
import numpy as np

import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# Load a pretrained ResNet18 model (dummy classifier for demonstration)
# We use standard ImageNet weights.
_model = None
_target_layers = None
_cam = None


def get_cam():
    global _model, _target_layers, _cam
    if _cam is None:
        _model = resnet18(weights=ResNet18_Weights.DEFAULT)
        _model.eval()
        _target_layers = [_model.layer4[-1]]
        _cam = GradCAM(model=_model, target_layers=_target_layers)
    return _cam, _model


def generate_heatmap_for_crop(image: Image.Image) -> bytes:
    """
    Generates a Grad-CAM heatmap for a given image crop using a pretrained ResNet18.
    Returns the heatmap image as JPEG bytes.
    """
    cam, model = get_cam()

    # Preprocess image for ResNet
    preprocess = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    input_tensor = preprocess(image).unsqueeze(0)

    # For visualization, we need the image normalized between 0 and 1 as a numpy array
    rgb_img = np.float32(image.resize((224, 224))) / 255

    # We don't have a specific target class since it's a dummy ImageNet model.
    # We will just target the highest scoring category.
    targets = None

    # Generate CAM
    grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
    grayscale_cam = grayscale_cam[0, :]

    # Overlay heatmap on image
    visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)

    # Convert back to PIL and bytes
    heatmap_img = Image.fromarray(visualization)

    # Optionally, resize back to original crop size
    heatmap_img = heatmap_img.resize(image.size)

    buf = io.BytesIO()
    heatmap_img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

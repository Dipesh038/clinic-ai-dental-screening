from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from PIL import Image

from app.config import settings
from app.models.prediction import BoundingBox, DetectionOut

logger = logging.getLogger("app.ai")

_predictor: "YoloPredictor | None" = None


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _weights_path() -> Path:
    configured_path = Path(settings.ai_model_weights_path)
    if configured_path.is_absolute():
        return configured_path
    return _backend_root() / configured_path


def _class_names() -> dict[int, str]:
    names = [name.strip() for name in settings.ai_class_names.split(",") if name.strip()]
    return dict(enumerate(names))


class YoloPredictor:
    def __init__(self, weights_path: Path, class_names: dict[int, str]):
        from ultralytics import YOLO

        self._model = YOLO(str(weights_path))
        self._class_names = class_names

    def predict(
        self, image_url: str | None = None, image_bytes: bytes | None = None
    ) -> list[DetectionOut]:
        detections: list[DetectionOut] = []
        if image_bytes:
            image = Image.open(BytesIO(image_bytes))
        elif image_url:
            # Fetch into memory and hand Ultralytics a PIL Image rather than the raw
            # URL: passing a URL makes it call check_file(download_dir="."), which
            # downloads the image into the process's cwd and never cleans it up.
            with urlopen(image_url) as response:
                image = Image.open(BytesIO(response.read()))
        else:
            raise ValueError("Must provide either image_url or image_bytes")
        image.load()
        results = self._model.predict(source=image, verbose=False)

        for result in results:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            for box in boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
                detections.append(
                    DetectionOut(
                        class_id=class_id,
                        disease_name=self._class_names.get(class_id, f"class_{class_id}"),
                        confidence=confidence,
                        box=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                    )
                )

        return detections


def load_predictor() -> None:
    global _predictor

    weights_path = _weights_path()
    if not weights_path.exists():
        logger.warning("YOLO weights not found at %s; AI prediction is disabled", weights_path)
        _predictor = None
        return

    try:
        _predictor = YoloPredictor(weights_path, _class_names())
        logger.info("YOLO model loaded from %s", weights_path)
    except ImportError:
        logger.exception("ultralytics is not installed; AI prediction is disabled")
        _predictor = None
    except Exception:
        logger.exception("Failed to load YOLO model; AI prediction is disabled")
        _predictor = None


def get_predictor() -> YoloPredictor | None:
    return _predictor

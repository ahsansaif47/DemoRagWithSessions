import os
import re
import gc
import fitz
import torch
import imagehash
import numpy as np

from PIL import Image
from ultralytics import YOLO
import ultralytics


def crop_regions(image, detections, page_number):
    # TODO: Check if we need the page number in this function.
    crops = []
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            continue

        if crop.size < 14950:
            continue

        crops.append(
            {
                "label": det["label"],
                "bbox": det["bbox"],
                "image": crop,
                "page_number": page_number,
            }
        )
        print(f"Cropped {det['label']} from page {page_number} at bbox {det['bbox']}")
    return crops


def phash_image(np_img):
    pil = Image.fromarray(np_img)
    h = imagehash.phash(pil)
    del pil  # Free PIL image immediately
    return h


def is_duplicate(new_hash, existing_hashes, threshold=6):
    """Check if a hash is duplicate of any existing hash."""
    return any(abs(new_hash - old) <= threshold for old in existing_hashes)


class VisualDetector:
    def __init__(self, model_path: str, conf: float = 0.25):
        with torch.serialization.safe_globals([ultralytics.nn.tasks.DetectionModel]):
            self.model = YOLO(model_path)

            if torch.cuda.is_available():
                self.model.to("cuda")

            self.conf = conf

    def detect(self, image):
        results = self.model(image, conf=self.conf, verbose=False)[0]

        detections = list()
        for box in results.boxes:
            cls = int(box.cls[0])
            label = self.model.names.get(cls, "unknown")

            if label.lower() in {
                "figure", "image", "diagram", "picture",
                "photo", "vector", " chart", "graph"
            }:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({"label": label, "bbox": (x1, y1, x2, y2)})

        return detections

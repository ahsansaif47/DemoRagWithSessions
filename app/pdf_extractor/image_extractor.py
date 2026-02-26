import fitz
import numpy as np
import os
import cv2
import imagehash
from PIL import Image
from ultralytics import YOLO
import ultralytics
import torch
import gc

torch.serialization._default_to_weights_only = False

class VisualDetector:
    def __init__(self, model_path: str, conf=0.25):
        with torch.serialization.safe_globals([ultralytics.nn.tasks.DetectionModel]):
            self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, image):
        results = self.model(image, conf=self.conf, verbose=False)[0]

        detections = []
        for box in results.boxes:
            cls = int(box.cls[0])
            print(f"Detected class {cls} with confidence {box.conf[0]:.2f}")
            label = self.model.names.get(cls, "unknown")

            if label.lower() in {
                "figure",
                "image",
                "diagram",
                "picture",
                "photo",
                "vector",
                "chart",
                "graph",
            }:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({"label": label, "bbox": (x1, y1, x2, y2)})

        return detections

# Note: This thing can be done in text extractor function
def render_single_page(doc, page_index, total_pages, dpi=300):
    """Render a single page and return the image. Memory efficient."""
    print(f"Rendering page {page_index + 1}/{total_pages}...")
    page = doc[page_index]
    pix = page.get_pixmap(dpi=dpi, alpha=False)

    # Copy the data immediately so pix can be freed
    img = np.frombuffer(pix.samples, dtype=np.uint8).copy()
    img = img.reshape(pix.h, pix.w, pix.n)

    # Explicitly free the pixmap
    del pix

    return img


def iterate_pdf_pages(pdf_path, dpi=300):
    """Generator that yields pages one at a time to avoid loading all into memory."""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    for page_index in range(total_pages):
        img = render_single_page(doc, page_index, total_pages, dpi)
        yield page_index + 1, img
        # Image will be garbage collected after caller is done with it

    doc.close()


def crop_regions(image, detections, page_number):
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


# FIXME: Load the output_dir from config
def extract_visual_elements(
        pdf_path: str, model_path: str, output_dir=""
):
    os.makedirs(output_dir, exist_ok=True)

    # Load detector once
    detector = VisualDetector(model_path)
    print(f"Initialized visual detector with model '{model_path}'.")

    # Track hashes for deduplication (lightweight - just hashes, not images)
    seen_hashes = []
    total_crops = 0
    unique_count = 0

    # Process pages one at a time using generator
    for page_num, page_img in iterate_pdf_pages(pdf_path):
        detections = detector.detect(page_img)
        print(f"Detected {len(detections)} visual elements on page {page_num}.")

        crops = crop_regions(page_img, detections, page_num)
        total_crops += len(crops)

        for i, crop in enumerate(crops):
            # Compute hash for deduplication
            crop_hash = phash_image(crop["image"])

            if is_duplicate(crop_hash, seen_hashes):
                # Skip duplicate, free memory
                del crop["image"]
                continue

            # Save unique image
            seen_hashes.append(crop_hash)
            unique_count += 1

            filename = f"page_{page_num}_vis_{i}.png"
            path = os.path.join(output_dir, filename)
            cv2.imwrite(path, crop["image"])

            # Free the crop image after saving
            del crop["image"]

        # Explicitly free page image and trigger garbage collection periodically
        del page_img
        del crops
        if page_num % 50 == 0:
            gc.collect()

    print(f"Raw visual regions: {total_crops}")
    print(f"After deduplication: {unique_count}")

    # Final cleanup
    gc.collect()

    return unique_count
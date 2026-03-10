import datetime
import os
from pathlib import Path

from app.extractor.visual import crop_regions, phash_image, is_duplicate
from app.extractor.content import ExtractedContent, PageContent, ExtractedImage
from app.extractor.visual import VisualDetector
from app.extractor.text import clean_text
import numpy as np
import fitz
from app.integrations.storage import local_storage
import cv2
from app.integrations.storage.azure_blob_storage import AzureStorageService

# TODO: Wrap this in a function and return the path
# FIXME: Ensure nothing is a global variable
base_path = Path(__file__).resolve().parents[2]
m_path = base_path / "scripts" / "models"
weights = os.path.join(str(m_path), "yolov8s-doclaynet.pt")

images_path = base_path / "resources" / "images"


# images_path = str(images_path)


class PDFContentExtractor:
    def __init__(
            self,
            pdf_path: str,
            include_page_markers: bool = True,
            model_path: str = weights,
            dpi: int = 300,
            conf: float = 0.25,
    ):
        self.pdf_path = pdf_path
        self.include_page_markers = include_page_markers
        self.dpi = dpi
        self.visual_detector = VisualDetector(model_path, conf)

    def render_page(self, page):
        pix = page.get_pixmap(dpi=self.dpi, alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).copy()
        img = img.reshape(pix.h, pix.w, pix.n)
        del pix
        return img

    def extract(self, user_img_dir: str, azure_storage: AzureStorageService) -> ExtractedContent:
        global images_path
        content = ExtractedContent()
        doc = fitz.open(self.pdf_path)

        content.total_pages = doc.page_count

        seen_hashes = set()
        total_images = 0
        raw_text = ""

        for page_num, page in enumerate(doc, start=1):
            text = clean_text(page.get_text() or "")
            if self.include_page_markers:
                text = f"[PAGE: {page_num}]\n{text}"
            raw_text += text + "\n"

            page_content = PageContent(
                page_number=page_num,
                page_text=text,
            )

            page_image = self.render_page(page)
            detections = self.visual_detector.detect(page_image)
            crops = crop_regions(page_image, detections, page_num)

            images = []
            for i, crop in enumerate(crops):
                crop_hash = phash_image(crop['image'])
                if is_duplicate(crop_hash, seen_hashes):
                    continue

                seen_hashes.add(crop_hash)
                total_images += 1

                _, buffer = cv2.imencode(".jpg", crop['image'])
                image_name = f'page_{page_num}_vis_{i}.jpg'

                user_file_path = '/'.join(user_img_dir.split('/')[-2:])
                img_blob_name = user_file_path + '/' + image_name

                azure_storage.upload_bytes(buffer.tobytes(), img_blob_name, "image")

                # img_dir_split = user_img_dir.split("/")[:]

                # blob_name = f'{user_img_dir}/{image_name}'
                # azure_storage.upload_bytes(buffer.tobytes(), )

                # TODO: Stop uploading on local system.
                # Save the image file in this function.
                img_path = os.path.join(user_img_dir, image_name)
                local_storage.save_image(img_path, buffer.tobytes())

                img = ExtractedImage(
                    image_number=i,
                    image_name=image_name
                )

                images.append(img)

            page_content.images = images
            content.page_content.append(page_content)
        content.total_images = total_images
        content.raw_text = raw_text
        return content

import datetime
import os

from app.extractor.visual import crop_regions, phash_image, is_duplicate
from app.extractor.content import ExtractedContent, PageContent, ExtractedImage
from app.extractor.visual import VisualDetector
from app.extractor.text import clean_text
import numpy as np
import fitz
import cv2


class PDFContentExtractor:
    def __init__(
            self,
            pdf_path: str,
            include_page_markers: bool = True,
            model_path: str = "../../scripts/models/yolov8s-doclaynet.pt",
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

    def extract(self) -> ExtractedContent:
        content = ExtractedContent()
        doc = fitz.open(self.pdf_path)

        content.total_pages = doc.page_count

        seen_hashes = []
        total_images = 0
        raw_text = ""

        for page_num, page in enumerate(doc, start=1):
            text = clean_text(page.get_text() or "")
            if self.include_page_markers:
                text = f"[PAGE: {page_num}]\n{text}]"
                raw_text += text + "\n"

            page_content = PageContent(
                page_number=page_num,
                page_text=text,
            )

            page_image = self.render_page(page)
            detections = self.visual_detector.detect(page_image)
            crops = crop_regions(page_image, detections, page_num)

            for i, crop in enumerate(crops):
                crop_hash = phash_image(crop['image'])
                if is_duplicate(crop_hash, seen_hashes):
                    continue

                seen_hashes.append(crop_hash)
                total_images += 1

                _, buffer = cv2.imencode(".jpg", crop['image'])

                # TODO: Save this in your service layer
                # pdf_name = self.pdf_path.split("/")[-1].split(".")[0]
                # dir_path = f'../../resources/temp_images/{pdf_name}'
                # os.makedirs(dir_path, exist_ok=True)
                # file_name = os.path.join(dir_path, f"page_{pdf_name}_vis_{i}.jpg")
                #
                #
                # with open(file_name, "wb") as f:
                #     f.write(buffer.tobytes())
                # TODO: Code cleanup after saving file

                img = ExtractedImage(
                    image_number=i,
                    image_data=buffer.tobytes(),
                )

                page_content.images.append(img)
            content.page_content.append(page_content)
        content.total_images = total_images
        content.raw_text = raw_text
        return content



extractor = PDFContentExtractor("../../resources/archive/Book_12_Ops.pdf", include_page_markers=True, model_path="../../scripts/models/yolov8s-doclaynet.pt")
e_content = extractor.extract()
print(e_content)


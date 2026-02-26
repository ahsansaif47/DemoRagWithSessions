from dataclasses import dataclass, field
from typing import List


@dataclass
class ExtractedImage:
    image_number: int = 1
    image_data: bytes = b''
    image_name: str = ""

@dataclass
class PageContent:
    page_number: int = 0
    images: List[ExtractedImage] = field(default_factory=list)
    page_text: str = ""


@dataclass
class ExtractedContent:
    raw_text: str = ""
    page_content: List[PageContent] = field(default_factory=list)
    total_pages: int = 0
    total_images: int = 0
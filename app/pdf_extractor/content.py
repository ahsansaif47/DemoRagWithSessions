from dataclasses import dataclass, field
from typing import List


@dataclass
class ExtractedImage:
    image_number: int = 0
    image_data: bytes = b''
    page_number: int = 0

@dataclass
class PageContent:
    page_number: int = 0
    images: List[ExtractedImage] = field(default_factory=list)
    page_text: list = field(default_factory=list)


@dataclass
class ExtractedContent:
    raw_text: str = ""
    # page_text: list = field(default_factory=list)
    # images: List[ExtractedImage] = field(default_factory=list)
    page_content: List[PageContent] = field(default_factory=list)
    total_pages: int = 0
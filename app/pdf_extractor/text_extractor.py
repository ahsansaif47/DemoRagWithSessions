import re
import logging
import fitz

from app.pdf_extractor.content import ExtractedContent, PageContent

logger = logging.getLogger(__name__)


class TextExtractor:
    def __init__(self, book_title: str, pdf_path: str, include_page_markers: bool = True):
        self.book_title = book_title
        self.pdf_path = pdf_path
        self.include_page_markers = include_page_markers

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'-\s*\n\s*', '', text)
        return "".join(c for c in text if c.isprintable() or c in "\n\t")

    def extract_text(self) -> ExtractedContent:
        self.logger.info("Extracting text from PDF: {}".format(self.pdf_path))
        content = ExtractedContent()

        doc = fitz.open(self.pdf_path)
        content.total_pages = doc.page_count
        logger.info(f'Total Document Pages: {content.total_pages}')
        all_pages_text = list()

        if self.include_page_markers:
            logger.info('Page markers will appear in page text')
        for i, page in enumerate(doc, start=1):
            page_text = self.clean_text(page.get_text() or "")
            if self.include_page_markers:
                page_text = f"[PAGE: {i}]\n{page_text}"
            all_pages_text.append(page_text)


            page_content = PageContent(
                page_text=[page_text],
                page_number=i
            )

            content.page_content.append(page_content)

        content.raw_text = "\n".join(all_pages_text)

        return content

# # TODO: Remove the logger after testing
#
# # Testing text extraction
# book_title = "Book_01_Air Law"
# pdf_path = "../../resources/archive/Book_01_Air Law.pdf"
# text_ext = TextExtractor(book_title, pdf_path)
# text_ext.extract_text()

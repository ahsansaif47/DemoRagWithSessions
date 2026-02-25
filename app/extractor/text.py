import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'-\s*\n\s*', '', text)
    return "".join(c for c in text if c.isprintable() or c in "\n\t")

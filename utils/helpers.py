import os
import re


def get_extension(file_name: str) -> str:
    return os.path.splitext(file_name)[1].lower().replace('.', '')


def clean_text(text: str) -> str:
    if not text:
        return ''
    text = text.replace('\x00', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def truncate_preview(text: str, length: int = 300) -> str:
    text = clean_text(text)
    if len(text) <= length:
        return text
    return text[:length].rstrip() + '...'


def split_sentences(text: str) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    return [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if s.strip()]

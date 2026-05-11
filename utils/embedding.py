import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client() -> OpenAI:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError('OPENAI_API_KEY is not set.')
    return OpenAI(api_key=api_key)


def prepare_text_for_embedding(text: str, max_chars: int = 8000) -> str:
    text = (text or '').strip()
    return text[:max_chars]


def get_embedding(text: str) -> list[float]:
    client = get_openai_client()
    model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    prepared = prepare_text_for_embedding(text)
    response = client.embeddings.create(model=model, input=prepared)
    return response.data[0].embedding

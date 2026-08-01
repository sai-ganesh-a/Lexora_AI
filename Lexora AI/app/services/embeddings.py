from google import genai
from config import Config


def get_client():
    return genai.Client(api_key=Config.GEMINI_API_KEY)


def embed_text(text: str):
    client = get_client()
    model_name = getattr(Config, "EMBEDDING_MODEL", "text-embedding-004")
    response = client.models.embed_content(
        model=model_name,
        contents=text,
    )
    return response.embeddings[0].values


def embed_chunks(chunks):
    return [embed_text(chunk) for chunk in chunks]
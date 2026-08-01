import os
from flask import current_app
from app.models import db
from config import Config

from app.services.parser import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_chunks
from app.services.vector_store import store_chunks


def process_document(document):
    upload_folder = current_app.config.get("UPLOAD_FOLDER", Config.UPLOAD_FOLDER)
    file_path = os.path.join(upload_folder, document.stored_filename)

    try:
        text = extract_text(file_path)

        if not text.strip():
            document.status = "error"
            db.session.commit()
            return

        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)

        store_chunks(
            document,
            chunks,
            embeddings,
        )

        document.status = "ready"
        db.session.commit()
    except Exception as e:
        print(f"Error processing document {document.id}: {e}")
        document.status = "error"
        db.session.commit()
        raise e
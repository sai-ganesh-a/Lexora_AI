import chromadb
from config import Config

client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)

collection = client.get_or_create_collection(
    name="documents"
)


def store_chunks(document, chunks, embeddings):
    """
    Store document chunks in ChromaDB.
    """
    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"{document.id}_{i}")
        metadatas.append(
            {
                "project_id": str(document.project_id),
                "document_id": str(document.id),
                "filename": document.filename,
                "chunk_index": i,
            }
        )

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search(project_id, query_embedding, top_k=5):
    """
    Search only inside one project.
    """
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "project_id": str(project_id)
        },
    )


def delete_document(document_id):
    """
    Delete all chunks belonging to a document.
    """
    try:
        collection.delete(
            where={
                "document_id": str(document_id)
            }
        )
    except Exception as e:
        print(f"Error deleting vectors for document {document_id}: {e}")


def delete_project_vectors(project_id):
    """
    Delete all chunks belonging to a project.
    """
    try:
        collection.delete(
            where={
                "project_id": str(project_id)
            }
        )
    except Exception as e:
        print(f"Error deleting vectors for project {project_id}: {e}")
import os
from google import genai
from flask import current_app
from config import Config
from app.models import db
from app.models.chat import ChatMessage
from app.models.document import Document
from app.services.embeddings import embed_text
from app.services.vector_store import search
from app.services.parser import extract_text


def get_genai_client():
    return genai.Client(api_key=Config.GEMINI_API_KEY)


def ask_question(project_id, question):
    # Save user message to database
    user_msg = ChatMessage(
        project_id=project_id,
        sender="user",
        message=question
    )
    db.session.add(user_msg)
    db.session.commit()

    # Detect general overview / summary / full analysis queries
    lower_q = question.lower()
    overview_keywords = ["summary", "summarize", "overview", "analyze", "analysis", "entire", "whole", "full", "pdf", "document"]
    is_overview_query = any(k in lower_q for k in overview_keywords)
    top_k_count = 15 if is_overview_query else 8

    query_embedding = embed_text(question)

    results = search(
        project_id=project_id,
        query_embedding=query_embedding,
        top_k=top_k_count,
    )

    contexts = []
    if results and "documents" in results and results["documents"]:
        contexts = results["documents"][0]

    if not contexts:
        answer = "I couldn't find any documents or relevant context in this project. Please upload a document first."
        ai_msg = ChatMessage(
            project_id=project_id,
            sender="ai",
            message=answer
        )
        db.session.add(ai_msg)
        db.session.commit()
        return {
            "answer": answer,
            "sources": [],
        }

    context_str = "\n\n".join(contexts)

    # Fetch recent conversation history (last 6 messages) for multi-turn context
    recent_history = ChatMessage.query.filter_by(project_id=project_id)\
        .order_by(ChatMessage.created_at.desc()).limit(6).all()
    recent_history.reverse()

    history_str = ""
    if len(recent_history) > 1:
        history_str = "Recent Chat History:\n" + "\n".join(
            [f"{msg.sender.upper()}: {msg.message}" for msg in recent_history[:-1]]
        ) + "\n\n"

    prompt = f"""You are Lexora AI, a dedicated RAG (Retrieval-Augmented Generation) document assistant.

Instructions:
1. Document Scope: Answer questions using ONLY the information provided in the Document Context below.
2. Full Document / Summary Queries: If the user asks to analyze, summarize, evaluate, or explain the uploaded document or PDF content, synthesize all provided context chunks into a clear, structured summary.
3. Unrelated / Out-of-Context Questions: If the question is completely unrelated to the content, subject, or topics in the uploaded document (for example, general trivia, unrelated concepts like 'what is war?' when viewing a resume), reply strictly with:
"I couldn't find any information about that in your uploaded documents. Please ask a question related to your uploaded files."

{history_str}Document Context:
{context_str}

User Question:
{question}

Answer:"""

    client = get_genai_client()
    response = client.models.generate_content(
        model=Config.GEMINI_MODEL,
        contents=prompt,
    )

    answer = response.text.strip()

    # Save AI message to database
    ai_msg = ChatMessage(
        project_id=project_id,
        sender="ai",
        message=answer
    )
    db.session.add(ai_msg)
    db.session.commit()

    return {
        "answer": answer,
        "sources": contexts,
    }


def get_chat_history(project_id):
    messages = ChatMessage.query.filter_by(project_id=project_id)\
        .order_by(ChatMessage.created_at.asc()).all()
    return [msg.to_dict() for msg in messages]


def clear_chat_history(project_id):
    ChatMessage.query.filter_by(project_id=project_id).delete()
    db.session.commit()
    return True


def summarize_document(document_id):
    doc = Document.query.get_or_404(document_id)
    upload_folder = current_app.config.get("UPLOAD_FOLDER", Config.UPLOAD_FOLDER)
    file_path = os.path.join(upload_folder, doc.stored_filename)

    text = extract_text(file_path)
    if not text.strip():
        return "The document appears to be empty or could not be read."

    # Truncate text if excessively long for summary prompt
    truncated_text = text[:15000]

    prompt = f"""You are Lexora AI. Provide a concise, comprehensive summary of the following document content.
Highlight key points, main conclusions, skills, and important details.

Document Filename: {doc.filename}

Content:
{truncated_text}

Summary:"""

    client = get_genai_client()
    response = client.models.generate_content(
        model=Config.GEMINI_MODEL,
        contents=prompt,
    )

    return response.text.strip()
from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app.models import db
from app.models.project import Project
from app.models.document import Document

from app.services.file_service import save_uploaded_file, delete_physical_file
from app.services.document_processor import process_document
from app.services.vector_store import delete_document
from app.services.chat_service import summarize_document

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/upload/<int:project_id>", methods=["POST"])
@login_required
def upload(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()

    file = request.files.get("document")

    if not file or file.filename == "":
        flash("No file selected for upload.", "warning")
        return redirect(url_for("projects.workspace", project_id=project.id))

    try:
        metadata = save_uploaded_file(file)

        document = Document(
            project_id=project.id,
            filename=metadata["original_name"],
            stored_filename=metadata["stored_name"],
            file_type=metadata["file_type"],
            file_size=metadata["file_size"],
            status="processing",
        )

        db.session.add(document)
        db.session.commit()

        # Process text extraction & embeddings
        process_document(document)
        flash(f"Document '{document.filename}' uploaded and processed successfully!", "success")

    except Exception as e:
        print(f"Upload error: {e}")
        flash(f"Error uploading document: {str(e)}", "danger")

    return redirect(url_for("projects.workspace", project_id=project.id))


@documents_bp.route("/delete/<int:document_id>", methods=["POST"])
@login_required
def delete(document_id):
    document = Document.query.get_or_404(document_id)
    project = Project.query.filter_by(id=document.project_id, user_id=current_user.id).first_or_404()

    try:
        # Delete from disk
        delete_physical_file(document.stored_filename)

        # Delete vectors from ChromaDB
        delete_document(document.id)

        # Delete record from SQLite
        db.session.delete(document)
        db.session.commit()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"status": "success", "message": "Document deleted"})

        flash(f"Document '{document.filename}' deleted.", "info")
    except Exception as e:
        print(f"Error deleting document {document_id}: {e}")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"status": "error", "message": str(e)}), 500
        flash("Failed to delete document.", "danger")

    return redirect(url_for("projects.workspace", project_id=project.id))


@documents_bp.route("/summarize/<int:document_id>", methods=["POST"])
@login_required
def summarize(document_id):
    document = Document.query.get_or_404(document_id)
    project = Project.query.filter_by(id=document.project_id, user_id=current_user.id).first_or_404()

    try:
        summary = summarize_document(document.id)
        return jsonify({
            "status": "success",
            "filename": document.filename,
            "summary": summary
        })
    except Exception as e:
        print(f"Summarize error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
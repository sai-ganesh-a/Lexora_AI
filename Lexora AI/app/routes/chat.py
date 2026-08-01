from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.models.project import Project
from app.services.chat_service import ask_question, get_chat_history, clear_chat_history

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/ask", methods=["POST"])
@login_required
def ask():
    data = request.get_json() or {}

    question = data.get("question", "").strip()
    project_id = data.get("project_id")

    if not question:
        return jsonify({"answer": "Please enter a question.", "sources": []})

    if not project_id:
        return jsonify({"answer": "Project ID missing.", "sources": []})

    # Ensure current user owns project
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({"answer": "Unauthorized access to project.", "sources": []}), 403

    try:
        result = ask_question(project_id, question)
        return jsonify(result)
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"answer": f"An error occurred while processing your request: {str(e)}", "sources": []}), 500


@chat_bp.route("/history/<int:project_id>", methods=["GET"])
@login_required
def history(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    messages = get_chat_history(project.id)
    return jsonify({"status": "success", "messages": messages})


@chat_bp.route("/clear/<int:project_id>", methods=["POST"])
@login_required
def clear_history(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    clear_chat_history(project.id)
    return jsonify({"status": "success", "message": "Chat history cleared successfully."})
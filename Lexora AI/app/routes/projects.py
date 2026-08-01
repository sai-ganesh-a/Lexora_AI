from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app.models import db
from app.models.project import Project
from app.services.file_service import delete_physical_file
from app.services.vector_store import delete_project_vectors

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/")
@login_required
def dashboard():
    projects = Project.query.filter_by(user_id=current_user.id)\
        .order_by(Project.created_at.desc()).all()
    return render_template("dashboard.html", projects=projects)


@projects_bp.route("/projects/create", methods=["POST"])
@login_required
def create_project():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("Project name is required.", "danger")
        return redirect(url_for("projects.dashboard"))

    project = Project(
        user_id=current_user.id,
        name=name,
        description=description
    )

    db.session.add(project)
    db.session.commit()

    flash(f"Project '{name}' created!", "success")
    return redirect(url_for("projects.workspace", project_id=project.id))


@projects_bp.route("/project/<int:project_id>")
@login_required
def workspace(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    documents = project.documents
    return render_template(
        "workspace.html",
        project=project,
        documents=documents
    )


@projects_bp.route("/projects/delete/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()

    # Clean up physical document files
    for doc in project.documents:
        delete_physical_file(doc.stored_filename)

    # Clean up ChromaDB vectors for this project
    delete_project_vectors(project.id)

    # Delete project from DB (cascades to documents and chat_messages)
    db.session.delete(project)
    db.session.commit()

    flash(f"Project '{project.name}' deleted successfully.", "info")
    return redirect(url_for("projects.dashboard"))
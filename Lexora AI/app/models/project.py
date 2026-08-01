from datetime import datetime
from . import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True  # nullable for backwards compatibility
    )
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="projects")

    documents = db.relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    chat_messages = db.relationship(
        "ChatMessage",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project {self.name}>"
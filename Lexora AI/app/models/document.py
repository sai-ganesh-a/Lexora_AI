from datetime import datetime
from . import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    filename = db.Column(db.String(255), nullable=False)

    stored_filename = db.Column(db.String(255), nullable=False)

    file_type = db.Column(db.String(10), nullable=False)

    file_size = db.Column(db.Integer)

    status = db.Column(
        db.String(20),
        default="uploaded"
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    project = db.relationship(
        "Project",
        back_populates="documents"
    )

    def __repr__(self):
        return f"<Document {self.filename}>"
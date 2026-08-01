from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .project import Project
from .document import Document
from .chat import ChatMessage
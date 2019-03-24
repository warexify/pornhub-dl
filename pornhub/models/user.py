"""The sqlite model for a user."""
from sqlalchemy import (
    Column,
    DateTime,
    func,
    String,
)
from sqlalchemy.orm import relationship

from pornhub.db import base


class User(base):
    """The model for a user."""

    __tablename__ = 'user'

    FULL_USER = 'user'
    SINGLE_VIDEO = 'video'
    CHANNEL = 'channel'

    key = Column(String, primary_key=True)
    name = Column(String, unique=True)
    user_type = Column(String)

    last_scan = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    clips = relationship('Clip')

    def __init__(self, key, name, user_type):
        """Create a new user."""
        self.key = key
        self.name = name
        self.user_type = user_type

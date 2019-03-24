"""The sqlite model for a Movie."""
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from pornhub.db import base


class Clip(base):
    """The sqlite model for a Movie."""

    __tablename__ = 'movie'

    viewkey = Column(String, primary_key=True)
    user_key = Column(String, ForeignKey('user.key'), index=True)
    name = Column(String)
    size = Column(Integer)
    completed = Column(Boolean, nullable=False, default=False)

    user = relationship("User")

    def __init__(self, viewkey, name, user, size):
        """Create a new Movie."""
        self.viewkey = viewkey
        self.name = name
        self.user = user
        self.size = size

"""The sqlite model for a Movie."""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    Boolean,
    DateTime,
    String,
)

from pornhub.db import base


class Clip(base):
    """The sqlite model for a Movie."""

    __tablename__ = 'movie'

    viewkey = Column(String, primary_key=True)
    user_key = Column(String, ForeignKey('user.key'), index=True)
    title = Column(String)
    completed = Column(Boolean, nullable=False, default=False)
    downloaded = Column(DateTime)

    user = relationship("User")

    def __init__(self, viewkey, user=None):
        """Create a new Movie."""
        self.viewkey = viewkey
        self.user = user

    def get_or_create(session, viewkey, user=None):
        """Get an existing clip or create a new one."""
        clip = session.query(Clip).get(viewkey)

        if clip is None:
            clip = Clip(viewkey, user)
            session.add(clip)

        return clip

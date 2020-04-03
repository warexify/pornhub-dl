"""The db model for a Movie."""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import (
    Boolean,
    DateTime,
    String,
)

from pornhub.db import base


class Clip(base):
    """The sqlite model for a Clip."""

    __tablename__ = "movie"

    viewkey = Column(String, primary_key=True)
    user_key = Column(
        String,
        ForeignKey("user.key", ondelete="cascade", onupdate="cascade", name="user"),
        index=True,
    )
    title = Column(String)
    extension = Column(String)
    location = Column(String)
    completed = Column(Boolean, nullable=False, default=False)
    downloaded = Column(DateTime)
    tags = Column(JSONB)
    categories = Column(JSONB)

    user = relationship("User")

    def __init__(self, viewkey, user=None):
        """Create a new Clip."""
        self.viewkey = viewkey
        self.user = user

    def get_or_create(session, viewkey, user=None):
        """Get an existing clip or create a new one."""
        clip = session.query(Clip).get(viewkey)

        if clip is None:
            clip = Clip(viewkey, user)
            session.add(clip)

        return clip

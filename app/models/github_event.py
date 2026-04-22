from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime, timezone
from app.models import Base


class GithubEvent(Base):
    __tablename__ = "github_events"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    delivery_id = Column(String(200), unique=True, nullable=False, index=True)
    event_type = Column(String(20), nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

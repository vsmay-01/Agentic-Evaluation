"""
Database models and connection management using SQLAlchemy.
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
from ..core.config import settings

Base = declarative_base()


class Evaluation(Base):
    """Evaluation result model."""
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, index=True)
    model_name = Column(String, index=True)
    final_score = Column(Float)
    dimension_scores = Column(JSON)  # Store as JSON
    individual_scores = Column(JSON)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    prompt = Column(Text, nullable=True)
    agent_response = Column(Text, nullable=True)  # Store agent response
    reference = Column(Text, nullable=True)


class BatchEvaluation(Base):
    """Batch evaluation result model."""
    __tablename__ = "batch_evaluations"

    batch_id = Column(String, primary_key=True, index=True)
    model_name = Column(String, index=True)
    total_evaluated = Column(Integer)
    average_score = Column(Float)
    dimension_averages = Column(JSON)
    score_distribution = Column(JSON)
    results = Column(JSON)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# Create database engine
def get_database_url():
    """Get database URL from settings or default to SQLite."""
    if settings.database_url.startswith("sqlite"):
        # Ensure directory exists for SQLite
        db_path = Path(__file__).resolve().parents[2] / ".." / ".." / "data" / "evaluations.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"
    return settings.database_url


engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database on import
init_db()

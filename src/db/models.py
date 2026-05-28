from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship

from src.utils.config import DATABASE_URL

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String, unique=True, nullable=False)
    specialty = Column(String, default="")
    target_language = Column(String, default="")
    plan = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)

    proposals = relationship("Proposal", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    external_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    budget = Column(String, default="")
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, default=0.0)
    client_rating = Column(Float, default=0.0)
    applicants = Column(Integer, default=0)
    submitted_at = Column(Integer, nullable=True)
    translated_ru = Column(Text, nullable=True)
    translations = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<Job {self.id}: {self.title[:50]}>"


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job")
    user = relationship("User", back_populates="proposals")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String, default="spam")
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job")
    user = relationship("User")


def get_engine():
    return create_engine(DATABASE_URL, echo=False)


def get_session_factory():
    engine = get_engine()
    Base.metadata.create_all(engine)
    for migration in (
        "ALTER TABLE users ADD COLUMN specialty VARCHAR DEFAULT ''",
        "ALTER TABLE users ADD COLUMN target_language VARCHAR DEFAULT ''",
        "ALTER TABLE jobs ADD COLUMN translations TEXT DEFAULT '{}'",
    ):
        try:
            with engine.connect() as conn:
                conn.execute(text(migration))
                conn.commit()
        except Exception:
            pass
    return sessionmaker(bind=engine, expire_on_commit=False)

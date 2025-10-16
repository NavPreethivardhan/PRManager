"""
Database configuration and models
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import os

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://prcopilot:password@localhost:5432/prcopilot"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PullRequest(Base):
    """Pull Request metadata and analysis results"""
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # GitHub PR identifiers
    github_pr_id = Column(BigInteger, unique=True, index=True)
    repository_full_name = Column(String, index=True)  # owner/repo
    pr_number = Column(Integer, index=True)
    
    # PR metadata
    title = Column(String)
    description = Column(Text)
    author = Column(String, index=True)
    state = Column(String)  # open, closed, merged
    
    # Analysis results
    classification = Column(String)  # Ready to Merge, Needs Discussion, etc.
    confidence = Column(Float)  # 0.0 to 1.0
    priority_score = Column(Integer)  # 0 to 100
    reasoning = Column(Text)
    suggested_action = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    analyzed_at = Column(DateTime(timezone=True))


class Repository(Base):
    """Repository metadata and settings"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Repository identifiers
    full_name = Column(String, unique=True, index=True)  # owner/repo
    github_repo_id = Column(Integer, unique=True, index=True)
    
    # Repository metadata
    name = Column(String)
    owner = Column(String, index=True)
    private = Column(Boolean, default=False)
    language = Column(String)
    
    # Settings
    auto_analyze_enabled = Column(Boolean, default=True)
    webhook_installed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    """User/Owner information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # GitHub user identifiers
    github_user_id = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    
    # User metadata
    email = Column(String)
    name = Column(String)
    avatar_url = Column(String)
    
    # Settings
    api_key_encrypted = Column(String)  # User's OpenAI API key (encrypted)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

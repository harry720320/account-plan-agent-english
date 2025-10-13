"""
Data model definitions
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()

class Account(Base):
    """Customer account table"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, index=True, nullable=False)
    industry = Column(String(100))
    company_size = Column(String(50))
    website = Column(String(255))
    country = Column(String(100), nullable=False)  # Country information, required field
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Add cascade delete
    plans = relationship("AccountPlan", back_populates="account", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="account", cascade="all, delete-orphan")
    external_info = relationship("ExternalInfo", cascade="all, delete-orphan")

class AccountPlan(Base):
    """Customer plan table"""
    __tablename__ = "account_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)  # Markdown format plan content
    status = Column(String(50), default="draft")  # draft, completed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    change_log = Column(JSON)  # Change log
    
    # Relationships - Add cascade delete
    account = relationship("Account", back_populates="plans")
    interactions = relationship("Interaction", back_populates="plan", cascade="all, delete-orphan")

class Interaction(Base):
    """Interaction record table"""
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("account_plans.id"), nullable=True)
    interaction_type = Column(String(50), nullable=False)  # question, answer, external_info
    question = Column(Text)
    answer = Column(Text)
    structured_data = Column(JSON)  # Structured extracted data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Add cascade delete
    account = relationship("Account", back_populates="interactions")
    plan = relationship("AccountPlan", back_populates="interactions")

class QuestionTemplate(Base):
    """Question TemplatesTable"""
    __tablename__ = "question_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)  # Question category
    question_text = Column(Text, nullable=False)
    description = Column(Text)  # Question description
    is_core = Column(Boolean, default=True)  # Whether it is a core question
    follow_up_questions = Column(JSON)  # Derived questions
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExternalInfo(Base):
    """External InformationTable"""
    __tablename__ = "external_info"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    info_type = Column(String(50), nullable=False)  # company_profile, news, market_info
    content = Column(Text)
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Add cascade delete
    account = relationship("Account", back_populates="external_info")
    
    # Add uniqueness constraint: each account can only have one customer profile
    __table_args__ = (
        UniqueConstraint('account_id', 'info_type', name='unique_account_info_type'),
    )

class Country(Base):
    """CountryTable"""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    """User table"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships

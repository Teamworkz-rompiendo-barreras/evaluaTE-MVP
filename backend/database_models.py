# backend/database_models.py
from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True) # Null si es login con Google
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EmployabilityReport(Base):
    __tablename__ = "employability_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    employability_score = Column(Integer, default=0)
    level = Column(String(50))
    report_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
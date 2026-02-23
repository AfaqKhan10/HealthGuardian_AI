# app/models.py
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# =========================
# USER TABLE
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # user / admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient_cases = relationship(
        "PatientCase",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# =========================
# PATIENT CASE TABLE
# =========================
class PatientCase(Base):
    __tablename__ = "patient_cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    user_query = Column(Text, nullable=False)
    extracted_symptoms = Column(JSONB, nullable=True)  # ← JSONB for PostgreSQL

    risk_level = Column(String(50), nullable=True)  # LOW / MEDIUM / HIGH / CRITICAL
    escalation_flag = Column(Boolean, default=False)

    status = Column(String(50), default="pending")  # pending / processing / completed / escalated
    final_response = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="patient_cases")
    agent_executions = relationship(
        "AgentExecution",
        back_populates="patient_case",
        cascade="all, delete-orphan"
    )
    supervisor_logs = relationship(
        "SupervisorLog",
        back_populates="patient_case",
        cascade="all, delete-orphan"
    )
    system_metrics = relationship(
        "SystemMetrics",
        back_populates="patient_case",
        cascade="all, delete-orphan"
    )


# =========================
# AGENT EXECUTION TABLE
# =========================
class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    patient_case_id = Column(Integer, ForeignKey("patient_cases.id"), nullable=False, index=True)

    agent_name = Column(String(100), nullable=False)
    agent_response = Column(Text, nullable=True)  # nullable kyunke error case ho sakta hai
    confidence_score = Column(Float, nullable=True)

    retry_count = Column(Integer, default=0)
    supervisor_decision = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    patient_case = relationship("PatientCase", back_populates="agent_executions")


# =========================
# SUPERVISOR LOG TABLE
# =========================
class SupervisorLog(Base):
    __tablename__ = "supervisor_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_case_id = Column(Integer, ForeignKey("patient_cases.id"), nullable=False, index=True)

    decision_type = Column(String(100), nullable=False)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    patient_case = relationship("PatientCase", back_populates="supervisor_logs")


# =========================
# SYSTEM METRICS TABLE
# =========================
class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    patient_case_id = Column(Integer, ForeignKey("patient_cases.id"), nullable=False, index=True)

    total_processing_time = Column(Float, nullable=True)  # in seconds
    total_agent_calls = Column(Integer, default=0)
    emergency_triggered = Column(Boolean, default=False)

    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    patient_case = relationship("PatientCase", back_populates="system_metrics")
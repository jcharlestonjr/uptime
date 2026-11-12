"""SQLAlchemy ORM models for production."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, Boolean, DateTime, Text,
                        ForeignKey, JSON, Enum as SQLEnum)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    monitors = relationship("MonitorModel", back_populates="owner")


class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    plan = Column(String(50), default="free")  # free | starter | team | business
    status = Column(String(50), default="active")
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MonitorModel(Base):
    __tablename__ = "monitors"
    id = Column(String(32), primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    interval_min = Column(Integer, default=5)
    timeout_s = Column(Float, default=10.0)
    expected_status = Column(Integer, default=200)
    regions = Column(JSON, default=list)
    active = Column(Boolean, default=True)
    alert_channels = Column(JSON, default=list)
    cooldown_min = Column(Integer, default=5)
    consecutive_failures_threshold = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="monitors")
    checks = relationship("CheckModel", back_populates="monitor", cascade="all, delete-orphan")
    incidents = relationship("IncidentModel", back_populates="monitor", cascade="all, delete-orphan")


class CheckModel(Base):
    __tablename__ = "checks"
    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(String(32), ForeignKey("monitors.id"), index=True, nullable=False)
    region = Column(String(50), nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    status = Column(String(20), nullable=False)  # up | down | degraded
    response_time_ms = Column(Float, default=0.0)
    status_code = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    monitor = relationship("MonitorModel", back_populates="checks")


class IncidentModel(Base):
    __tablename__ = "incidents"
    id = Column(String(32), primary_key=True, index=True)
    monitor_id = Column(String(32), ForeignKey("monitors.id"), index=True, nullable=False)
    started_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    cause = Column(Text, nullable=True)
    notified = Column(Boolean, default=False)
    post_mortem = Column(Text, nullable=True)
    monitor = relationship("MonitorModel", back_populates="incidents")


class StatusPageModel(Base):
    __tablename__ = "status_pages"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    monitor_id = Column(String(32), ForeignKey("monitors.id"), nullable=False)
    title = Column(String(255), nullable=True)
    custom_domain = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LeadModel(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    name = Column(String(255), nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
from sqlalchemy import (create_engine, Column, String, Float, DateTime,
                        Boolean, Text, Integer, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from src.config import DB_URL
import uuid

engine       = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base         = declarative_base()


class Product(Base):
    __tablename__ = "products"
    id           = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name         = Column(String(255), nullable=False)
    normalized_name = Column(String(255))       # NLP-normalized name for matching
    category     = Column(String(100))
    our_price    = Column(Float)                # Our store's price
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    prices       = relationship("PriceRecord", back_populates="product", cascade="all, delete")
    alerts       = relationship("PriceAlert",  back_populates="product", cascade="all, delete")


class Competitor(Base):
    __tablename__ = "competitors"
    id           = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name         = Column(String(255), nullable=False)
    base_url     = Column(String(500), nullable=False)
    scraper_type = Column(String(50), default="beautifulsoup")   # bs4 | scrapy | api
    is_active    = Column(Boolean, default=True)
    prices       = relationship("PriceRecord", back_populates="competitor")


class PriceRecord(Base):
    __tablename__ = "price_records"
    id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id    = Column(String(36), ForeignKey("products.id"), nullable=False)
    competitor_id = Column(String(36), ForeignKey("competitors.id"), nullable=False)
    price         = Column(Float, nullable=False)
    url           = Column(String(500))
    scraped_at    = Column(DateTime, default=datetime.utcnow)
    product       = relationship("Product",    back_populates="prices")
    competitor    = relationship("Competitor", back_populates="prices")


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id    = Column(String(36), ForeignKey("products.id"), nullable=False)
    alert_type    = Column(String(50))    # drop | spike | undercut | opportunity
    message       = Column(Text)
    old_price     = Column(Float)
    new_price     = Column(Float)
    change_pct    = Column(Float)
    competitor    = Column(String(255))
    is_read       = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    product       = relationship("Product", back_populates="alerts")


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

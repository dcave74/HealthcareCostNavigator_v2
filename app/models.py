from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Provider(Base):
    __tablename__ = "provider"

    provider_id = Column(Integer, primary_key=True)
    provider_name = Column(String(255), nullable=False)
    provider_city = Column(String(255), nullable=False)
    provider_state = Column(String(2), nullable=False)
    provider_zip_code = Column(String(20), nullable=False)
    provider_status = Column(String(20), default="UNKNOWN")

    pricing = relationship("ProviderPricing", back_populates="provider")
    rating = relationship("ProviderRating", back_populates="provider")

class ProviderPricing(Base):
    __tablename__ = "provider_pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"), nullable=False)
    ms_drg_definition = Column(String(1000), nullable=False)
    total_discharges = Column(Integer, default=0)
    averaged_covered_charges = Column(Integer, default=0)
    average_total_payments = Column(Integer, default=0)
    average_medicare_payments = Column(Integer, default=0)
    provider_pricing_year = Column(Integer)

    provider = relationship("Provider", back_populates="pricing")

class ProviderRating(Base):
    __tablename__ = "provider_rating"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"), nullable=False)
    provider_overall_rating = Column(Integer, default=0)
    provider_star_rating = Column(Integer, default=0)
    provider_rating_year = Column(Integer)

    provider = relationship("Provider", back_populates="rating")
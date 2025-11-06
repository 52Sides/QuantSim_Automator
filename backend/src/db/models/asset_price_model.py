from sqlalchemy import Column, Integer, String, Date, Float, DateTime, UniqueConstraint, Index, func
from sqlalchemy.orm import relationship
from db.database import Base

class AssetPriceModel(Base):
    __tablename__ = "asset_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(16), nullable=False, index=True)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    inserted_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_asset_ticker_date"),
        Index("ix_asset_ticker_date", "ticker", "date"),
    )

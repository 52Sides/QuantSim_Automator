from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Table
from sqlalchemy.orm import relationship

from db.database import Base

asset_simulation = Table(
    "asset_simulation",
    Base.metadata,
    Column("asset_id", ForeignKey("assets.id"), primary_key=True),
    Column("simulation_id", ForeignKey("simulations.id"), primary_key=True),
)


class AssetModel(Base):
    """Актив (ценная бумага и т.д.)"""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, unique=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    simulations = relationship("SimulationModel", secondary=asset_simulation, back_populates="assets")

    def __repr__(self) -> str:
        return f"<Asset(ticker={self.ticker})>"

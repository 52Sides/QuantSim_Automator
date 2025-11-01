from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class AssetModel(Base):
    """Актив (ценная бумага и т.д.)"""
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=DateTime(timezone=True), nullable=False
    )

    simulations: Mapped[list["SimulationModel"]] = relationship(
        back_populates="assets",
        secondary="simulation_assets",
    )

    def __repr__(self) -> str:
        return f"<Asset(ticker={self.ticker})>"

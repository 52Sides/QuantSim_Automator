from datetime import datetime, date

from sqlalchemy import Integer, String, Date, DateTime, ForeignKey, JSON, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

# --- Связующая таблица для Simulation ↔ Asset ---
simulation_assets = Table(
    "simulation_assets",
    Base.metadata,
    Column("simulation_id", ForeignKey("simulations.id", ondelete="CASCADE"), primary_key=True),
    Column("asset_id", ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
)


class SimulationModel(Base):
    """Результат симуляции портфеля"""
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    command: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=DateTime(timezone=True), nullable=False
    )

    metrics: Mapped["MetricModel"] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
        uselist=False,
    )

    assets: Mapped[list["AssetModel"]] = relationship(
        back_populates="simulations",
        secondary=simulation_assets,
    )

    def __repr__(self) -> str:
        return f"<Simulation(id={self.id}, command={self.command})>"

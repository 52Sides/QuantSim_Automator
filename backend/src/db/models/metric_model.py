from datetime import datetime

from sqlalchemy import Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class MetricModel(Base):
    """Финансовые метрики симуляции"""
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    cagr: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe: Mapped[float] = mapped_column(Float, nullable=False)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=DateTime(timezone=True), nullable=False
    )

    simulation: Mapped["SimulationModel"] = relationship(back_populates="metrics")

    def __repr__(self) -> str:
        return (
            f"<Metric(sim_id={self.simulation_id}, "
            f"CAGR={self.cagr:.2f}, Sharpe={self.sharpe:.2f})>"
        )

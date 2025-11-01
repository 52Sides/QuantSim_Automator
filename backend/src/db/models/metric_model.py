from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from db.database import Base


class MetricModel(Base):
    """Финансовые метрики симуляции"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    cagr = Column(Float)
    sharpe = Column(Float)
    max_drawdown = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    simulation = relationship("SimulationModel", back_populates="metrics")

    def __repr__(self) -> str:
        return (
            f"<Metric(sim_id={self.simulation_id}, "
            f"CAGR={self.cagr:.2f}, Sharpe={self.sharpe:.2f})>"
        )

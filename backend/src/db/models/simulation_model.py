from sqlalchemy import Column, Integer, String, Date, JSON, DateTime, func
from sqlalchemy.orm import relationship
from db.database import Base


class SimulationModel(Base):
    """Результат симуляции портфеля"""
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True)
    command = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    metrics = relationship(
        "MetricModel",
        back_populates="simulation",
        uselist=False,
        cascade="all, delete-orphan",
    )
    assets = relationship(
        "AssetModel",
        secondary="asset_simulation",
        back_populates="simulations",
    )

    def __repr__(self) -> str:
        return f"<Simulation(id={self.id}, command={self.command})>"

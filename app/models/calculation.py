import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Float, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(50), nullable=False, index=True)
    result = Column(Float, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="calculations")

    __mapper_args__ = {
        "polymorphic_identity": "calculation",
        "polymorphic_on": type,
    }

    def get_result(self) -> float:
        raise NotImplementedError("Subclasses must implement get_result()")

    @classmethod
    def create(cls, calc_type: str, a: float, b: float, user_id: uuid.UUID = None) -> "Calculation":
        """Factory method returning the specialized polymorphic Calculation subclass."""
        factory_map = {
            "add": AddCalculation,
            "sub": SubCalculation,
            "subtract": SubCalculation,
            "multiply": MultiplyCalculation,
            "divide": DivideCalculation,
        }
        normalized_type = calc_type.strip().lower()
        target_cls = factory_map.get(normalized_type)
        if not target_cls:
            raise ValueError(
                f"Unsupported calculation type '{calc_type}'. Must be one of: Add, Sub, Multiply, Divide."
            )
        instance = target_cls(a=a, b=b, user_id=user_id)
        instance.result = instance.get_result()
        return instance


class AddCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "add"}

    def get_result(self) -> float:
        return self.a + self.b


class SubCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "sub"}

    def get_result(self) -> float:
        return self.a - self.b


class MultiplyCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "multiply"}

    def get_result(self) -> float:
        return self.a * self.b


class DivideCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "divide"}

    def get_result(self) -> float:
        if self.b == 0:
            raise ValueError("Division by zero is not allowed.")
        return self.a / self.b

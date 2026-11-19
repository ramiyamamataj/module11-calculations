import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

class CalculationType(str, Enum):
    ADD = "Add"
    SUB = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"

class CalculationBase(BaseModel):
    a: float = Field(..., description="First numeric operand")
    b: float = Field(..., description="Second numeric operand")
    type: CalculationType = Field(..., description="Arithmetic operation type (Add, Sub, Multiply, Divide)")

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        if isinstance(value, str):
            mapping = {
                "add": "Add",
                "sub": "Sub",
                "subtract": "Sub",
                "multiply": "Multiply",
                "divide": "Divide",
            }
            normalized = mapping.get(value.strip().lower())
            if normalized:
                return normalized
        return value

class CalculationCreate(CalculationBase):
    user_id: Optional[uuid.UUID] = Field(default=None, description="Optional owner user UUID")

    @model_validator(mode="after")
    def validate_division_by_zero(self):
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed: operand 'b' cannot be 0 when type is Divide.")
        return self

class CalculationRead(BaseModel):
    id: uuid.UUID
    a: float
    b: float
    type: str
    result: float
    user_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

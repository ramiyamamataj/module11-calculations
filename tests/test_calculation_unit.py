import uuid
import pytest
from pydantic import ValidationError
from app.models.calculation import (
    Calculation,
    AddCalculation,
    SubCalculation,
    MultiplyCalculation,
    DivideCalculation,
)
from app.schemas.calculation import CalculationCreate, CalculationRead, CalculationType

@pytest.mark.parametrize("calc_type, expected_cls, a, b, expected_result", [
    ("Add", AddCalculation, 10.0, 5.0, 15.0),
    ("Sub", SubCalculation, 10.0, 4.0, 6.0),
    ("Multiply", MultiplyCalculation, 3.0, 7.0, 21.0),
    ("Divide", DivideCalculation, 20.0, 4.0, 5.0),
    ("add", AddCalculation, -2.5, 2.5, 0.0),
])
def test_calculation_factory_operations(calc_type, expected_cls, a, b, expected_result):
    calc = Calculation.create(calc_type=calc_type, a=a, b=b)
    assert isinstance(calc, expected_cls)
    assert isinstance(calc, Calculation)
    assert calc.result == pytest.approx(expected_result)

def test_calculation_factory_invalid_type():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(calc_type="Modulo", a=10.0, b=3.0)

def test_calculation_factory_divide_by_zero():
    with pytest.raises(ValueError, match="Division by zero"):
        Calculation.create(calc_type="Divide", a=10.0, b=0.0)

def test_base_calculation_not_implemented():
    base_calc = Calculation(a=1.0, b=2.0, type="calculation")
    with pytest.raises(NotImplementedError):
        base_calc.get_result()

def test_calculation_create_schema_valid():
    schema = CalculationCreate(a=12.5, b=2.5, type="Divide")
    assert schema.a == 12.5
    assert schema.b == 2.5
    assert schema.type == CalculationType.DIVIDE

def test_calculation_create_schema_zero_divisor():
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(a=10.0, b=0.0, type="Divide")
    assert "Division by zero is not allowed" in str(exc_info.value)

def test_calculation_create_schema_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=5.0, b=3.0, type="Exponent")

def test_calculation_create_schema_invalid_operands():
    with pytest.raises(ValidationError):
        CalculationCreate(a="not_a_number", b=3.0, type="Add")

def test_calculation_read_serialization():
    calc = Calculation.create(calc_type="Multiply", a=4.0, b=6.0)
    calc.id = uuid.uuid4()
    from datetime import datetime, timezone
    calc.created_at = datetime.now(timezone.utc)

    read_schema = CalculationRead.model_validate(calc)
    assert read_schema.id == calc.id
    assert read_schema.a == 4.0
    assert read_schema.b == 6.0
    assert read_schema.type == "multiply"
    assert read_schema.result == 24.0

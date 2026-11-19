import pytest
from sqlalchemy.exc import IntegrityError
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.calculation import (
    Calculation,
    AddCalculation,
    SubCalculation,
    MultiplyCalculation,
    DivideCalculation,
)
from app.schemas.user import UserCreate
from app.schemas.calculation import CalculationCreate, CalculationRead

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_insert_and_query_polymorphic_calculations(db_session):
    user = User.register(
        db_session,
        UserCreate(username="calc_tester", email="tester@example.com", password="password123")
    )

    payloads = [
        CalculationCreate(a=15, b=5, type="Add", user_id=user.id),
        CalculationCreate(a=15, b=5, type="Sub", user_id=user.id),
        CalculationCreate(a=15, b=5, type="Multiply", user_id=user.id),
        CalculationCreate(a=15, b=5, type="Divide", user_id=user.id),
    ]

    for item in payloads:
        calc_obj = Calculation.create(
            calc_type=item.type.value,
            a=item.a,
            b=item.b,
            user_id=item.user_id,
        )
        db_session.add(calc_obj)

    db_session.commit()

    records = db_session.query(Calculation).filter(Calculation.user_id == user.id).all()
    assert len(records) == 4

    results_by_type = {rec.type: rec for rec in records}
    assert isinstance(results_by_type["add"], AddCalculation)
    assert results_by_type["add"].result == 20.0

    assert isinstance(results_by_type["sub"], SubCalculation)
    assert results_by_type["sub"].result == 10.0

    assert isinstance(results_by_type["multiply"], MultiplyCalculation)
    assert results_by_type["multiply"].result == 75.0

    assert isinstance(results_by_type["divide"], DivideCalculation)
    assert results_by_type["divide"].result == 3.0

    serialized = CalculationRead.model_validate(results_by_type["add"])
    assert serialized.result == 20.0
    assert serialized.user_id == user.id

def test_cascade_delete_user_calculations(db_session):
    user = User.register(
        db_session,
        UserCreate(username="cascade_user", email="cascade@example.com", password="password123")
    )
    calc = Calculation.create(calc_type="Add", a=2, b=3, user_id=user.id)
    db_session.add(calc)
    db_session.commit()

    assert db_session.query(Calculation).count() == 1

    db_session.delete(user)
    db_session.commit()

    assert db_session.query(Calculation).count() == 0

def test_invalid_foreign_key_user_id(db_session):
    import uuid
    orphan_calc = Calculation.create(calc_type="Add", a=1, b=2, user_id=uuid.uuid4())
    db_session.add(orphan_calc)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

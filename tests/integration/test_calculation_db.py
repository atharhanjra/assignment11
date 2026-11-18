"""
Integration tests for the Calculation model with a real PostgreSQL database.

Locally, start the database first with: docker compose up -d db
"""

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.calculation_service import create_calculation
from app.database import Base, SessionLocal, engine
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationRead
from app.schemas.user import UserCreate
from app.user_service import create_user


@pytest.fixture
def db():
    """Give each test fresh, empty tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user(db):
    """A saved user that calculations can belong to."""
    return create_user(
        db, UserCreate(username="alice", email="alice@example.com", password="secret123")
    )


@pytest.mark.parametrize("calc_type, a, b, expected", [
    ("Add", 2, 3, 5),
    ("Sub", 10, 4, 6),
    ("Multiply", 4, 5, 20),
    ("Divide", 10, 4, 2.5),
])
def test_calculation_is_stored_correctly(db, user, calc_type, a, b, expected):
    """Each calculation type is saved with the correct data and result."""
    calc = create_calculation(db, CalculationCreate(a=a, b=b, type=calc_type, user_id=user.id))
    saved = db.query(Calculation).filter(Calculation.id == calc.id).first()
    assert saved.a == a
    assert saved.b == b
    assert saved.type == calc_type
    assert saved.result == expected
    assert saved.user_id == user.id
    assert saved.created_at is not None


def test_invalid_user_id_is_rejected(db):
    """The foreign key stops a calculation for a user that doesn't exist."""
    with pytest.raises(IntegrityError):
        create_calculation(db, CalculationCreate(a=1, b=2, type="Add", user_id=999))
    db.rollback()
    assert db.query(Calculation).count() == 0


@pytest.mark.parametrize("bad_data", [
    {"a": 1, "b": 2, "type": "Modulus"},
    {"a": 1, "b": 0, "type": "Divide"},
])
def test_invalid_calculation_never_reaches_database(db, user, bad_data):
    """An invalid type or zero divisor is rejected before anything is saved."""
    with pytest.raises(ValidationError):
        create_calculation(db, CalculationCreate(**bad_data, user_id=user.id))
    assert db.query(Calculation).count() == 0


def test_user_has_many_calculations(db, user):
    """One user can have many calculations (one-to-many)."""
    create_calculation(db, CalculationCreate(a=1, b=1, type="Add", user_id=user.id))
    create_calculation(db, CalculationCreate(a=2, b=2, type="Multiply", user_id=user.id))
    db.refresh(user)
    assert len(user.calculations) == 2
    assert user.calculations[0].user.username == "alice"


def test_deleting_user_deletes_calculations(db, user):
    """When a user is deleted, their calculations are deleted too."""
    create_calculation(db, CalculationCreate(a=1, b=1, type="Add", user_id=user.id))
    db.delete(user)
    db.commit()
    assert db.query(Calculation).count() == 0


def test_calculation_read_from_database(db, user):
    """A saved calculation converts to CalculationRead correctly."""
    calc = create_calculation(db, CalculationCreate(a=6, b=3, type="Divide", user_id=user.id))
    data = CalculationRead.model_validate(calc).model_dump()
    assert data["result"] == 2
    assert data["type"] == "Divide"
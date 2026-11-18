"""Unit tests for the Pydantic calculation schemas (app/schemas/calculation.py)."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.calculation import CalculationCreate, CalculationRead, CalculationType


@pytest.mark.parametrize("calc_type", ["Add", "Sub", "Multiply", "Divide"])
def test_valid_calculation_create(calc_type):
    """Each allowed type is accepted."""
    calc = CalculationCreate(a=10, b=2, type=calc_type, user_id=1)
    assert calc.type == CalculationType(calc_type)


@pytest.mark.parametrize("changes", [
    {"type": "Modulus"},     # not an allowed type
    {"type": "add"},         # wrong capitalization
    {"a": "abc"},            # not a number
    {"b": None},             # missing value
    {"type": "Divide", "b": 0},  # dividing by zero
])
def test_calculation_create_rejects_invalid_input(changes):
    """Invalid data raises a ValidationError before reaching the database."""
    data = {"a": 10, "b": 2, "type": "Add", "user_id": 1}
    data.update(changes)
    with pytest.raises(ValidationError):
        CalculationCreate(**data)


def test_zero_allowed_for_other_types():
    """b can be zero for operations other than division."""
    calc = CalculationCreate(a=10, b=0, type="Multiply", user_id=1)
    assert calc.b == 0


def test_calculation_read():
    """CalculationRead returns the expected fields."""
    calc = CalculationRead(
        id=1, a=2, b=3, type="Add", result=5, user_id=1, created_at=datetime.now()
    )
    data = calc.model_dump()
    assert data["result"] == 5
    assert set(data) == {"id", "a", "b", "type", "result", "user_id", "created_at"}
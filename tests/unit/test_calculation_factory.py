"""Unit tests for the CalculationFactory (app/calculation_factory.py)."""

import pytest

from app.calculation_factory import CalculationFactory
from app.operations import add, divide, multiply, subtract


@pytest.mark.parametrize("calc_type, expected_function", [
    ("Add", add),
    ("Sub", subtract),
    ("Multiply", multiply),
    ("Divide", divide),
])
def test_factory_picks_correct_operation(calc_type, expected_function):
    """The factory returns the right function for each type."""
    assert CalculationFactory.get_operation(calc_type) is expected_function


@pytest.mark.parametrize("calc_type, a, b, expected", [
    ("Add", 2, 3, 5),
    ("Sub", 10, 4, 6),
    ("Multiply", 4, 5, 20),
    ("Divide", 10, 4, 2.5),
])
def test_factory_computes_result(calc_type, a, b, expected):
    """The factory runs the operation and returns the correct result."""
    assert CalculationFactory.compute(calc_type, a, b) == expected


@pytest.mark.parametrize("bad_type", ["Modulus", "add", ""])
def test_factory_rejects_unknown_type(bad_type):
    """An unsupported type raises a ValueError."""
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.get_operation(bad_type)


def test_factory_divide_by_zero():
    """Dividing by zero through the factory still raises an error."""
    with pytest.raises(ValueError):
        CalculationFactory.compute("Divide", 5, 0)
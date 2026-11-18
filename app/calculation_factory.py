"""
Factory pattern for calculations.

Instead of a long if/elif chain, the factory looks up the right operation
function for each calculation type. Adding a new type only needs one new line.
"""

from app.operations import add, divide, multiply, subtract


class CalculationFactory:
    """Picks and runs the right operation for a calculation type."""

    _operations = {
        "Add": add,
        "Sub": subtract,
        "Multiply": multiply,
        "Divide": divide,
    }

    @classmethod
    def get_operation(cls, calc_type: str):
        """Return the operation function for a calculation type."""
        operation = cls._operations.get(calc_type)
        if operation is None:
            raise ValueError(f"Unsupported calculation type: {calc_type}")
        return operation

    @classmethod
    def compute(cls, calc_type: str, a: float, b: float) -> float:
        """Run the right operation and return the result."""
        return cls.get_operation(calc_type)(a, b)
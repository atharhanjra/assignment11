"""
Functions for saving calculations in the database.
"""

from sqlalchemy.orm import Session

from app.calculation_factory import CalculationFactory
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate


def create_calculation(db: Session, calc_in: CalculationCreate) -> Calculation:
    """
    Compute the result with the factory, then save the calculation.

    Raises sqlalchemy.exc.IntegrityError if user_id does not match a real user.
    """
    calc_type = calc_in.type.value
    result = CalculationFactory.compute(calc_type, calc_in.a, calc_in.b)
    calculation = Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=calc_type,
        result=result,
        user_id=calc_in.user_id,
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation
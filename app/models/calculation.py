"""
SQLAlchemy Calculation model.

Each Calculation is one row in the calculations table. The result is computed
once by the CalculationFactory when the row is created, then stored, so it
never has to be recalculated when history is read.
"""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class Calculation(Base):
    """A calculation made by a user."""

    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)   # Add, Sub, Multiply, or Divide
    result = Column(Float, nullable=False)
    # Foreign key: every calculation belongs to a real user.
    # If the user is deleted, their calculations are deleted too.
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Lets us use calculation.user to get the User object
    user = relationship("User", back_populates="calculations")
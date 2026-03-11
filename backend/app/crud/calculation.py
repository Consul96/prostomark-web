import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.calculation import Calculation
from app.models.enums import UserRole
from app.models.user import User


def _scoped(stmt, current_user: User):
    if current_user.role != UserRole.SUPERADMIN:
        stmt = stmt.where(Calculation.company_id == current_user.company_id)
    return stmt


def create_calculation(db: Session, calculation: Calculation) -> Calculation:
    db.add(calculation)
    db.flush()
    return calculation


def list_calculations(db: Session, current_user: User, *, limit: int = 50, offset: int = 0) -> list[Calculation]:
    stmt = _scoped(select(Calculation), current_user).order_by(Calculation.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


def get_calculation(db: Session, calculation_id: uuid.UUID, current_user: User) -> Calculation | None:
    stmt = _scoped(select(Calculation).where(Calculation.id == calculation_id), current_user)
    return db.execute(stmt).scalar_one_or_none()

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user


def list_users(db: Session, *, company_id: str | None = None, limit: int = 50, offset: int = 0) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc())
    if company_id:
        stmt = stmt.where(User.company_id == company_id)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())

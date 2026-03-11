from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company


def get_company_by_slug(db: Session, slug: str) -> Company | None:
    return db.execute(select(Company).where(Company.slug == slug)).scalar_one_or_none()


def create_company(db: Session, *, name: str, slug: str) -> Company:
    company = Company(name=name, slug=slug)
    db.add(company)
    db.flush()
    return company


def list_companies(db: Session, *, limit: int = 50, offset: int = 0) -> list[Company]:
    stmt = select(Company).order_by(Company.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())

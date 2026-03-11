import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.product import Product
from app.models.user import User


def _scoped(stmt, current_user: User):
    if current_user.role != UserRole.SUPERADMIN:
        stmt = stmt.where(Product.company_id == current_user.company_id)
    return stmt


def list_products(db: Session, current_user: User, *, limit: int = 50, offset: int = 0) -> list[Product]:
    stmt = _scoped(select(Product), current_user).order_by(Product.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


def create_product(db: Session, product: Product) -> Product:
    db.add(product)
    db.flush()
    return product


def get_product(db: Session, product_id: uuid.UUID, current_user: User) -> Product | None:
    stmt = _scoped(select(Product).where(Product.id == product_id), current_user)
    return db.execute(stmt).scalar_one_or_none()


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)


def update_product(db: Session, product: Product, data: dict) -> Product:
    for key, value in data.items():
        setattr(product, key, value)
    db.flush()
    return product

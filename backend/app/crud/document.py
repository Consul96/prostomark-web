import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.enums import UserRole
from app.models.user import User


def _scoped(stmt, current_user: User):
    if current_user.role != UserRole.SUPERADMIN:
        stmt = stmt.where(Document.company_id == current_user.company_id)
    return stmt


def create_document(db: Session, document: Document) -> Document:
    db.add(document)
    db.flush()
    return document


def list_documents(db: Session, current_user: User, *, limit: int = 50, offset: int = 0) -> list[Document]:
    stmt = _scoped(select(Document), current_user).order_by(Document.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


def get_document(db: Session, document_id: uuid.UUID, current_user: User) -> Document | None:
    stmt = _scoped(select(Document).where(Document.id == document_id), current_user)
    return db.execute(stmt).scalar_one_or_none()


def delete_document(db: Session, document: Document) -> None:
    db.delete(document)


def update_document(db: Session, document: Document, data: dict) -> Document:
    for key, value in data.items():
        setattr(document, key, value)
    db.flush()
    return document

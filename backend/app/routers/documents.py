import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.crud.document import create_document, delete_document, get_document, list_documents
from app.db import get_db
from app.dependencies import get_current_user
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentOut
from app.services.audit_service import log_audit
from app.services.storage_service import delete_file, save_uploaded_file
from app.tasks.document_tasks import process_document_task

router = APIRouter(prefix='/documents', tags=['documents'])


@router.post('/upload', response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    product_id: uuid.UUID | None = Form(default=None),
    document_type: str = Form(default='other'),
    number: str | None = Form(default=None),
    document_date: date | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentOut:
    path = save_uploaded_file(str(current_user.company_id), file)

    document = Document(
        company_id=current_user.company_id,
        product_id=product_id,
        document_type=document_type,
        number=number,
        document_date=document_date,
        file_path=path,
        original_filename=file.filename or 'file',
        mime_type=file.content_type or 'application/octet-stream',
        status=DocumentStatus.UPLOADED,
        created_by=current_user.id,
    )
    create_document(db, document)

    log_audit(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action='documents.upload',
        entity_type='document',
        entity_id=str(document.id),
    )
    db.commit()
    db.refresh(document)

    try:
        process_document_task.delay(str(document.id))
    except Exception:
        # Do not break upload flow if broker is temporary unavailable.
        pass

    return DocumentOut.model_validate(document)


@router.get('', response_model=list[DocumentOut])
def documents_index(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentOut]:
    return [DocumentOut.model_validate(doc) for doc in list_documents(db, current_user, limit=limit, offset=offset)]


@router.get('/{document_id}', response_model=DocumentOut)
def documents_get(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentOut:
    document = get_document(db, document_id, current_user)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Document not found')
    return DocumentOut.model_validate(document)


@router.delete('/{document_id}')
def documents_delete(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    document = get_document(db, document_id, current_user)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Document not found')

    delete_file(document.file_path)
    delete_document(db, document)

    log_audit(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action='documents.delete',
        entity_type='document',
        entity_id=str(document_id),
    )
    db.commit()
    return {'message': 'Document deleted'}

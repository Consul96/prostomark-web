import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.product import create_product, delete_product, get_product, list_products, update_product
from app.db import get_db
from app.dependencies import get_current_user
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.audit_service import log_audit

router = APIRouter(prefix='/products', tags=['products'])


@router.get('', response_model=list[ProductOut])
def products_index(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProductOut]:
    return [ProductOut.model_validate(row) for row in list_products(db, current_user, limit=limit, offset=offset)]


@router.post('', response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def products_create(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductOut:
    product = Product(company_id=current_user.company_id, created_by=current_user.id, **payload.model_dump())
    create_product(db, product)
    log_audit(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action='products.create',
        entity_type='product',
        entity_id=str(product.id),
    )
    db.commit()
    db.refresh(product)
    return ProductOut.model_validate(product)


@router.get('/{product_id}', response_model=ProductOut)
def products_get(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductOut:
    product = get_product(db, product_id, current_user)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
    return ProductOut.model_validate(product)


@router.put('/{product_id}', response_model=ProductOut)
def products_update(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductOut:
    product = get_product(db, product_id, current_user)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    updated = update_product(db, product, payload.model_dump(exclude_none=True))
    log_audit(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action='products.update',
        entity_type='product',
        entity_id=str(product.id),
    )
    db.commit()
    db.refresh(updated)
    return ProductOut.model_validate(updated)


@router.delete('/{product_id}')
def products_delete(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    product = get_product(db, product_id, current_user)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

    delete_product(db, product)
    log_audit(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action='products.delete',
        entity_type='product',
        entity_id=str(product.id),
    )
    db.commit()
    return {'message': 'Product deleted'}

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.calculation import create_calculation, get_calculation, list_calculations
from app.db import get_db
from app.dependencies import get_current_user
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationCreate, CalculationOut
from app.services.audit_service import log_audit
from app.services.calculation_service import build_calculation_result

router = APIRouter(prefix='/calculations', tags=['calculations'])


@router.post('', response_model=CalculationOut, status_code=status.HTTP_201_CREATED)
def calculations_create(
    payload: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalculationOut:
    result_json, total = build_calculation_result(payload.input_json)

    row = Calculation(
        company_id=current_user.company_id,
        user_id=current_user.id,
        input_json=payload.input_json,
        result_json=result_json,
        currency=payload.currency,
        total_amount=total,
    )
    create_calculation(db, row)

    log_audit(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action='calculations.create',
        entity_type='calculation',
        entity_id=str(row.id),
    )
    db.commit()
    db.refresh(row)

    return CalculationOut.model_validate(row)


@router.get('', response_model=list[CalculationOut])
def calculations_index(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CalculationOut]:
    return [CalculationOut.model_validate(item) for item in list_calculations(db, current_user, limit=limit, offset=offset)]


@router.get('/{calculation_id}', response_model=CalculationOut)
def calculations_get(
    calculation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalculationOut:
    item = get_calculation(db, calculation_id, current_user)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Calculation not found')
    return CalculationOut.model_validate(item)

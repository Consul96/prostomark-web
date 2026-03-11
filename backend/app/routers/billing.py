from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.billing import CheckoutRequest, CheckoutResponse, CurrentPlanResponse
from app.services.audit_service import log_audit
from app.services.billing_service import BillingService

router = APIRouter(prefix='/billing', tags=['billing'])


@router.post('/checkout', response_model=CheckoutResponse)
def create_checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutResponse:
    session = BillingService.create_checkout(db, current_user, payload)
    log_audit(
        db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action='billing.checkout.create',
        entity_type='subscription',
        entity_id=session.get('id'),
        meta_json={'plan_code': payload.plan_code, 'billing_cycle': payload.billing_cycle},
    )
    db.commit()
    return CheckoutResponse(checkout_url=session.get('url', ''), session_id=session.get('id'))


@router.post('/webhook')
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias='stripe-signature'),
    db: Session = Depends(get_db),
) -> dict:
    if not stripe_signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Missing Stripe signature')

    payload = await request.body()
    response = BillingService.process_webhook(db, payload, stripe_signature)
    db.commit()
    return response


@router.get('/current-plan', response_model=CurrentPlanResponse)
def current_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CurrentPlanResponse:
    subscription, plans = BillingService.current_plan(db, current_user)
    return CurrentPlanResponse(subscription=subscription, available_plans=plans)

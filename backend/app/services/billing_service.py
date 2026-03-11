from datetime import UTC, datetime
import uuid

import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.subscription import (
    get_active_company_subscription,
    get_plan_by_code,
    get_subscription_by_stripe_id,
    list_plans,
)
from app.models.enums import SubscriptionStatus
from app.models.subscription import CompanySubscription
from app.models.user import User
from app.schemas.billing import CheckoutRequest

stripe.api_key = settings.stripe_secret_key


class BillingService:
    @staticmethod
    def create_checkout(db: Session, user: User, payload: CheckoutRequest) -> stripe.checkout.Session:
        if not settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stripe is not configured')

        plan = get_plan_by_code(db, payload.plan_code)
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Plan not found')

        current_subscription = get_active_company_subscription(db, user.company_id)
        customer_id = current_subscription.stripe_customer_id if current_subscription else None

        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'company_id': str(user.company_id)},
                name=f'{user.first_name} {user.last_name}',
            )
            customer_id = customer['id']

        amount = plan.price_year if payload.billing_cycle == 'year' else plan.price_month
        interval = 'year' if payload.billing_cycle == 'year' else 'month'

        session = stripe.checkout.Session.create(
            mode='subscription',
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {
                            'name': f'{plan.name} ({payload.billing_cycle})',
                        },
                        'recurring': {'interval': interval},
                        'unit_amount': int(float(amount) * 100),
                    },
                    'quantity': 1,
                }
            ],
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url,
            metadata={
                'company_id': str(user.company_id),
                'plan_id': str(plan.id),
                'plan_code': plan.code,
            },
        )

        if current_subscription:
            current_subscription.stripe_customer_id = customer_id
        else:
            db.add(
                CompanySubscription(
                    company_id=user.company_id,
                    plan_id=plan.id,
                    stripe_customer_id=customer_id,
                    status=SubscriptionStatus.TRIAL,
                )
            )

        db.flush()
        return session

    @staticmethod
    def current_plan(db: Session, user: User) -> tuple[CompanySubscription | None, list]:
        return get_active_company_subscription(db, user.company_id), list_plans(db)

    @staticmethod
    def process_webhook(db: Session, payload: bytes, stripe_signature: str) -> dict:
        if not settings.stripe_webhook_secret:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Webhook secret not configured')

        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.stripe_webhook_secret)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata', {})
            company_id = metadata.get('company_id')
            plan_id = metadata.get('plan_id')
            stripe_subscription_id = session.get('subscription')
            stripe_customer_id = session.get('customer')
            if not company_id or not plan_id:
                return {'received': True}

            subscription = (
                db.query(CompanySubscription)
                .filter(CompanySubscription.company_id == uuid.UUID(company_id))
                .order_by(CompanySubscription.created_at.desc())
                .first()
            )
            if subscription is None:
                subscription = CompanySubscription(company_id=uuid.UUID(company_id), plan_id=uuid.UUID(plan_id))
                db.add(subscription)

            subscription.plan_id = uuid.UUID(plan_id)
            subscription.stripe_customer_id = stripe_customer_id
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.status = SubscriptionStatus.ACTIVE

        if event['type'] in {'customer.subscription.updated', 'customer.subscription.deleted'}:
            data = event['data']['object']
            stripe_subscription_id = data.get('id')
            subscription = get_subscription_by_stripe_id(db, stripe_subscription_id)
            if subscription:
                status_map = {
                    'trialing': SubscriptionStatus.TRIAL,
                    'active': SubscriptionStatus.ACTIVE,
                    'past_due': SubscriptionStatus.PAST_DUE,
                    'canceled': SubscriptionStatus.CANCELED,
                    'unpaid': SubscriptionStatus.EXPIRED,
                }
                subscription.status = status_map.get(data.get('status'), SubscriptionStatus.EXPIRED)
                if data.get('current_period_start'):
                    subscription.current_period_start = datetime.fromtimestamp(data['current_period_start'], tz=UTC)
                if data.get('current_period_end'):
                    subscription.current_period_end = datetime.fromtimestamp(data['current_period_end'], tz=UTC)

        return {'received': True}

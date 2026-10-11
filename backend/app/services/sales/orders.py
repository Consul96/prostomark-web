from decimal import Decimal, ROUND_HALF_UP, localcontext
from fastapi import HTTPException
from sqlalchemy import select
from app.models.sales import SalesCustomer, SalesSeller, SalesOrderItem
from app.models.product import Product
from app.models.user import User

CENT = Decimal("0.01")


def money(value):
    with localcontext() as ctx:
        ctx.prec = 64
        result = value.quantize(CENT, rounding=ROUND_HALF_UP)
        if abs(result) > Decimal("9999999999999999.99"):
            raise HTTPException(422, "Сумма превышает допустимый предел")
        return result


def calculate(quantity, price, discount, vat_rate, included):
    with localcontext() as ctx:
        ctx.prec = 64
        gross = quantity * price
        discounted = money(gross * (1 - discount / Decimal(100)))
        savings = money(gross) - discounted
        if vat_rate is None:
            return discounted, Decimal("0.00"), savings
        vat = (
            money(discounted * vat_rate / (100 + vat_rate))
            if included
            else money(discounted * vat_rate / 100)
        )
        return money(discounted if included else discounted + vat), vat, savings


def scoped(db, model, id, user, lock=False):
    query = select(model).where(model.id == id, model.company_id == user.company_id)
    if lock:
        query = query.with_for_update()
    row = db.scalar(query)
    if row is None:
        raise HTTPException(404, "Запись не найдена")
    return row


def role(user, roles):
    if str(user.role) not in roles:
        raise HTTPException(403, "Недостаточно прав")


def rates_for(seller, day):
    rules = [
        r
        for r in seller.vat_rules
        if r["from_date"] <= day.isoformat()
        and (not r["to_date"] or r["to_date"] >= day.isoformat())
    ]
    if len(rules) != 1:
        raise HTTPException(
            422,
            {
                "missing_fields": [
                    "У продавца нет однозначных настроек НДС на дату заказа"
                ]
            },
        )
    return [None if r is None else Decimal(r) for r in rules[0]["rates"]]


def apply_order(db, order, payload, user):
    customer = scoped(db, SalesCustomer, payload.customer_id, user)
    seller = scoped(db, SalesSeller, payload.seller_id, user)
    if customer.archived or not seller.active:
        raise HTTPException(422, "Выберите действующего покупателя и продавца")
    responsible = payload.responsible_id or user.id
    scoped(db, User, responsible, user)
    data = payload.model_dump(exclude={"items", "revision"})
    data["responsible_id"] = responsible
    for k, v in data.items():
        setattr(order, k, v)
    allowed = rates_for(seller, payload.order_date) if payload.items else []
    lines = []
    for position, item in enumerate(payload.items, 1):
        product = scoped(db, Product, item.product_id, user)
        if item.vat_rate not in allowed:
            raise HTTPException(
                422, f"Ставка НДС позиции {position} не разрешена настройками продавца"
            )
        total, vat, discount = calculate(
            item.quantity,
            item.price,
            item.discount,
            item.vat_rate,
            payload.vat_included,
        )
        lines.append(
            (
                SalesOrderItem(
                    company_id=user.company_id,
                    position=position,
                    name=product.name,
                    article=product.article,
                    gtin=product.gtin,
                    total=total,
                    vat_amount=vat,
                    **item.model_dump(),
                ),
                discount,
            )
        )
    order.items = [r for r, _ in lines]
    order.total = money(sum((r.total for r, _ in lines), Decimal("0.00")))
    order.vat_total = money(sum((r.vat_amount for r, _ in lines), Decimal("0.00")))
    order.discount_total = money(sum((d for _, d in lines), Decimal("0.00")))


def validate_confirm(db, order, user):
    missing = []
    customer = scoped(db, SalesCustomer, order.customer_id, user)
    seller = scoped(db, SalesSeller, order.seller_id, user)
    if customer.archived:
        missing.append("Покупатель архивирован")
    if not seller.active:
        missing.append("Продавец неактивен")
    if not order.items:
        missing.append("Добавьте хотя бы один товар")
    allowed = rates_for(seller, order.order_date)
    for item in order.items:
        if item.vat_rate not in allowed:
            missing.append(f"Проверьте НДС: {item.name}")
    if missing:
        raise HTTPException(422, {"missing_fields": missing})

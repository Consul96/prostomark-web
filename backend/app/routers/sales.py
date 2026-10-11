import hashlib
import re
import uuid
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import get_current_user
from app.models.audit_log import AuditLog
from app.models.product import Product
from app.models.user import User
from app.models.sales import (
    SalesCustomer,
    SalesSeller,
    SalesOrder,
    SalesDocument,
    SalesDocumentFile,
    SalesDocumentTemplate,
    SalesDocumentSequence,
)
from app.schemas.sales import (
    CustomerInput,
    SellerInput,
    OrderInput,
    DocumentInput,
    PreviewInput,
)
from app.services.audit_service import log_audit
from app.services.sales.orders import scoped, role, apply_order, validate_confirm
from app.services.sales.documents import document_data, render

router = APIRouter(prefix="/sales", tags=["sales"])
DB = Depends(get_db)
AUTH = Depends(get_current_user)
MANAGERS = ["manager", "company_admin", "superadmin"]
ADMINS = ["company_admin", "superadmin"]


def out(row):
    return jsonable_encoder(
        {
            c.name: str(getattr(row, c.name))
            if c.type.python_type.__name__ == "Decimal"
            else getattr(row, c.name)
            for c in row.__table__.columns
            if c.name != "content"
        }
    )


def audit(db, user, action, row):
    log_audit(
        db,
        company_id=user.company_id,
        user_id=user.id,
        action="sales." + action,
        entity_type=row.__tablename__,
        entity_id=str(row.id),
        meta_json={
            "revision": getattr(row, "revision", None),
            "status": getattr(row, "status", None),
        },
    )


def order_out(db, order):
    result = out(order)
    result["items"] = [out(i) for i in order.items]
    result["customer_name"] = db.get(SalesCustomer, order.customer_id).name
    result["seller_name"] = db.get(SalesSeller, order.seller_id).name
    u = db.get(User, order.responsible_id)
    result["responsible_name"] = f"{u.first_name} {u.last_name}"
    return result


def page(db, query, limit, offset, serialize=out):
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    return {
        "items": [serialize(r) for r in db.scalars(query.limit(limit).offset(offset))],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def normalized_phone(value):
    digits = re.sub(r"\D", "", value or "")
    return "7" + digits[1:] if len(digits) == 11 and digits.startswith("8") else digits


def duplicates(db, user, row):
    others = db.scalars(
        select(SalesCustomer).where(
            SalesCustomer.company_id == user.company_id, SalesCustomer.id != row.id
        )
    )
    phone = normalized_phone(row.phone)
    return [
        {"id": str(r.id), "name": r.name}
        for r in others
        if (row.inn and row.inn == r.inn)
        or (phone and phone == normalized_phone(r.phone))
    ]


def customer_out(db, user, row):
    data = out(row)
    data["duplicates"] = duplicates(db, user, row)
    data["orders_count"], data["last_order"] = db.execute(
        select(func.count(SalesOrder.id), func.max(SalesOrder.order_date)).where(
            SalesOrder.company_id == user.company_id, SalesOrder.customer_id == row.id
        )
    ).one()
    return jsonable_encoder(data)


@router.get("/customers")
def customers(
    q: str = "",
    kind: Literal["person", "ip", "legal"] | None = None,
    archived: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = DB,
    user: User = AUTH,
):
    query = select(SalesCustomer).where(
        SalesCustomer.company_id == user.company_id, SalesCustomer.archived == archived
    )
    if q:
        predicates = [
            c.ilike(f"%{q}%")
            for c in [SalesCustomer.name, SalesCustomer.phone, SalesCustomer.inn]
        ]
        digits = re.sub(r"\D", "", q)
        if digits:
            predicates.append(
                func.regexp_replace(SalesCustomer.phone, r"\D", "", "g").ilike(
                    f"%{digits}%"
                )
            )
        query = query.where(or_(*predicates))
    if kind:
        query = query.where(SalesCustomer.kind == kind)
    return page(
        db,
        query.order_by(SalesCustomer.name),
        limit,
        offset,
        lambda r: customer_out(db, user, r),
    )


@router.post("/customers", status_code=201)
def create_customer(payload: CustomerInput, db: Session = DB, user: User = AUTH):
    data = payload.model_dump(mode="json")
    data["responsible_id"] = payload.responsible_id or user.id
    scoped(db, User, data["responsible_id"], user)
    row = SalesCustomer(company_id=user.company_id, **data)
    db.add(row)
    db.flush()
    audit(db, user, "customer.create", row)
    db.commit()
    return customer_out(db, user, row)


@router.get("/customers/{id}")
def get_customer(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    return customer_out(db, user, scoped(db, SalesCustomer, id, user))


@router.patch("/customers/{id}")
def update_customer(
    id: uuid.UUID, payload: CustomerInput, db: Session = DB, user: User = AUTH
):
    row = scoped(db, SalesCustomer, id, user, lock=True)
    data = payload.model_dump(mode="json")
    data["responsible_id"] = payload.responsible_id or user.id
    scoped(db, User, data["responsible_id"], user)
    for k, v in data.items():
        setattr(row, k, v)
    audit(db, user, "customer.update", row)
    db.commit()
    return customer_out(db, user, row)


@router.get("/sellers")
def sellers(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = DB,
    user: User = AUTH,
):
    return page(
        db,
        select(SalesSeller)
        .where(SalesSeller.company_id == user.company_id)
        .order_by(SalesSeller.name),
        limit,
        offset,
    )


@router.post("/sellers", status_code=201)
def create_seller(payload: SellerInput, db: Session = DB, user: User = AUTH):
    role(user, ADMINS)
    row = SalesSeller(company_id=user.company_id, **payload.model_dump(mode="json"))
    db.add(row)
    db.flush()
    audit(db, user, "seller.create", row)
    db.commit()
    return out(row)


@router.get("/sellers/{id}")
def get_seller(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    return out(scoped(db, SalesSeller, id, user))


@router.patch("/sellers/{id}")
def update_seller(
    id: uuid.UUID, payload: SellerInput, db: Session = DB, user: User = AUTH
):
    role(user, ADMINS)
    row = scoped(db, SalesSeller, id, user, lock=True)
    for k, v in payload.model_dump(mode="json").items():
        setattr(row, k, v)
    audit(db, user, "seller.update", row)
    db.commit()
    return out(row)


@router.get("/staff")
def staff(db: Session = DB, user: User = AUTH):
    return [
        {"id": str(r.id), "name": f"{r.first_name} {r.last_name}"}
        for r in db.scalars(
            select(User).where(
                User.company_id == user.company_id, User.is_active.is_(True)
            )
        )
    ]


@router.get("/catalog")
def catalog(
    q: str = "",
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = DB,
    user: User = AUTH,
):
    query = select(Product).where(Product.company_id == user.company_id)
    if q:
        query = query.where(
            or_(
                Product.name.ilike(f"%{q}%"),
                Product.article.ilike(f"%{q}%"),
                Product.gtin.ilike(f"%{q}%"),
            )
        )
    return page(db, query.order_by(Product.name), limit, offset)


@router.get("/orders")
def orders(
    q: str = "",
    status: Literal["draft", "confirmed", "completed", "cancelled"] | None = None,
    customer_id: uuid.UUID | None = None,
    seller_id: uuid.UUID | None = None,
    responsible_id: uuid.UUID | None = None,
    source: Literal["telegram", "vk", "phone", "other", "manual"] | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = DB,
    user: User = AUTH,
):
    query = (
        select(SalesOrder)
        .join(SalesCustomer, SalesOrder.customer_id == SalesCustomer.id)
        .where(SalesOrder.company_id == user.company_id)
    )
    for k, v in [
        ("status", status),
        ("customer_id", customer_id),
        ("seller_id", seller_id),
        ("source", source),
        ("responsible_id", responsible_id),
    ]:
        if v is not None:
            query = query.where(getattr(SalesOrder, k) == v)
    if q:
        query = query.where(
            or_(SalesOrder.number.ilike(f"%{q}%"), SalesCustomer.name.ilike(f"%{q}%"))
        )
    if from_date:
        query = query.where(SalesOrder.order_date >= from_date)
    if to_date:
        query = query.where(SalesOrder.order_date <= to_date)
    return page(
        db,
        query.order_by(SalesOrder.created_at.desc(), SalesOrder.id),
        limit,
        offset,
        lambda r: order_out(db, r),
    )


@router.get("/customers/{id}/orders")
def customer_orders(
    id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = DB,
    user: User = AUTH,
):
    scoped(db, SalesCustomer, id, user)
    return page(
        db,
        select(SalesOrder)
        .where(SalesOrder.company_id == user.company_id, SalesOrder.customer_id == id)
        .order_by(SalesOrder.created_at.desc()),
        limit,
        offset,
        lambda r: order_out(db, r),
    )


@router.post("/orders", status_code=201)
def create_order(payload: OrderInput, db: Session = DB, user: User = AUTH):
    row = SalesOrder(
        company_id=user.company_id,
        number="З-" + uuid.uuid4().hex.upper(),
        status="draft",
        revision=1,
    )
    apply_order(db, row, payload, user)
    db.add(row)
    db.flush()
    audit(db, user, "order.create", row)
    db.commit()
    return order_out(db, row)


@router.get("/orders/{id}")
def get_order(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    return order_out(db, scoped(db, SalesOrder, id, user))


@router.patch("/orders/{id}")
def update_order(
    id: uuid.UUID, payload: OrderInput, db: Session = DB, user: User = AUTH
):
    row = scoped(db, SalesOrder, id, user, lock=True)
    if row.status != "draft":
        raise HTTPException(
            409, "Редактирование доступно только в черновике. Верните заказ в черновик."
        )
    if payload.revision != row.revision:
        raise HTTPException(409, "Заказ изменён другим сотрудником. Обновите страницу.")
    apply_order(db, row, payload, user)
    row.revision += 1
    audit(db, user, "order.update", row)
    db.commit()
    return order_out(db, row)


def transition(db, id, user, target):
    role(user, MANAGERS)
    row = scoped(db, SalesOrder, id, user, lock=True)
    allowed = {
        "confirmed": ["draft"],
        "completed": ["confirmed"],
        "cancelled": ["draft", "confirmed"],
        "draft": ["confirmed"],
    }
    if row.status not in allowed[target]:
        raise HTTPException(409, "Недопустимый переход статуса")
    if target == "confirmed":
        validate_confirm(db, row, user)
    row.status = target
    row.revision += 1
    audit(db, user, "order." + target, row)
    db.commit()
    return order_out(db, row)


@router.post("/orders/{id}/confirm")
def confirm(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    return transition(db, id, user, "confirmed")


@router.post("/orders/{id}/cancel")
def cancel(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    return transition(db, id, user, "cancelled")


@router.post("/orders/{id}/complete")
def complete(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    return transition(db, id, user, "completed")


@router.post("/orders/{id}/reopen")
def reopen(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    return transition(db, id, user, "draft")


@router.post("/orders/{id}/duplicate", status_code=201)
def duplicate(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    row = scoped(db, SalesOrder, id, user)
    payload = OrderInput(
        customer_id=row.customer_id,
        seller_id=row.seller_id,
        responsible_id=user.id,
        order_date=date.today(),
        source=row.source,
        delivery_address=row.delivery_address,
        comment=row.comment,
        basis=row.basis,
        vat_included=row.vat_included,
        items=[
            {
                k: getattr(i, k)
                for k in [
                    "product_id",
                    "unit",
                    "okei",
                    "quantity",
                    "price",
                    "discount",
                    "vat_rate",
                ]
            }
            for i in row.items
        ],
    )
    return create_order(payload, db, user)


@router.get("/orders/{id}/history")
def history(id: uuid.UUID, db: Session = DB, user: User = AUTH):
    scoped(db, SalesOrder, id, user)
    return [
        out(r)
        for r in db.scalars(
            select(AuditLog)
            .where(
                AuditLog.company_id == user.company_id, AuditLog.entity_id == str(id)
            )
            .order_by(AuditLog.created_at.desc())
        )
    ]


@router.get("/templates")
def templates(db: Session = DB, user: User = AUTH):
    return [
        out(r)
        for r in db.scalars(
            select(SalesDocumentTemplate).where(
                or_(
                    SalesDocumentTemplate.company_id == user.company_id,
                    SalesDocumentTemplate.company_id.is_(None),
                ),
                SalesDocumentTemplate.status == "active",
            )
        )
    ]


@router.get("/documents")
def documents(
    order_id: uuid.UUID | None = None,
    document_type: Literal["torg12", "upd", "invoice"] | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = DB,
    user: User = AUTH,
):
    query = select(SalesDocument).where(SalesDocument.company_id == user.company_id)
    if order_id:
        scoped(db, SalesOrder, order_id, user)
        query = query.where(SalesDocument.order_id == order_id)
    if document_type:
        query = query.where(SalesDocument.document_type == document_type)
    return page(db, query.order_by(SalesDocument.created_at.desc()), limit, offset)


@router.get("/orders/{id}/documents")
def order_documents(
    id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = DB,
    user: User = AUTH,
):
    return documents(id, None, limit, offset, db, user)


def file_response(content, format, name, inline=False):
    mime = (
        "application/pdf"
        if format == "pdf"
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    return Response(
        content,
        media_type=mime,
        headers={
            "Content-Disposition": f'{"inline" if inline else "attachment"}; filename="{name}.{format}"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post("/orders/{id}/documents/preview")
def preview(id: uuid.UUID, payload: PreviewInput, db: Session = DB, user: User = AUTH):
    row = scoped(db, SalesOrder, id, user)
    data = document_data(db, row, payload, user, "ЧЕРНОВИК", 0, draft=True)
    return file_response(
        render(data, payload.format), payload.format, "draft", inline=True
    )


@router.post("/orders/{id}/documents", status_code=201)
def issue(id: uuid.UUID, payload: DocumentInput, db: Session = DB, user: User = AUTH):
    # Serialize issuance for an order, then lock seller to serialize its number sequence.
    row = scoped(db, SalesOrder, id, user, lock=True)
    request = payload.model_dump(mode="json")
    previous_request = db.scalar(
        select(SalesDocument).where(
            SalesDocument.company_id == user.company_id,
            SalesDocument.idempotency_key == payload.idempotency_key,
        )
    )
    if previous_request:
        if previous_request.order_id != id or previous_request.request_json != request:
            raise HTTPException(
                409, "Ключ запроса уже использован для другого документа"
            )
        return out(previous_request)
    if row.status not in ["confirmed", "completed"]:
        raise HTTPException(409, "Документы выпускаются из подтверждённого заказа")
    scoped(db, SalesSeller, row.seller_id, user, lock=True)
    # Requests on another order could share a key. Seller lock is insufficient across sellers.
    db.execute(
        select(
            func.pg_advisory_xact_lock(
                int.from_bytes(
                    hashlib.sha256(
                        (str(user.company_id) + str(payload.idempotency_key)).encode()
                    ).digest()[:8],
                    "big",
                    signed=True,
                )
            )
        )
    )
    previous_request = db.scalar(
        select(SalesDocument).where(
            SalesDocument.company_id == user.company_id,
            SalesDocument.idempotency_key == payload.idempotency_key,
        )
    )
    if previous_request:
        if previous_request.order_id != id or previous_request.request_json != request:
            raise HTTPException(409, "Ключ запроса уже использован")
        return out(previous_request)
    prev = db.scalar(
        select(SalesDocument)
        .where(
            SalesDocument.order_id == id,
            SalesDocument.seller_id == row.seller_id,
            SalesDocument.document_type == payload.document_type,
            SalesDocument.year == payload.document_date.year,
        )
        .order_by(SalesDocument.version.desc())
    )
    if not prev and not payload.new_version:
        prior = db.scalar(
            select(SalesDocument.id)
            .where(
                SalesDocument.order_id == id,
                SalesDocument.seller_id == row.seller_id,
                SalesDocument.document_type == payload.document_type,
            )
            .limit(1)
        )
        if prior:
            raise HTTPException(
                409,
                "Подтвердите выпуск документа в новом году; предыдущие файлы сохранятся",
            )
    if prev and prev.order_revision == row.revision and not payload.new_version:
        if (
            prev.document_date != payload.document_date
            or prev.snapshot["upd_status"] != payload.upd_status
            or (payload.template_id and prev.template_id != payload.template_id)
        ):
            raise HTTPException(
                409, "Параметры документа изменены. Подтвердите выпуск новой версии."
            )
        return out(prev)
    if prev and not payload.new_version:
        raise HTTPException(
            409, "Подтвердите выпуск новой версии; предыдущие файлы сохранятся"
        )
    if payload.new_version:
        role(user, MANAGERS)
    year = payload.document_date.year
    if prev and prev.year != year:
        prev = None
    # Atomic PostgreSQL UPSERT returns the next number. Rolled back if rendering fails.
    if prev:
        number, version = prev.number, prev.version + 1
    else:
        stmt = insert(SalesDocumentSequence).values(
            id=uuid.uuid4(),
            company_id=user.company_id,
            seller_id=row.seller_id,
            document_type=payload.document_type,
            year=year,
            value=1,
        )
        number = db.scalar(
            stmt.on_conflict_do_update(
                index_elements=["seller_id", "document_type", "year"],
                set_={"value": SalesDocumentSequence.value + 1},
            ).returning(SalesDocumentSequence.value)
        )
        version = 1
    snapshot = document_data(db, row, payload, user, number, version)
    document = SalesDocument(
        company_id=user.company_id,
        order_id=row.id,
        seller_id=row.seller_id,
        template_id=uuid.UUID(snapshot["template_id"]),
        document_type=payload.document_type,
        number=number,
        year=year,
        document_date=payload.document_date,
        version=version,
        order_revision=row.revision,
        idempotency_key=payload.idempotency_key,
        request_json=request,
        snapshot=snapshot,
        created_by=user.id,
    )
    db.add(document)
    db.flush()
    for format in ["xlsx", "pdf"]:
        content = render(snapshot, format)
        db.add(
            SalesDocumentFile(
                company_id=user.company_id,
                document_id=document.id,
                format=format,
                content=content,
                sha256=hashlib.sha256(content).hexdigest(),
                size=len(content),
            )
        )
    audit(db, user, "document.issue", document)
    log_audit(
        db,
        company_id=user.company_id,
        user_id=user.id,
        action="sales.order.document",
        entity_type="sales_orders",
        entity_id=str(row.id),
        meta_json={
            "document_id": str(document.id),
            "type": document.document_type,
            "version": version,
        },
    )
    db.commit()
    return out(document)


@router.get("/documents/{id}/download")
def download(
    id: uuid.UUID,
    format: Literal["xlsx", "pdf"] = "pdf",
    db: Session = DB,
    user: User = AUTH,
):
    doc = scoped(db, SalesDocument, id, user)
    file = db.scalar(
        select(SalesDocumentFile).where(
            SalesDocumentFile.document_id == doc.id,
            SalesDocumentFile.company_id == user.company_id,
            SalesDocumentFile.format == format,
        )
    )
    if not file:
        raise HTTPException(404, "Файл не найден")
    if hashlib.sha256(file.content).hexdigest() != file.sha256:
        raise HTTPException(500, "Контрольная сумма файла не совпадает")
    return file_response(
        file.content,
        format,
        f"{doc.document_type}-{doc.year}-{doc.number}-v{doc.version}",
    )


@router.post("/calculate")
def calculate_order(payload: OrderInput, db: Session = DB, user: User = AUTH):
    order = SalesOrder(company_id=user.company_id)
    apply_order(db, order, payload, user)
    return {
        "total": str(order.total),
        "vat_total": str(order.vat_total),
        "discount_total": str(order.discount_total),
        "lines": [
            {"total": str(i.total), "vat_amount": str(i.vat_amount)}
            for i in order.items
        ],
    }

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

Name = Annotated[str, Field(min_length=1, max_length=255)]
Money = Annotated[Decimal, Field(ge=0, max_digits=16, decimal_places=2)]
Rate = Annotated[Decimal, Field(ge=0, le=100, max_digits=7, decimal_places=4)]
Source = Literal["telegram", "vk", "phone", "other", "manual"]
DocType = Literal["torg12", "upd", "invoice"]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Details(Input):
    full_name: str = Field(default="", max_length=1000)
    email: EmailStr | None = None
    contact: str = Field(default="", max_length=255)
    telegram: str = Field(default="", max_length=255)
    vk: str = Field(default="", max_length=255)
    source: Source = "manual"
    comment: str = Field(default="", max_length=4000)
    kpp: str = Field(default="", pattern=r"^(\d{9})?$")
    ogrn: str = Field(default="", pattern=r"^(\d{13}|\d{15})?$")
    legal_address: str = Field(default="", max_length=2000)
    actual_address: str = Field(default="", max_length=2000)
    shipping_address: str = Field(default="", max_length=2000)
    delivery_addresses: list[Annotated[str, Field(max_length=2000)]] = Field(
        default_factory=list, max_length=20
    )
    account: str = Field(default="", pattern=r"^(\d{20})?$")
    bank: str = Field(default="", max_length=255)
    bik: str = Field(default="", pattern=r"^(\d{9})?$")
    correspondent_account: str = Field(default="", pattern=r"^(\d{20})?$")
    signatory: str = Field(default="", max_length=255)
    position: str = Field(default="", max_length=255)
    authority: str = Field(default="", max_length=1000)
    taxation: str = Field(default="", max_length=255)
    okpo: str = Field(default="", max_length=14)
    okei: str = Field(default="796", max_length=10)


class CustomerInput(Input):
    kind: Literal["person", "ip", "legal"]
    name: Name
    phone: str | None = Field(default=None, max_length=40)
    inn: str | None = Field(default=None, pattern=r"^(\d{10}|\d{12})$")
    details: Details = Field(default_factory=Details)
    archived: bool = False
    responsible_id: UUID | None = None

    @model_validator(mode="after")
    def inn_kind(self):
        if self.inn and (
            (self.kind == "legal" and len(self.inn) != 10)
            or (self.kind == "ip" and len(self.inn) != 12)
        ):
            raise ValueError("ИНН организации: 10 цифр; ИП: 12 цифр")
        return self


class VatRule(Input):
    from_date: date
    to_date: date | None = None
    rates: list[Rate | None] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def dates(self):
        if self.to_date and self.to_date < self.from_date:
            raise ValueError("Конец периода НДС раньше начала")
        return self


class SellerInput(Input):
    kind: Literal["ip", "legal"]
    name: Name
    inn: str | None = Field(default=None, pattern=r"^(\d{10}|\d{12})$")
    details: Details = Field(default_factory=Details)
    vat_rules: list[VatRule] = Field(default_factory=list, max_length=50)
    active: bool = True

    @model_validator(mode="after")
    def valid_rules(self):
        if self.inn and len(self.inn) != (12 if self.kind == "ip" else 10):
            raise ValueError("ИНН не соответствует типу продавца")
        rules = sorted(self.vat_rules, key=lambda r: r.from_date)
        for a, b in zip(rules, rules[1:]):
            if a.to_date is None or a.to_date >= b.from_date:
                raise ValueError("Периоды ставок НДС пересекаются")
        return self


class ItemInput(Input):
    product_id: UUID
    unit: str = Field(default="шт.", min_length=1, max_length=40)
    okei: str = Field(default="796", pattern=r"^\d{3,4}$")
    quantity: Decimal = Field(gt=0, max_digits=15, decimal_places=3)
    price: Money
    discount: Rate = Decimal("0")
    vat_rate: Rate | None = None


class OrderInput(Input):
    customer_id: UUID
    seller_id: UUID
    responsible_id: UUID | None = None
    order_date: date
    source: Source = "manual"
    delivery_address: str = Field(default="", max_length=2000)
    comment: str = Field(default="", max_length=4000)
    basis: str = Field(default="", max_length=1000)
    vat_included: bool = True
    items: list[ItemInput] = Field(default_factory=list, max_length=500)
    revision: int | None = Field(default=None, ge=1)


class DocumentInput(Input):
    document_type: DocType
    document_date: date
    upd_status: Literal[1, 2] = 2
    template_id: UUID | None = None
    idempotency_key: UUID
    new_version: bool = False


class PreviewInput(Input):
    document_type: DocType
    document_date: date
    upd_status: Literal[1, 2] = 2
    template_id: UUID | None = None
    format: Literal["xlsx", "pdf"] = "pdf"

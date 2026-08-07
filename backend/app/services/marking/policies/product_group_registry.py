"""Реестр правил по товарным группам.

Первый релиз полноценно поддерживает лёгкую промышленность и обувь. Обе группы
формируют отчёт о нанесении АВТОМАТИЧЕСКИ на стороне ГИС МТ, поэтому ручной
`/utilisation` для них не отправляется — контроль нанесения идёт через True API
(`/cises/info`). Архитектура позволяет добавлять группы без правки основных сервисов.

Источники значений зафиксированы в docs/marking/crpt-api-mapping.md. Значения,
не подтверждённые документацией, помечены `confirmed=False` и требуют проверки
перед боевым использованием.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.enums import ProductGroupCode, ReleaseMethodType, WorkflowType


@dataclass(frozen=True)
class ProductGroupPolicy:
    code: str
    title: str
    supports_gtin: bool
    # Обязательные поля карточки НК (минимальный набор для валидации).
    required_card_fields: tuple[str, ...]
    # Тип формирования отчёта о нанесении.
    auto_application_report: bool
    manual_application_report: bool
    # Значения для заказа КМ (СУЗ).
    order_release_methods: tuple[str, ...]
    default_template_id: str | None
    cis_type: str | None
    # Поддержанные сценарии ввода в оборот.
    circulation_workflows: tuple[str, ...]
    # Лимиты (источник — mapping-doc; None = не подтверждён документацией).
    max_codes_per_order: int | None
    max_km_per_manual_report: int | None
    confirmed: bool = True
    notes: str = ''


_LIGHT_INDUSTRY = ProductGroupPolicy(
    code=ProductGroupCode.LIGHT_INDUSTRY.value,
    title='Лёгкая промышленность',
    supports_gtin=True,
    required_card_fields=('name', 'tnved', 'brand', 'article'),
    auto_application_report=True,
    manual_application_report=False,
    order_release_methods=(
        ReleaseMethodType.PRODUCTION.value,
        ReleaseMethodType.IMPORT.value,
        ReleaseMethodType.REMAINS.value,
    ),
    default_template_id=None,  # НЕ подтверждён документацией — задать при интеграции СУЗ
    cis_type=None,
    circulation_workflows=(
        WorkflowType.PRODUCTION_RF.value,
        WorkflowType.IMPORT_FTS.value,
        WorkflowType.IMPORT_EAEU.value,
        WorkflowType.REMAINS.value,
    ),
    max_codes_per_order=None,  # уточнить в API СУЗ 3.0
    max_km_per_manual_report=None,
    confirmed=True,
    notes='Отчёт о нанесении формируется автоматически; ручной /utilisation не отправляется.',
)

_SHOES = ProductGroupPolicy(
    code=ProductGroupCode.SHOES.value,
    title='Обувь',
    supports_gtin=True,
    required_card_fields=('name', 'tnved', 'brand', 'article'),
    auto_application_report=True,
    manual_application_report=False,
    order_release_methods=(
        ReleaseMethodType.PRODUCTION.value,
        ReleaseMethodType.IMPORT.value,
        ReleaseMethodType.REMAINS.value,
    ),
    default_template_id=None,
    cis_type=None,
    circulation_workflows=(
        WorkflowType.PRODUCTION_RF.value,
        WorkflowType.IMPORT_FTS.value,
        WorkflowType.IMPORT_EAEU.value,
        WorkflowType.REMAINS.value,
    ),
    max_codes_per_order=None,
    max_km_per_manual_report=None,
    confirmed=True,
    notes='Отчёт о нанесении формируется автоматически; ручной /utilisation не отправляется.',
)


@dataclass
class ProductGroupPolicyRegistry:
    _policies: dict[str, ProductGroupPolicy] = field(default_factory=dict)

    def register(self, policy: ProductGroupPolicy) -> None:
        self._policies[policy.code] = policy

    def get(self, code: str) -> ProductGroupPolicy | None:
        return self._policies.get(code)

    def require(self, code: str) -> ProductGroupPolicy:
        policy = self.get(code)
        if policy is None:
            from app.services.marking.errors import MarkingError

            raise MarkingError(
                f'Товарная группа «{code}» не поддерживается',
                code='MARKING_UNSUPPORTED_PRODUCT_GROUP',
            )
        return policy

    def all(self) -> list[ProductGroupPolicy]:
        return list(self._policies.values())


registry = ProductGroupPolicyRegistry()
registry.register(_LIGHT_INDUSTRY)
registry.register(_SHOES)

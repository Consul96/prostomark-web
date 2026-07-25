from enum import StrEnum


class UserRole(StrEnum):
    SUPERADMIN = 'superadmin'
    COMPANY_ADMIN = 'company_admin'
    MANAGER = 'manager'
    USER = 'user'


class SubscriptionStatus(StrEnum):
    TRIAL = 'trial'
    ACTIVE = 'active'
    PAST_DUE = 'past_due'
    CANCELED = 'canceled'
    EXPIRED = 'expired'


class DocumentStatus(StrEnum):
    UPLOADED = 'uploaded'
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    FAILED = 'failed'


# ---------------------------------------------------------------------------
# Модуль «Честный знак» (marking)
# ---------------------------------------------------------------------------


class CrptEnvironment(StrEnum):
    SANDBOX = 'sandbox'
    PRODUCTION = 'production'


class ConnectionStatus(StrEnum):
    UNKNOWN = 'unknown'
    OK = 'ok'
    NEEDS_SETUP = 'needs_setup'
    EXPIRED = 'expired'
    CERT_UNAVAILABLE = 'cert_unavailable'
    UNAVAILABLE = 'unavailable'


class MchdStatus(StrEnum):
    UNKNOWN = 'unknown'
    ACTIVE = 'active'
    EXPIRED = 'expired'
    REVOKED = 'revoked'
    NOT_SET = 'not_set'


class ProductGroupCode(StrEnum):
    # Коды товарных групп ГИС МТ, поддержанные первым релизом.
    LIGHT_INDUSTRY = 'lp'  # лёгкая промышленность
    SHOES = 'shoes'  # обувь


class MarkingApplicationStatus(StrEnum):
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ARCHIVED = 'archived'


class ProductCardStatus(StrEnum):
    DRAFT = 'draft'
    VALIDATED = 'validated'
    GTIN_PENDING = 'gtin_pending'
    GTIN_ASSIGNED = 'gtin_assigned'
    FEED_SENT = 'feed_sent'
    MODERATION = 'moderation'
    PUBLISHED = 'published'
    ERROR = 'error'


class KmOrderStatus(StrEnum):
    DRAFT = 'draft'
    VALIDATED = 'validated'
    WAITING_FOR_SIGNATURE = 'waiting_for_signature'
    SENT = 'sent'
    PENDING = 'pending'  # заказ принят СУЗ, коды готовятся
    READY = 'ready'  # часть/все коды доступны к получению
    PARTIALLY_RECEIVED = 'partially_received'
    RECEIVED = 'received'
    CLOSED = 'closed'
    REJECTED = 'rejected'
    ERROR = 'error'


class ApplicationReportStatus(StrEnum):
    DRAFT = 'draft'
    VALIDATING = 'validating'
    CHECKED = 'checked'  # контроль нанесения (True API) завершён
    WAITING_FOR_SIGNATURE = 'waiting_for_signature'
    SENT = 'sent'  # ручной отчёт отправлен в СУЗ
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    ERROR = 'error'


class CirculationDocumentStatus(StrEnum):
    DRAFT = 'draft'
    VALIDATING = 'validating'
    VALIDATED = 'validated'
    WAITING_FOR_SIGNATURE = 'waiting_for_signature'
    SENT = 'sent'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    ERROR = 'error'


class SignJobStatus(StrEnum):
    PENDING = 'pending'
    CLAIMED = 'claimed'  # агент забрал задачу
    COMPLETED = 'completed'
    FAILED = 'failed'
    EXPIRED = 'expired'


class SignJobType(StrEnum):
    ATTACHED = 'attached'
    DETACHED = 'detached'


class OperationJobStatus(StrEnum):
    PENDING = 'pending'
    VALIDATING = 'validating'
    WAITING_FOR_SIGNATURE = 'waiting_for_signature'
    QUEUED = 'queued'
    PROCESSING = 'processing'
    WAITING_EXTERNAL_SYSTEM = 'waiting_external_system'
    COMPLETED = 'completed'
    COMPLETED_WITH_ERRORS = 'completed_with_errors'
    FAILED = 'failed'
    CANCELED = 'canceled'


class WorkflowType(StrEnum):
    # Сценарий ввода в оборот.
    IMPORT_FTS = 'import_fts'  # импорт после ФТС (Россия, третьи страны)
    IMPORT_EAEU = 'import_eaeu'  # ввоз из ЕАЭС
    PRODUCTION_RF = 'production_rf'  # производство в РФ
    REMAINS = 'remains'  # маркировка остатков


class ReleaseMethodType(StrEnum):
    PRODUCTION = 'PRODUCTION'
    IMPORT = 'IMPORT'
    REMAINS = 'REMAINS'
    CROSSBORDER = 'CROSSBORDER'
    REMARKING = 'REMARKING'

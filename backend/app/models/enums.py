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

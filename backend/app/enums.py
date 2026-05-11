"""Single source of truth for enum-like values used in models, schemas and APIs."""
from enum import Enum


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class IngestionSource(str, Enum):
    API = "api"
    FTP = "ftp"
    DAILY = "daily"


class IngestionStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class TrackingEventType(str, Enum):
    ASSIGN = "assign"
    REMOVE = "remove"


class TrackingItemType(str, Enum):
    WAGON = "Вагон"
    CONTAINER = "Контейнер"


class DocumentType(str, Enum):
    INVOICE = "invoice"
    INVOICE_VAT = "invoice_vat"
    ACT = "act"
    ACT_APPENDIX = "act_appendix"
    UNIQUE_NUMBERS = "unique_numbers"


class DocumentFormat(str, Enum):
    PDF = "pdf"
    XLSX = "xlsx"


class EmailLogStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ReportFormat(str, Enum):
    XLSX = "xlsx"
    CSV = "csv"

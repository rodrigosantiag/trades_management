from enum import unique, Enum


@unique
class ErrorCode(Enum):
    VALIDATION = "validation"

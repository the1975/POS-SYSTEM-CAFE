from app.core.exceptions import AppError


class InvalidDateRangeError(AppError):
    status_code = 422
    code = "INVALID_DATE_RANGE"

    def __init__(self, message: str) -> None:
        super().__init__(message)

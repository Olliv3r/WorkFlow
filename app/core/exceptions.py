class AppException(Exception):
    status_code = 500
    message = "Internal server error"

    def __init__(self, message=None):
        if message:
            self.message = message

        super().__init__(self.message)


class NotFoundError(AppException):
    status_code = 404


class ConflictError(AppException):
    status_code = 409


class ValidationError(AppException):
    status_code = 422


class PermissionError(AppException):
    status_code = 403


class UnauthorizedError(AppException):
    status_code = 401


class TooManyRequestsError(AppException):
    status_code = 429


class InternalServerError(AppException):
    status_code = 500


class TokenInvalidError(AppException):
    status_code = 401


class TokenExpiredError(AppException):
    status_code = 401

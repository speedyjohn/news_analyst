class AppError(Exception):
    status = 400
    code = "bad_request"

    def __init__(self, message: str, *, code: str | None = None, status: int | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status:
            self.status = status


class NotFound(AppError):
    status = 404
    code = "not_found"


class Unauthorized(AppError):
    status = 401
    code = "unauthorized"


class Forbidden(AppError):
    status = 403
    code = "forbidden"


class ValidationError(AppError):
    status = 400
    code = "validation_error"


class RateLimited(AppError):
    status = 429
    code = "rate_limited"


class ModerationRejected(AppError):
    status = 400
    code = "moderation_rejected"


class LLMError(AppError):
    status = 503
    code = "llm_unavailable"


class Conflict(AppError):
    status = 409
    code = "conflict"

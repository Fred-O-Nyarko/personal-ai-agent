class BaseAppError(Exception):
    """Root exception for all app errors."""
    code: str = "APP_ERROR"
    status_code: int = 500

    def __init__(self, message: str = "An unexpected error occurred") -> None:
        self.message = message
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code-{self.code}, message={self.message!r})"


# ── Tool Errors ───────────────────────────────────────────────────────────────

class ToolError(BaseAppError):
    code = "TOOL_ERROR"
    status_code = 422

class ToolNotFoundError(ToolError):
    code = "TOOL_NOT_FOUND"
    status_code = 404

class ContentTooLargeError(ToolError):
    code = "CONTENT_TOO_LARGE"
    status_code = 413

# ── LLM Errors ────────────────────────────────────────────────────────────────

class LLMError(BaseAppError):
    code = "LLM_ERROR"
    status_code = 502

class UnknownProviderError(LLMError):
    code = "UNKNOWN_PROVIDER"
    status_code = 500

class LLMStreamError(LLMError):
    code = "LLM_STREAM_ERROR"
    status_code = 502

# ── Domain Errors ─────────────────────────────────────────────────────────────

class ThreadNotFoundError(BaseAppError):
    code = "THREAD_NOT_FOUND"
    status_code = 404

class RunNotFoundError(BaseAppError):
    code = "RUN_NOT_FOUND"
    status_code = 404
from pydantic import Field
import fitz
from fastapi import UploadFile

from app.tools.base import BaseTool, ToolInput, ToolOutput
from app.core.exceptions import ToolError
from app.config import get_settings


class PDFInput(ToolInput):
    file: UploadFile = Field(...)

    model_config = {"arbitrary_types_allowed": True}


class PDFReaderTool(BaseTool):
    """
    Accepts an uploaded PDF file and extracts its text content
    page by page using PyMuPDF.
    """

    name        = "pdf_reader"
    description = "Extract text content from an uploaded PDF file."

    async def execute(self, tool_input: ToolInput) -> ToolOutput:
        assert isinstance(tool_input, PDFInput)
        settings = get_settings()

        try:
            contents = await tool_input.file.read()
            doc      = fitz.open(stream=contents, filetype="pdf")
            pages    = [page.get_text() for page in doc]
            text     = "\n".join(pages)

        except Exception as e:
            raise ToolError(f"Failed to parse PDF: {e}") from e

        text = self._truncate(text, settings.max_content_tokens)

        return ToolOutput(
            content=text,
            metadata={
                "filename": tool_input.file.filename or "unknown.pdf",
                "pages":    len(pages),
                "chars":    len(text),
            },
        )

    def _truncate(self, text: str, max_tokens: int) -> str:
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            return text[:max_chars]
        return text

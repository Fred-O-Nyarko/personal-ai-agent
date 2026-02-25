import uuid
from typing import AsyncGenerator

from app.agents.base import BaseAgent
from app.llm.prompts.system import EIT_SYSTEM_PROMPT
from app.tools.url_scraper import URLInput
from app.tools.pdf_reader import PDFInput
from app.core.events import RunStartedEvent, RunCompletedEvent, RunFailedEvent
from app.core.exceptions import ToolError
from app.schemas.agent import RunRequest


SUMMARIZE_TEMPLATE = """
Please summarise the following content:

---
{content}
---
""".strip()


class SummarizerAgent(BaseAgent):
    """
    Concrete agent — handles URL and PDF summarization.
    Selects the correct tool, builds the prompt with EIT persona,
    then streams the response from the LLM.
    """

    async def run(self, request: RunRequest) -> AsyncGenerator[str, None]:
        run_id = str(uuid.uuid4())

        await self._bus.publish(RunStartedEvent(
            run_id=run_id,
            tool="url_scraper" if request.url else "pdf_reader",
        ))

        try:
            # ── Step 1: extract content via the correct tool ──────────────
            content = await self._extract_content(request)

            # ── Step 2: build messages with EIT persona ───────────────────
            messages = [
                {"role": "system", "content": EIT_SYSTEM_PROMPT},
                {"role": "user",   "content": SUMMARIZE_TEMPLATE.format(content=content)},
            ]

            # ── Step 3: stream LLM response ───────────────────────────────
            token_count = 0
            async for chunk in self._llm.stream(messages):
                token_count += 1
                yield chunk

            await self._bus.publish(RunCompletedEvent(
                run_id=run_id,
                tokens_used=token_count,
            ))

        except ToolError as e:
            await self._bus.publish(RunFailedEvent(
                run_id=run_id,
                error=e.message,
                code=e.code,
            ))
            raise

        except Exception as e:
            await self._bus.publish(RunFailedEvent(
                run_id=run_id,
                error=str(e),
                code="UNEXPECTED_ERROR",
            ))
            raise

    async def _extract_content(self, request: RunRequest) -> str:
        if request.url:
            result = await self._registry.execute(
                "url_scraper",
                URLInput(url=request.url),
            )
        elif request.file:
            result = await self._registry.execute(
                "pdf_reader",
                PDFInput(file=request.file),
            )
        else:
            raise ValueError("RunRequest must have either a url or a file.")

        return result.content
"""PM Agent – Product Manager agent that converts a natural-language requirement
into a structured project breakdown with user stories."""

from __future__ import annotations

import json
import re
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from config.llm_config import llm_pm
from tools.llm_helpers import clean_llm_response


# ── Pydantic output models ──────────────────────────────────────────────────

class UserStory(BaseModel):
    id: str = Field(..., description="Unique ID in the format US-001, US-002, etc.")
    title: str = Field(..., description="Short descriptive title for the user story")
    description: str = Field(
        ...,
        description='User story in the format "Como X, quiero Y, para Z"',
    )
    acceptance_criteria: list[str] = Field(
        ..., description="List of acceptance criteria"
    )
    priority: Literal["high", "medium", "low"] = Field(
        ..., description="Priority level"
    )
    estimated_points: int = Field(
        ..., description="Story points using Fibonacci scale (1, 2, 3, 5, 8, 13)"
    )


class PMOutput(BaseModel):
    project_name: str = Field(..., description="Name for the project")
    summary: str = Field(..., description="High-level project summary")
    user_stories: list[UserStory] = Field(
        ..., description="List of user stories derived from the requirement"
    )


# ── System prompt ────────────────────────────────────────────────────────────

PM_SYSTEM_PROMPT = """\
You are an expert Product Manager in agile software development.

Your task is to receive a natural language requirement and generate a structured project document with user stories.

STRICT RULES:
1. Respond ONLY with a valid JSON. Do NOT include explanatory text, comments, or markdown code blocks (```).
2. The JSON must follow EXACTLY this schema:

{{
  "project_name": "string",
  "summary": "string",
  "user_stories": [
    {{
      "id": "US-001",
      "title": "string",
      "description": "As a [user type], I want [action], so that [benefit]",
      "acceptance_criteria": ["criterion 1", "criterion 2"],
      "priority": "high" | "medium" | "low",
      "estimated_points": 1 | 2 | 3 | 5 | 8 | 13
    }}
  ]
}}

3. Generate between 5 and 10 relevant user stories.
4. IDs must be sequential: US-001, US-002, US-003…
5. Descriptions must use the format: "As a [user], I want [functionality], so that [benefit]"
6. Estimated points must use the Fibonacci scale: 1, 2, 3, 5, 8, 13.
7. Assign priorities realistically (not all "high").
8. Do NOT use backticks, do NOT use markdown, ONLY pure JSON.
"""


# ── Agent class ──────────────────────────────────────────────────────────────

class PMAgent:
    """Wraps a ChatOpenAI call with structured JSON parsing."""

    def __init__(self) -> None:
        self.llm = llm_pm

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _clean_response(text: str) -> str:
        """Strip markdown code fences and surrounding whitespace."""
        # Remove ```json ... ``` or ``` ... ```
        cleaned = re.sub(r"```(?:json)?\s*", "", text)
        cleaned = re.sub(r"```", "", cleaned)
        return cleaned.strip()

    # ── public API ───────────────────────────────────────────────────────

    def run(self, requirement: str) -> PMOutput:
        """Send the requirement to the LLM and parse its JSON response."""
        messages = [
            SystemMessage(content=PM_SYSTEM_PROMPT),
            HumanMessage(content=f"Requirement:\n{requirement}"),
        ]

        response = self.llm.invoke(messages)
        raw_text: str = response.content  # type: ignore[assignment]

        cleaned = clean_llm_response(raw_text)

        data = json.loads(cleaned, strict=False)
        return PMOutput.model_validate(data)

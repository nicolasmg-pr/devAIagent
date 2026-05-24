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
Eres un Product Manager experto en desarrollo de software ágil.

Tu tarea es recibir un requerimiento en lenguaje natural y generar un documento \
estructurado de proyecto con historias de usuario.

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con un JSON válido. NO incluyas texto explicativo, \
comentarios, ni bloques markdown (```).
2. El JSON debe seguir EXACTAMENTE este esquema:

{{
  "project_name": "string",
  "summary": "string",
  "user_stories": [
    {{
      "id": "US-001",
      "title": "string",
      "description": "Como [tipo de usuario], quiero [acción], para [beneficio]",
      "acceptance_criteria": ["criterio 1", "criterio 2"],
      "priority": "high" | "medium" | "low",
      "estimated_points": 1 | 2 | 3 | 5 | 8 | 13
    }}
  ]
}}

3. Genera entre 5 y 10 historias de usuario relevantes.
4. Los IDs deben ser secuenciales: US-001, US-002, US-003…
5. Las descripciones deben usar el formato: "Como [usuario], quiero [funcionalidad], para [beneficio]"
6. Los puntos estimados deben usar la escala Fibonacci: 1, 2, 3, 5, 8, 13.
7. Asigna prioridades de forma realista (no todas "high").
8. NO uses backticks, NO uses markdown, SOLO JSON puro.
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
            HumanMessage(content=f"Requerimiento:\n{requirement}"),
        ]

        response = self.llm.invoke(messages)
        raw_text: str = response.content  # type: ignore[assignment]

        cleaned = clean_llm_response(raw_text)

        data = json.loads(cleaned, strict=False)
        return PMOutput.model_validate(data)

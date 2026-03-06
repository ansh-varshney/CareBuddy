"""Triage module — urgency assessment and symptom extraction."""

import json
import logging
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.core.prompts import TRIAGE_PROMPT, SYMPTOM_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)
settings = get_settings()


class TriageResult:
    """Structured triage assessment result."""

    def __init__(
        self,
        symptoms: list[str],
        urgency_level: int,
        urgency_reasoning: str,
        recommended_action: str,
        specialist_type: Optional[str],
        follow_up_questions: list[str],
        key_concerns: list[str],
    ):
        self.symptoms = symptoms
        self.urgency_level = urgency_level
        self.urgency_reasoning = urgency_reasoning
        self.recommended_action = recommended_action
        self.specialist_type = specialist_type
        self.follow_up_questions = follow_up_questions
        self.key_concerns = key_concerns

    def to_dict(self) -> dict:
        return {
            "symptoms_identified": self.symptoms,
            "urgency_level": self.urgency_level,
            "urgency_reasoning": self.urgency_reasoning,
            "recommended_action": self.recommended_action,
            "specialist_type": self.specialist_type,
            "follow_up_questions": self.follow_up_questions,
            "key_concerns": self.key_concerns,
        }


async def assess_triage(
    conversation_text: str, model: Optional[str] = None
) -> Optional[TriageResult]:
    """
    Analyze a conversation and produce a structured triage assessment.

    Args:
        conversation_text: The full conversation text to analyze
        model: Ollama model to use (defaults to config)

    Returns:
        TriageResult or None if parsing fails
    """
    try:
        llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=model or settings.DEFAULT_MODEL,
            temperature=0.1,  # Low temperature for consistent structured output
        )

        prompt = TRIAGE_PROMPT.format(conversation=conversation_text)
        messages = [
            SystemMessage(content="You are a medical triage assistant. Respond only with valid JSON."),
            HumanMessage(content=prompt),
        ]

        response = await llm.ainvoke(messages)
        content = response.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        data = json.loads(content)

        return TriageResult(
            symptoms=data.get("symptoms_identified", []),
            urgency_level=min(max(data.get("urgency_level", 1), 1), 5),
            urgency_reasoning=data.get("urgency_reasoning", ""),
            recommended_action=data.get("recommended_action", "schedule-appointment"),
            specialist_type=data.get("specialist_type"),
            follow_up_questions=data.get("follow_up_questions", []),
            key_concerns=data.get("key_concerns", []),
        )

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse triage response: {e}")
        return None
    except Exception as e:
        logger.error(f"Triage assessment error: {e}")
        return None


async def extract_symptoms(message: str, model: Optional[str] = None) -> list[str]:
    """
    Extract symptom keywords from a user message.

    Returns:
        List of symptom strings, or empty list on failure
    """
    try:
        llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=model or settings.DEFAULT_MODEL,
            temperature=0.0,
        )

        prompt = SYMPTOM_EXTRACTION_PROMPT.format(message=message)
        messages = [HumanMessage(content=prompt)]
        response = await llm.ainvoke(messages)
        content = response.content.strip()

        # Extract JSON array
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        symptoms = json.loads(content)
        return symptoms if isinstance(symptoms, list) else []

    except Exception as e:
        logger.warning(f"Symptom extraction failed: {e}")
        return []

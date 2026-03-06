"""Tests for the triage assessment module."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.triage import assess_triage, TriageResult


MOCK_TRIAGE_JSON = """{
    "symptoms_identified": ["fever", "cough"],
    "urgency_level": 3,
    "urgency_reasoning": "Symptoms present for 3 days",
    "recommended_action": "schedule-appointment",
    "specialist_type": "general-practitioner",
    "follow_up_questions": ["How long have you had these symptoms?"],
    "key_concerns": ["Possible respiratory infection"]
}"""


@pytest.mark.asyncio
async def test_triage_returns_result():
    with patch("app.core.triage.ChatOllama") as mock_llm_class:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = MOCK_TRIAGE_JSON
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm_class.return_value = mock_instance

        result = await assess_triage("I have been having fever and cough for 3 days")
        assert result is not None
        assert isinstance(result.urgency_level, int)
        assert 1 <= result.urgency_level <= 5
        assert result.recommended_action == "schedule-appointment"


@pytest.mark.asyncio
async def test_triage_returns_none_on_failure():
    with patch("app.core.triage.ChatOllama") as mock_llm_class:
        mock_instance = MagicMock()
        mock_instance.ainvoke = AsyncMock(side_effect=Exception("Ollama not available"))
        mock_llm_class.return_value = mock_instance

        result = await assess_triage("I have a headache")
        assert result is None


def test_triage_result_to_dict():
    result = TriageResult(
        symptoms=["headache", "fever"],
        urgency_level=3,
        urgency_reasoning="Moderate symptoms",
        recommended_action="schedule-appointment",
        specialist_type="general-practitioner",
        follow_up_questions=["How long have you had these?"],
        key_concerns=["Possible infection"],
    )
    d = result.to_dict()
    assert d["urgency_level"] == 3
    assert d["recommended_action"] == "schedule-appointment"
    assert d["symptoms_identified"] == ["headache", "fever"]

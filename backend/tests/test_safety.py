"""Tests for the safety guardrails module — no LLM calls needed."""

import pytest
from app.core.safety import check_safety, add_disclaimer, MEDICAL_DISCLAIMER


# ── Emergency detection ──────────────────────────────────────────

@pytest.mark.parametrize("message", [
    "I have severe chest pain and can't breathe",
    "I think I'm having a heart attack",
    "He is unconscious and unresponsive",
    "I am having a seizure",
    "severe allergic reaction I can't breathe",
    "I overdosed on pills",
])
def test_emergency_messages_flagged(message):
    is_safe, override, urgency = check_safety(message)
    assert not is_safe
    assert override is not None
    assert urgency == 5
    assert "911" in override or "108" in override or "EMERGENCY" in override


# ── Mental health crisis detection ───────────────────────────────

@pytest.mark.parametrize("message", [
    "I want to kill myself",
    "I want to end my life",
    "I've been hurting myself",
    "I'm thinking about suicide",
])
def test_crisis_messages_flagged(message):
    is_safe, override, urgency = check_safety(message)
    assert not is_safe
    assert override is not None
    assert urgency == 5
    assert "988" in override or "crisis" in override.lower()


# ── High urgency (non-emergency) ─────────────────────────────────

@pytest.mark.parametrize("message", [
    "I have a high fever and it won't go down",
    "there is blood in my stool",
    "I have sudden severe headache the worst of my life",
    "I have severe pain in my abdomen",
])
def test_high_urgency_messages_still_safe(message):
    is_safe, override, urgency = check_safety(message)
    assert is_safe          # LLM still responds
    assert override is None
    assert urgency == 4


# ── Normal messages — no concern ─────────────────────────────────

@pytest.mark.parametrize("message", [
    "I have a mild cold and runny nose",
    "How much water should I drink daily?",
    "What foods help with digestion?",
    "I have a slight headache",
    "My knee is a bit sore after jogging",
])
def test_normal_messages_pass(message):
    is_safe, override, urgency = check_safety(message)
    assert is_safe
    assert override is None
    assert urgency == 0


# ── Disclaimer ───────────────────────────────────────────────────

def test_disclaimer_added_when_absent():
    result = add_disclaimer("Here is some health advice.")
    assert "Disclaimer" in result
    assert MEDICAL_DISCLAIMER in result


def test_disclaimer_not_duplicated():
    text = "Some advice." + MEDICAL_DISCLAIMER
    result = add_disclaimer(text)
    assert result.count("Disclaimer") == 1

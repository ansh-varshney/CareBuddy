"""Clinical safety guardrails for detecting high-risk scenarios."""

import re
from typing import Tuple

# ── Emergency keyword patterns ──────────────────────────────────
EMERGENCY_PATTERNS = [
    r"\b(chest\s+pain|heart\s+attack)\b",
    r"\b(can'?t\s+breathe|difficulty\s+breathing|shortness\s+of\s+breath)\b",
    r"\b(stroke|face\s+drooping|arm\s+weakness|speech\s+difficulty)\b",
    r"\b(severe\s+bleeding|uncontrolled\s+bleeding)\b",
    r"\b(unconscious|passed\s+out|unresponsive)\b",
    r"\b(seizure|convulsion)\b",
    r"\b(anaphylax|severe\s+allergic)\b",
    r"\b(suicid\w*|self[- ]?harm|kill\s+(myself|me)|end\s+my\s+life|want\s+to\s+die)\b",
    r"\b(overdos\w*|took\s+too\s+many\s+(pills|medication))\b",
    r"\b(poison\w*|swallowed|ingested)\b",
    r"\b(severe\s+head\s+injury|head\s+trauma)\b",
    r"\b(choking|can'?t\s+swallow)\b",
]

# ── High urgency patterns (not emergency, but seek care soon) ───
HIGH_URGENCY_PATTERNS = [
    r"\b(high\s+fever|fever\s+over\s+10[3-9]|fever\s+over\s+39)\b",
    r"\bblood\s+in\b.{0,10}\b(urine|stool|vomit)\b",
    r"\b(severe\s+pain)\b",
    r"\b(sudden\s+vision\s+(loss|change))\b",
    r"\b(persistent\s+vomiting)\b",
    r"\b(severe\s+headache|worst\s+headache)\b",
    r"\b(numbness|tingling).*(face|arm|leg)\b",
    r"\b(confusion|disoriented|altered\s+mental)\b",
]

# ── Mental health crisis patterns ───────────────────────────────
CRISIS_PATTERNS = [
    r"\b(suicid\w*|self[- ]?harm|kill\s+(myself|me)|end\s+my\s+life)\b",
    r"\b(want\s+to\s+die|better\s+off\s+dead|no\s+reason\s+to\s+live)\b",
    r"\b(hurting\s+myself|cutting\s+myself)\b",
]

EMERGENCY_RESPONSE = """
🚨 **EMERGENCY — SEEK IMMEDIATE HELP**

Based on what you've described, this could be a **medical emergency**.

**Please take these steps immediately:**
1. **Call emergency services: 911 (US) / 112 (EU) / 999 (UK) / 108 (India)**
2. If someone is with you, ask them to help
3. Do not drive yourself — wait for emergency services

⚠️ *I am an AI assistant and cannot provide emergency medical care. \
Please contact emergency services right away.*
"""

CRISIS_RESPONSE = """
💙 **I hear you, and I want you to know that help is available.**

**Please reach out to a crisis helpline right now:**
- 🇺🇸 **988 Suicide & Crisis Lifeline**: Call or text **988**
- 🇮🇳 **iCall**: **9152987821** | **Vandrevala Foundation**: **1860 2662 345**
- 🇬🇧 **Samaritans**: **116 123**
- 🌍 **International**: https://findahelpline.com/

You are not alone. These services are free, confidential, and available 24/7.

*If you are in immediate danger, please call emergency services.*
"""

MEDICAL_DISCLAIMER = (
    "\n\n---\n*⚕️ Disclaimer: I am an AI health assistant, not a medical professional. "
    "This information is for educational purposes only and should not replace "
    "professional medical advice. Please consult a qualified healthcare provider "
    "for diagnosis and treatment.*"
)


def check_safety(message: str) -> Tuple[bool, str | None, int]:
    """
    Check a user message for safety concerns.

    Returns:
        Tuple of (is_safe, override_response, urgency_level)
        - is_safe: False if an emergency/crisis override is needed
        - override_response: The response to send instead of LLM output (or None)
        - urgency_level: Assessed urgency (5=emergency, 4=high, 0=no concern)
    """
    message_lower = message.lower()

    # Check for mental health crisis FIRST (highest priority)
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, message_lower):
            return False, CRISIS_RESPONSE, 5

    # Check for medical emergencies
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, message_lower):
            return False, EMERGENCY_RESPONSE, 5

    # Check for high urgency
    for pattern in HIGH_URGENCY_PATTERNS:
        if re.search(pattern, message_lower):
            return True, None, 4  # Safe to proceed but flag as high urgency

    return True, None, 0


def add_disclaimer(response: str) -> str:
    """Append medical disclaimer to a response if not already present."""
    if "Disclaimer" not in response:
        return response + MEDICAL_DISCLAIMER
    return response

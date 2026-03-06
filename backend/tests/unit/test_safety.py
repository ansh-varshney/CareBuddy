"""Tests for the safety guardrails module."""

from app.core.safety import check_safety, add_disclaimer, MEDICAL_DISCLAIMER


class TestCheckSafety:
    """Test the safety check function."""

    def test_normal_message_is_safe(self):
        """Normal health queries should be marked safe."""
        is_safe, override, urgency = check_safety("I have a mild headache")
        assert is_safe is True
        assert override is None
        assert urgency == 0

    def test_emergency_chest_pain(self):
        """Chest pain should trigger emergency response."""
        is_safe, override, urgency = check_safety("I'm having severe chest pain")
        assert is_safe is False
        assert override is not None
        assert urgency == 5
        assert "EMERGENCY" in override or "emergency" in override.lower()

    def test_emergency_cant_breathe(self):
        """Breathing difficulty should trigger emergency response."""
        is_safe, override, urgency = check_safety("I can't breathe properly")
        assert is_safe is False
        assert urgency == 5

    def test_crisis_suicidal(self):
        """Suicidal mentions should trigger crisis response."""
        is_safe, override, urgency = check_safety("I want to kill myself")
        assert is_safe is False
        assert override is not None
        assert urgency == 5
        assert "988" in override or "crisis" in override.lower()

    def test_crisis_self_harm(self):
        """Self-harm mentions should trigger crisis response."""
        is_safe, override, urgency = check_safety("I've been hurting myself")
        assert is_safe is False
        assert urgency == 5

    def test_high_urgency_blood_in_stool(self):
        """Blood in stool should flag high urgency but still be safe to proceed."""
        is_safe, override, urgency = check_safety("There is blood in my stool")
        assert is_safe is True
        assert override is None
        assert urgency == 4

    def test_high_urgency_severe_pain(self):
        """Severe pain should flag high urgency."""
        is_safe, override, urgency = check_safety("I have severe pain in my abdomen")
        assert is_safe is True
        assert urgency == 4

    def test_normal_cold_symptoms(self):
        """Common cold symptoms should not trigger anything."""
        is_safe, override, urgency = check_safety(
            "I have a runny nose and mild sore throat"
        )
        assert is_safe is True
        assert urgency == 0

    def test_case_insensitive(self):
        """Safety checks should be case-insensitive."""
        is_safe, override, urgency = check_safety("I'M HAVING A HEART ATTACK")
        assert is_safe is False
        assert urgency == 5


class TestAddDisclaimer:
    """Test the disclaimer adding function."""

    def test_adds_disclaimer(self):
        """Should add disclaimer to responses without one."""
        response = "You should rest and drink fluids."
        result = add_disclaimer(response)
        assert "Disclaimer" in result

    def test_no_double_disclaimer(self):
        """Should not add disclaimer if already present."""
        response = f"Some response {MEDICAL_DISCLAIMER}"
        result = add_disclaimer(response)
        assert result.count("Disclaimer") == 1

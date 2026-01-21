"""
Tests for phase management and transitions.
"""

import pytest
from datetime import datetime

from robby.phases import Phase, PhaseTransition, PhaseTransitionError


def test_phase_order():
    """Test that phases follow the correct order."""
    assert Phase.INTAKE.next_phase() == Phase.SCOPE_LOCK
    assert Phase.SCOPE_LOCK.next_phase() == Phase.PLAN
    assert Phase.PLAN.next_phase() == Phase.EXECUTE
    assert Phase.EXECUTE.next_phase() == Phase.PROVE
    assert Phase.PROVE.next_phase() == Phase.HANDOFF
    assert Phase.HANDOFF.next_phase() == Phase.SHIP
    assert Phase.SHIP.next_phase() is None


def test_final_phase():
    """Test final phase detection."""
    assert not Phase.INTAKE.is_final_phase()
    assert not Phase.EXECUTE.is_final_phase()
    assert Phase.SHIP.is_final_phase()


def test_valid_transition_from_none():
    """Test that first transition must be to INTAKE."""
    transition = PhaseTransition(
        from_phase=None,
        to_phase=Phase.INTAKE,
        timestamp=datetime.utcnow(),
        reason="Starting session",
    )
    assert transition.is_valid()
    transition.validate()  # Should not raise


def test_invalid_transition_from_none():
    """Test that first transition to non-INTAKE phase is invalid."""
    transition = PhaseTransition(
        from_phase=None,
        to_phase=Phase.EXECUTE,
        timestamp=datetime.utcnow(),
        reason="Invalid start",
    )
    assert not transition.is_valid()
    
    with pytest.raises(PhaseTransitionError) as exc_info:
        transition.validate()
    assert "Invalid phase transition" in str(exc_info.value)


def test_valid_sequential_transition():
    """Test valid sequential phase transitions."""
    transition = PhaseTransition(
        from_phase=Phase.INTAKE,
        to_phase=Phase.SCOPE_LOCK,
        timestamp=datetime.utcnow(),
        reason="Intake complete",
    )
    assert transition.is_valid()
    transition.validate()


def test_invalid_skip_phase():
    """Test that skipping phases is not allowed."""
    transition = PhaseTransition(
        from_phase=Phase.INTAKE,
        to_phase=Phase.EXECUTE,
        timestamp=datetime.utcnow(),
        reason="Trying to skip",
    )
    assert not transition.is_valid()
    
    with pytest.raises(PhaseTransitionError) as exc_info:
        transition.validate()
    assert "Invalid phase transition" in str(exc_info.value)
    assert "INTAKE → EXECUTE" in str(exc_info.value)


def test_invalid_backward_transition():
    """Test that backward transitions are not allowed."""
    transition = PhaseTransition(
        from_phase=Phase.EXECUTE,
        to_phase=Phase.PLAN,
        timestamp=datetime.utcnow(),
        reason="Trying to go back",
    )
    assert not transition.is_valid()
    
    with pytest.raises(PhaseTransitionError):
        transition.validate()


def test_complete_lifecycle():
    """Test a complete valid lifecycle transition sequence."""
    phases = [
        (None, Phase.INTAKE),
        (Phase.INTAKE, Phase.SCOPE_LOCK),
        (Phase.SCOPE_LOCK, Phase.PLAN),
        (Phase.PLAN, Phase.EXECUTE),
        (Phase.EXECUTE, Phase.PROVE),
        (Phase.PROVE, Phase.HANDOFF),
        (Phase.HANDOFF, Phase.SHIP),
    ]
    
    for from_phase, to_phase in phases:
        transition = PhaseTransition(
            from_phase=from_phase,
            to_phase=to_phase,
            timestamp=datetime.utcnow(),
            reason=f"Moving to {to_phase.value}",
        )
        assert transition.is_valid()
        transition.validate()

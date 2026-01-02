"""
Tests for Work Session and SessionManager.
"""

import pytest

from robby.session import WorkSession, SessionManager, Blocker
from robby.phases import Phase, PhaseTransitionError


def test_create_session():
    """Test creating a new Work Session."""
    manager = SessionManager()
    session = manager.create_session(metadata={"user": "test"})
    
    assert session.session_id
    assert session.current_phase == Phase.INTAKE
    assert len(session.phase_history) == 1
    assert session.phase_history[0].to_phase == Phase.INTAKE
    assert session.metadata["user"] == "test"


def test_get_session():
    """Test retrieving a session."""
    manager = SessionManager()
    session = manager.create_session()
    
    retrieved = manager.get_session(session.session_id)
    assert retrieved == session
    
    not_found = manager.get_session("nonexistent")
    assert not_found is None


def test_advance_phase_success():
    """Test successfully advancing through phases."""
    manager = SessionManager()
    session = manager.create_session()
    
    # INTAKE -> SCOPE_LOCK
    session = manager.advance_phase(session.session_id, "Intake complete")
    assert session.current_phase == Phase.SCOPE_LOCK
    assert len(session.phase_history) == 2
    
    # SCOPE_LOCK -> PLAN
    session = manager.advance_phase(session.session_id, "Scope locked")
    assert session.current_phase == Phase.PLAN
    assert len(session.phase_history) == 3


def test_advance_phase_with_blocker():
    """Test that advancing phase is blocked when there are active blockers."""
    manager = SessionManager()
    session = manager.create_session()
    
    # Add a blocker
    manager.add_blocker(session.session_id, "Missing requirements")
    
    # Try to advance - should fail
    with pytest.raises(PhaseTransitionError) as exc_info:
        manager.advance_phase(session.session_id, "Try to advance")
    assert "active blocker" in str(exc_info.value)


def test_advance_phase_requires_approved_plan():
    """Test that PLAN phase requires approved plan before advancing."""
    manager = SessionManager()
    session = manager.create_session()
    
    # Advance to PLAN phase
    manager.advance_phase(session.session_id, "Intake complete")
    manager.advance_phase(session.session_id, "Scope locked")
    
    assert session.current_phase == Phase.PLAN
    
    # Try to advance without approved plan
    with pytest.raises(PhaseTransitionError) as exc_info:
        manager.advance_phase(session.session_id, "Try to execute")
    assert "without approved plan" in str(exc_info.value)
    
    # Approve plan and advance
    manager.approve_plan(session.session_id, "1. Do this\n2. Do that")
    session = manager.advance_phase(session.session_id, "Plan approved")
    assert session.current_phase == Phase.EXECUTE


def test_advance_phase_requires_truthserum():
    """Test that PROVE phase requires TruthSerum receipts before advancing."""
    manager = SessionManager()
    session = manager.create_session()
    
    # Advance through phases to PROVE
    manager.advance_phase(session.session_id, "Intake complete")
    manager.advance_phase(session.session_id, "Scope locked")
    manager.approve_plan(session.session_id, "Test plan")
    manager.advance_phase(session.session_id, "Plan approved")
    manager.advance_phase(session.session_id, "Execution complete")
    
    assert session.current_phase == Phase.PROVE
    
    # Try to advance without TruthSerum receipts
    with pytest.raises(PhaseTransitionError) as exc_info:
        manager.advance_phase(session.session_id, "Try to handoff")
    assert "TruthSerum receipts" in str(exc_info.value)
    
    # Add verified receipt and advance
    manager.add_truthserum_receipt(
        session.session_id,
        "test_verification",
        True,
        {"test": "passed"},
        "test_verifier",
    )
    session = manager.advance_phase(session.session_id, "Verification complete")
    assert session.current_phase == Phase.HANDOFF


def test_blocker_lifecycle():
    """Test adding and resolving blockers."""
    manager = SessionManager()
    session = manager.create_session()
    
    # Add blocker
    blocker = manager.add_blocker(session.session_id, "Need clarification")
    assert blocker.description == "Need clarification"
    assert blocker.phase == Phase.INTAKE
    assert not blocker.resolved
    
    # Check active blockers
    session = manager.get_session(session.session_id)
    assert session.has_active_blockers()
    assert len(session.get_active_blockers()) == 1
    
    # Resolve blocker
    resolved = manager.resolve_blocker(
        session.session_id,
        blocker.blocker_id,
        "Clarification received",
    )
    assert resolved
    
    # Check no active blockers
    session = manager.get_session(session.session_id)
    assert not session.has_active_blockers()
    assert len(session.get_active_blockers()) == 0


def test_approved_plan():
    """Test approved plan management."""
    session = WorkSession()
    
    # Initially no plan
    assert not session.has_approved_plan()
    
    # Cannot set plan outside PLAN phase
    with pytest.raises(ValueError):
        session.set_approved_plan("Some plan")
    
    # Set to PLAN phase and add plan
    session.current_phase = Phase.PLAN
    session.set_approved_plan("Approved execution plan")
    assert session.has_approved_plan()
    assert session.approved_plan == "Approved execution plan"


def test_next_action():
    """Test next action determination."""
    session = WorkSession()
    
    # INTAKE phase
    assert "SCOPE_LOCK" in session.get_next_action()
    
    # With blocker
    session.add_blocker("Test blocker")
    assert "Resolve" in session.get_next_action()
    assert "blocker" in session.get_next_action()
    
    # Resolve and move to PLAN
    session.blockers[0].resolved = True
    session.current_phase = Phase.PLAN
    assert "approve plan" in session.get_next_action().lower()
    
    # With approved plan
    session.approved_plan = "Test plan"
    assert "EXECUTE" in session.get_next_action()
    
    # Final phase
    session.current_phase = Phase.SHIP
    assert "complete" in session.get_next_action().lower()


def test_session_status():
    """Test comprehensive session status reporting."""
    manager = SessionManager()
    session = manager.create_session()
    
    status = manager.get_session_status(session.session_id)
    
    assert status["session_id"] == session.session_id
    assert status["current_phase"] == "INTAKE"
    assert status["next_phase"] == "SCOPE_LOCK"
    assert status["blocker_count"] == 0
    assert not status["has_approved_plan"]
    assert "next_action" in status
    assert len(status["phase_history"]) == 1


def test_complete_lifecycle():
    """Test complete Work Session lifecycle."""
    manager = SessionManager()
    session = manager.create_session()
    
    # INTAKE -> SCOPE_LOCK
    session = manager.advance_phase(session.session_id, "Intake complete")
    assert session.current_phase == Phase.SCOPE_LOCK
    
    # SCOPE_LOCK -> PLAN
    session = manager.advance_phase(session.session_id, "Scope locked")
    assert session.current_phase == Phase.PLAN
    
    # Approve plan
    manager.approve_plan(session.session_id, "Complete execution plan")
    
    # PLAN -> EXECUTE
    session = manager.advance_phase(session.session_id, "Plan approved")
    assert session.current_phase == Phase.EXECUTE
    
    # EXECUTE -> PROVE
    session = manager.advance_phase(session.session_id, "Execution complete")
    assert session.current_phase == Phase.PROVE
    
    # Add TruthSerum receipt
    manager.add_truthserum_receipt(
        session.session_id,
        "execution_verification",
        True,
        {"status": "passed"},
        "automated_verifier",
    )
    
    # PROVE -> HANDOFF
    session = manager.advance_phase(session.session_id, "Verification complete")
    assert session.current_phase == Phase.HANDOFF
    
    # HANDOFF -> SHIP
    session = manager.advance_phase(session.session_id, "Handoff complete")
    assert session.current_phase == Phase.SHIP
    
    # Verify complete history
    assert len(session.phase_history) == 7
    
    # Try to advance from SHIP (should fail)
    with pytest.raises(PhaseTransitionError):
        manager.advance_phase(session.session_id, "Try to go beyond")


def test_audit_events():
    """Test that audit events are emitted."""
    manager = SessionManager()
    session = manager.create_session()
    
    emitter = manager.get_event_emitter()
    
    # Check initial event
    events = emitter.get_events(session.session_id)
    assert len(events) == 1
    assert events[0].event_type == "PHASE_TRANSITION"
    assert events[0].phase == Phase.INTAKE
    
    # Advance phase
    manager.advance_phase(session.session_id, "Test advance")
    events = emitter.get_events(session.session_id)
    assert len(events) == 2
    
    # Add blocker
    manager.add_blocker(session.session_id, "Test blocker")
    events = emitter.get_events(session.session_id)
    assert len(events) == 3
    assert events[2].event_type == "BLOCKER"


def test_session_persistence():
    """Test session serialization to dictionary."""
    manager = SessionManager()
    session = manager.create_session(metadata={"project": "test"})
    blocker = manager.add_blocker(session.session_id, "Test blocker")
    manager.resolve_blocker(session.session_id, blocker.blocker_id, "Resolved")
    manager.advance_phase(session.session_id, "Progress")
    
    session_dict = session.to_dict()
    
    assert session_dict["session_id"] == session.session_id
    assert session_dict["current_phase"] == "SCOPE_LOCK"
    assert len(session_dict["phase_history"]) == 2
    assert len(session_dict["blockers"]) == 1
    assert session_dict["metadata"]["project"] == "test"

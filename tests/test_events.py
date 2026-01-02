"""
Tests for audit event system.
"""

import pytest

from robby.events import AuditEvent, EventEmitter
from robby.phases import Phase


def test_create_audit_event():
    """Test creating an audit event."""
    event = AuditEvent(
        session_id="test-session",
        event_type="TEST_EVENT",
        phase=Phase.INTAKE,
        metadata={"key": "value"},
    )
    
    assert event.event_id
    assert event.session_id == "test-session"
    assert event.event_type == "TEST_EVENT"
    assert event.phase == Phase.INTAKE
    assert event.metadata["key"] == "value"


def test_emit_event():
    """Test emitting events."""
    emitter = EventEmitter()
    
    event = AuditEvent(
        session_id="test-session",
        event_type="TEST_EVENT",
    )
    
    emitter.emit(event)
    
    events = emitter.get_events()
    assert len(events) == 1
    assert events[0] == event


def test_emit_phase_transition():
    """Test emitting phase transition events."""
    emitter = EventEmitter()
    
    event = emitter.emit_phase_transition(
        session_id="test-session",
        from_phase=Phase.INTAKE,
        to_phase=Phase.SCOPE_LOCK,
        metadata={"reason": "test"},
    )
    
    assert event.event_type == "PHASE_TRANSITION"
    assert event.phase == Phase.SCOPE_LOCK
    assert event.previous_phase == Phase.INTAKE
    assert event.metadata["reason"] == "test"
    
    events = emitter.get_events()
    assert len(events) == 1


def test_emit_blocker():
    """Test emitting blocker events."""
    emitter = EventEmitter()
    
    event = emitter.emit_blocker(
        session_id="test-session",
        phase=Phase.EXECUTE,
        blocker_description="Test blocker",
    )
    
    assert event.event_type == "BLOCKER"
    assert event.phase == Phase.EXECUTE
    assert event.metadata["blocker_description"] == "Test blocker"


def test_emit_execution():
    """Test emitting execution events."""
    emitter = EventEmitter()
    
    event = emitter.emit_execution(
        session_id="test-session",
        phase=Phase.EXECUTE,
        action="test_action",
        metadata={"detail": "test"},
    )
    
    assert event.event_type == "EXECUTION"
    assert event.phase == Phase.EXECUTE
    assert event.metadata["action"] == "test_action"
    assert event.metadata["detail"] == "test"


def test_get_events_by_session():
    """Test filtering events by session."""
    emitter = EventEmitter()
    
    # Emit events for different sessions
    emitter.emit_phase_transition("session-1", None, Phase.INTAKE)
    emitter.emit_phase_transition("session-2", None, Phase.INTAKE)
    emitter.emit_phase_transition("session-1", Phase.INTAKE, Phase.SCOPE_LOCK)
    
    # Get all events
    all_events = emitter.get_events()
    assert len(all_events) == 3
    
    # Get session-1 events
    session1_events = emitter.get_events("session-1")
    assert len(session1_events) == 2
    
    # Get session-2 events
    session2_events = emitter.get_events("session-2")
    assert len(session2_events) == 1


def test_get_events_by_phase():
    """Test filtering events by phase."""
    emitter = EventEmitter()
    
    # Emit events for different phases
    emitter.emit_phase_transition("session-1", None, Phase.INTAKE)
    emitter.emit_phase_transition("session-1", Phase.INTAKE, Phase.SCOPE_LOCK)
    emitter.emit_execution("session-1", Phase.SCOPE_LOCK, "test_action")
    
    # Get INTAKE phase events
    intake_events = emitter.get_events_by_phase(Phase.INTAKE, "session-1")
    assert len(intake_events) == 1
    assert intake_events[0].phase == Phase.INTAKE
    
    # Get SCOPE_LOCK phase events
    scope_events = emitter.get_events_by_phase(Phase.SCOPE_LOCK, "session-1")
    assert len(scope_events) == 2


def test_event_persistence():
    """Test event serialization to dictionary."""
    event = AuditEvent(
        session_id="test-session",
        event_type="TEST_EVENT",
        phase=Phase.EXECUTE,
        previous_phase=Phase.PLAN,
        metadata={"key": "value"},
    )
    
    event_dict = event.to_dict()
    
    assert event_dict["event_id"] == event.event_id
    assert event_dict["session_id"] == "test-session"
    assert event_dict["event_type"] == "TEST_EVENT"
    assert event_dict["phase"] == "EXECUTE"
    assert event_dict["previous_phase"] == "PLAN"
    assert event_dict["metadata"]["key"] == "value"

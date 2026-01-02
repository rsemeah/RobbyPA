"""
Auditable event system for Robby Work Sessions.
Every phase transition emits auditable events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .phases import Phase


@dataclass
class AuditEvent:
    """Auditable event for Work Session activities."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    event_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    phase: Optional[Phase] = None
    previous_phase: Optional[Phase] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for persistence."""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "phase": self.phase.value if self.phase else None,
            "previous_phase": self.previous_phase.value if self.previous_phase else None,
            "metadata": self.metadata,
        }


class EventEmitter:
    """Emits and stores auditable events for Work Sessions."""
    
    def __init__(self):
        self._events: List[AuditEvent] = []
    
    def emit(self, event: AuditEvent) -> None:
        """Emit an auditable event."""
        self._events.append(event)
    
    def emit_phase_transition(
        self,
        session_id: str,
        from_phase: Optional[Phase],
        to_phase: Phase,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Emit a phase transition event."""
        event = AuditEvent(
            session_id=session_id,
            event_type="PHASE_TRANSITION",
            phase=to_phase,
            previous_phase=from_phase,
            metadata=metadata or {},
        )
        self.emit(event)
        return event
    
    def emit_blocker(
        self,
        session_id: str,
        phase: Phase,
        blocker_description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Emit a blocker event."""
        event_metadata = metadata or {}
        event_metadata["blocker_description"] = blocker_description
        
        event = AuditEvent(
            session_id=session_id,
            event_type="BLOCKER",
            phase=phase,
            metadata=event_metadata,
        )
        self.emit(event)
        return event
    
    def emit_execution(
        self,
        session_id: str,
        phase: Phase,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Emit an execution event."""
        event_metadata = metadata or {}
        event_metadata["action"] = action
        
        event = AuditEvent(
            session_id=session_id,
            event_type="EXECUTION",
            phase=phase,
            metadata=event_metadata,
        )
        self.emit(event)
        return event
    
    def get_events(self, session_id: Optional[str] = None) -> List[AuditEvent]:
        """Get all events, optionally filtered by session_id."""
        if session_id:
            return [e for e in self._events if e.session_id == session_id]
        return self._events.copy()
    
    def get_events_by_phase(self, phase: Phase, session_id: Optional[str] = None) -> List[AuditEvent]:
        """Get events for a specific phase."""
        events = self.get_events(session_id)
        return [e for e in events if e.phase == phase]

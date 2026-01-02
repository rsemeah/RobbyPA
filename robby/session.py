"""
Work Session management with strict lifecycle enforcement.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .phases import Phase, PhaseTransition, PhaseTransitionError
from .events import EventEmitter
from .truthserum import TruthSerumValidator, TruthSerumReceipt


@dataclass
class Blocker:
    """Represents a blocker in the Work Session."""
    blocker_id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    phase: Phase = Phase.INTAKE
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution: str = ""


@dataclass
class WorkSession:
    """
    Work Session with strict lifecycle management.
    Phases: INTAKE → SCOPE_LOCK → PLAN → EXECUTE → PROVE → HANDOFF → SHIP
    """
    session_id: str = field(default_factory=lambda: str(uuid4()))
    current_phase: Phase = Phase.INTAKE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    phase_history: List[PhaseTransition] = field(default_factory=list)
    blockers: List[Blocker] = field(default_factory=list)
    approved_plan: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_blocker(self, description: str) -> Blocker:
        """Add a blocker to the current phase."""
        blocker = Blocker(
            description=description,
            phase=self.current_phase,
        )
        self.blockers.append(blocker)
        return blocker
    
    def resolve_blocker(self, blocker_id: str, resolution: str) -> bool:
        """Resolve a blocker."""
        for blocker in self.blockers:
            if blocker.blocker_id == blocker_id:
                blocker.resolved = True
                blocker.resolution = resolution
                return True
        return False
    
    def get_active_blockers(self) -> List[Blocker]:
        """Get all unresolved blockers."""
        return [b for b in self.blockers if not b.resolved]
    
    def has_active_blockers(self) -> bool:
        """Check if there are any unresolved blockers."""
        return len(self.get_active_blockers()) > 0
    
    def set_approved_plan(self, plan: str) -> None:
        """Set the approved plan (only in PLAN phase)."""
        if self.current_phase != Phase.PLAN:
            raise ValueError(f"Can only set approved plan in PLAN phase, currently in {self.current_phase.value}")
        self.approved_plan = plan
    
    def has_approved_plan(self) -> bool:
        """Check if session has an approved plan."""
        return self.approved_plan is not None
    
    def get_next_action(self) -> str:
        """Determine the exact next action based on current phase and state."""
        if self.has_active_blockers():
            blockers = self.get_active_blockers()
            return f"Resolve {len(blockers)} active blocker(s) before proceeding"
        
        if self.current_phase == Phase.INTAKE:
            return "Complete intake and move to SCOPE_LOCK"
        elif self.current_phase == Phase.SCOPE_LOCK:
            return "Lock scope and move to PLAN"
        elif self.current_phase == Phase.PLAN:
            if not self.has_approved_plan():
                return "Create and approve plan before moving to EXECUTE"
            return "Move to EXECUTE phase"
        elif self.current_phase == Phase.EXECUTE:
            if not self.has_approved_plan():
                return "Cannot execute without approved plan"
            return "Execute approved plan and move to PROVE"
        elif self.current_phase == Phase.PROVE:
            return "Verify work with TruthSerum receipts and move to HANDOFF"
        elif self.current_phase == Phase.HANDOFF:
            return "Complete handoff and move to SHIP"
        elif self.current_phase == Phase.SHIP:
            return "Session complete"
        
        return "Unknown state"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for persistence."""
        return {
            "session_id": self.session_id,
            "current_phase": self.current_phase.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "phase_history": [
                {
                    "from_phase": t.from_phase.value if t.from_phase else None,
                    "to_phase": t.to_phase.value,
                    "timestamp": t.timestamp.isoformat(),
                    "reason": t.reason,
                }
                for t in self.phase_history
            ],
            "blockers": [
                {
                    "blocker_id": b.blocker_id,
                    "description": b.description,
                    "phase": b.phase.value,
                    "timestamp": b.timestamp.isoformat(),
                    "resolved": b.resolved,
                    "resolution": b.resolution,
                }
                for b in self.blockers
            ],
            "approved_plan": self.approved_plan,
            "metadata": self.metadata,
        }


class SessionManager:
    """
    Manages Work Sessions with strict phase enforcement at API boundaries.
    """
    
    def __init__(self):
        self._sessions: Dict[str, WorkSession] = {}
        self._event_emitter = EventEmitter()
        self._truthserum_validator = TruthSerumValidator()
    
    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> WorkSession:
        """Create a new Work Session starting at INTAKE phase."""
        session = WorkSession(metadata=metadata or {})
        self._sessions[session.session_id] = session
        
        # Record initial phase
        transition = PhaseTransition(
            from_phase=None,
            to_phase=Phase.INTAKE,
            timestamp=datetime.utcnow(),
            reason="Session created",
        )
        transition.validate()
        session.phase_history.append(transition)
        
        # Emit audit event
        self._event_emitter.emit_phase_transition(
            session_id=session.session_id,
            from_phase=None,
            to_phase=Phase.INTAKE,
            metadata={"reason": "Session created"},
        )
        
        return session
    
    def get_session(self, session_id: str) -> Optional[WorkSession]:
        """Get a Work Session by ID."""
        return self._sessions.get(session_id)
    
    def advance_phase(self, session_id: str, reason: str) -> WorkSession:
        """
        Advance session to next phase with validation.
        Enforces strict phase ordering and checks preconditions.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Check for active blockers
        if session.has_active_blockers():
            raise PhaseTransitionError(
                f"Cannot advance phase: {len(session.get_active_blockers())} active blocker(s)"
            )
        
        # Check special preconditions
        if session.current_phase == Phase.PLAN:
            if not session.has_approved_plan():
                raise PhaseTransitionError(
                    "Cannot advance from PLAN phase without approved plan"
                )
        
        if session.current_phase == Phase.EXECUTE:
            if not session.has_approved_plan():
                raise PhaseTransitionError(
                    "Cannot execute without approved plan"
                )
        
        if session.current_phase == Phase.PROVE:
            # Must have TruthSerum receipts before moving to HANDOFF
            if not self._truthserum_validator.has_verified_receipts(session_id):
                raise PhaseTransitionError(
                    "Cannot advance from PROVE phase without verified TruthSerum receipts"
                )
        
        # Get next phase
        next_phase = session.current_phase.next_phase()
        if not next_phase:
            raise PhaseTransitionError(
                f"Already at final phase: {session.current_phase.value}"
            )
        
        # Create and validate transition
        transition = PhaseTransition(
            from_phase=session.current_phase,
            to_phase=next_phase,
            timestamp=datetime.utcnow(),
            reason=reason,
        )
        transition.validate()
        
        # Update session
        previous_phase = session.current_phase
        session.current_phase = next_phase
        session.updated_at = datetime.utcnow()
        session.phase_history.append(transition)
        
        # Emit audit event
        self._event_emitter.emit_phase_transition(
            session_id=session_id,
            from_phase=previous_phase,
            to_phase=next_phase,
            metadata={"reason": reason},
        )
        
        return session
    
    def add_blocker(self, session_id: str, description: str) -> Blocker:
        """Add a blocker to a session."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        blocker = session.add_blocker(description)
        
        # Emit audit event
        self._event_emitter.emit_blocker(
            session_id=session_id,
            phase=session.current_phase,
            blocker_description=description,
        )
        
        return blocker
    
    def resolve_blocker(self, session_id: str, blocker_id: str, resolution: str) -> bool:
        """Resolve a blocker in a session."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        resolved = session.resolve_blocker(blocker_id, resolution)
        
        if resolved:
            # Emit audit event
            from .events import AuditEvent
            event = AuditEvent(
                session_id=session_id,
                event_type="BLOCKER_RESOLVED",
                phase=session.current_phase,
                metadata={
                    "blocker_id": blocker_id,
                    "resolution": resolution,
                },
            )
            self._event_emitter.emit(event)
        
        return resolved
    
    def approve_plan(self, session_id: str, plan: str) -> WorkSession:
        """Approve a plan for execution."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.set_approved_plan(plan)
        
        # Emit audit event
        self._event_emitter.emit_execution(
            session_id=session_id,
            phase=session.current_phase,
            action="plan_approved",
            metadata={"plan_length": len(plan)},
        )
        
        return session
    
    def add_truthserum_receipt(
        self,
        session_id: str,
        verification_type: str,
        verified: bool,
        verification_data: Dict[str, Any],
        verifier: str,
    ) -> TruthSerumReceipt:
        """Add a TruthSerum receipt for verification."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        receipt = self._truthserum_validator.create_receipt(
            session_id=session_id,
            verification_type=verification_type,
            verified=verified,
            verification_data=verification_data,
            verifier=verifier,
        )
        
        # Emit audit event
        from .events import AuditEvent
        event = AuditEvent(
            session_id=session_id,
            event_type="TRUTHSERUM_RECEIPT",
            phase=session.current_phase,
            metadata={
                "receipt_id": receipt.receipt_id,
                "verification_type": verification_type,
                "verified": verified,
            },
        )
        self._event_emitter.emit(event)
        
        return receipt
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive status report for a session.
        Always reports: current phase, blockers, exact next action.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        active_blockers = session.get_active_blockers()
        receipts = self._truthserum_validator.get_receipts(session_id)
        
        return {
            "session_id": session.session_id,
            "current_phase": session.current_phase.value,
            "next_phase": session.current_phase.next_phase().value if session.current_phase.next_phase() else None,
            "blockers": [
                {
                    "blocker_id": b.blocker_id,
                    "description": b.description,
                    "phase": b.phase.value,
                }
                for b in active_blockers
            ],
            "blocker_count": len(active_blockers),
            "has_approved_plan": session.has_approved_plan(),
            "truthserum_receipts": len(receipts),
            "verified_receipts": len([r for r in receipts if r.verified]),
            "next_action": session.get_next_action(),
            "phase_history": [
                {
                    "from": t.from_phase.value if t.from_phase else None,
                    "to": t.to_phase.value,
                    "timestamp": t.timestamp.isoformat(),
                    "reason": t.reason,
                }
                for t in session.phase_history
            ],
        }
    
    def get_event_emitter(self) -> EventEmitter:
        """Get the event emitter for accessing audit events."""
        return self._event_emitter
    
    def get_truthserum_validator(self) -> TruthSerumValidator:
        """Get the TruthSerum validator."""
        return self._truthserum_validator

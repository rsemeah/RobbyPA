"""
Robby - Autonomous Development Conductor for QuietBuild OS
Manages strict Work Session lifecycle with auditable phase transitions.
"""

__version__ = "0.1.0"

from .session import WorkSession, SessionManager
from .phases import Phase, PhaseTransition
from .events import AuditEvent, EventEmitter

__all__ = [
    "WorkSession",
    "SessionManager",
    "Phase",
    "PhaseTransition",
    "AuditEvent",
    "EventEmitter",
]

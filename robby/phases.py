"""
Phase management for Robby Work Sessions.
Defines the strict lifecycle: INTAKE → SCOPE_LOCK → PLAN → EXECUTE → PROVE → HANDOFF → SHIP
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


class Phase(Enum):
    """Work Session lifecycle phases."""
    INTAKE = "INTAKE"
    SCOPE_LOCK = "SCOPE_LOCK"
    PLAN = "PLAN"
    EXECUTE = "EXECUTE"
    PROVE = "PROVE"
    HANDOFF = "HANDOFF"
    SHIP = "SHIP"

    def next_phase(self) -> Optional["Phase"]:
        """Get the next phase in the lifecycle."""
        phase_order = [
            Phase.INTAKE,
            Phase.SCOPE_LOCK,
            Phase.PLAN,
            Phase.EXECUTE,
            Phase.PROVE,
            Phase.HANDOFF,
            Phase.SHIP,
        ]
        try:
            current_index = phase_order.index(self)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
            return None
        except ValueError:
            return None

    def is_final_phase(self) -> bool:
        """Check if this is the final phase."""
        return self == Phase.SHIP


@dataclass
class PhaseTransition:
    """Represents a phase transition in the Work Session lifecycle."""
    from_phase: Optional[Phase]
    to_phase: Phase
    timestamp: datetime
    reason: str
    validated: bool = True

    def is_valid(self) -> bool:
        """Validate that this transition follows the strict lifecycle."""
        if self.from_phase is None:
            # First transition must be to INTAKE
            return self.to_phase == Phase.INTAKE
        
        # Can only move to the next phase in sequence
        expected_next = self.from_phase.next_phase()
        return self.to_phase == expected_next

    def validate(self) -> None:
        """Validate the transition and raise error if invalid."""
        if not self.is_valid():
            from_name = self.from_phase.value if self.from_phase else "None"
            raise PhaseTransitionError(
                f"Invalid phase transition: {from_name} → {self.to_phase.value}. "
                f"Phases must follow strict order: "
                f"INTAKE → SCOPE_LOCK → PLAN → EXECUTE → PROVE → HANDOFF → SHIP"
            )


class PhaseTransitionError(Exception):
    """Raised when an invalid phase transition is attempted."""
    pass

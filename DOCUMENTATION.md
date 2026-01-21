# Robby - Autonomous Development Conductor for QuietBuild OS

Robby is an autonomous development conductor that manages a strict Work Session lifecycle with auditable phase transitions, enforced boundaries, and verifiable certification.

## Features

### ✅ Strict Lifecycle Management
- **Seven Phases**: INTAKE → SCOPE_LOCK → PLAN → EXECUTE → PROVE → HANDOFF → SHIP
- **No Phase Skipping**: Phases must be followed in exact order
- **Enforced Boundaries**: API-level validation prevents invalid transitions

### 📋 Phase Enforcement
- **Explicit State**: Current phase is always persisted and available
- **Precondition Checks**: Each phase has specific requirements before advancing
- **Blocker Management**: Active blockers prevent phase transitions

### 🔐 TruthSerum Verification
- **Verifiable Receipts**: All work requires verified TruthSerum receipts before certification
- **Multiple Verification Types**: Support for various verification methods (tests, reviews, etc.)
- **Certification Requirements**: PROVE phase requires receipts before advancing

### 📝 Audit Trail
- **Complete Event History**: Every transition emits auditable events
- **Event Types**: Phase transitions, blockers, executions, verifications
- **Timestamped Records**: All events include timestamps and metadata

### 📊 Status Reporting
- **Current Phase**: Always reports the current phase
- **Active Blockers**: Shows all unresolved blockers
- **Next Action**: Determines the exact next action required
- **Phase History**: Complete history of all transitions

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from robby import SessionManager

# Create a session manager
manager = SessionManager()

# Start a new work session
session = manager.create_session(metadata={"project": "My Project"})

# Get current status
status = manager.get_session_status(session.session_id)
print(f"Current Phase: {status['current_phase']}")
print(f"Next Action: {status['next_action']}")

# Advance through phases
manager.advance_phase(session.session_id, "Intake complete")
manager.advance_phase(session.session_id, "Scope locked")

# Approve a plan in PLAN phase
manager.approve_plan(session.session_id, "Detailed execution plan...")

# Continue through lifecycle
manager.advance_phase(session.session_id, "Plan approved")
manager.advance_phase(session.session_id, "Execution complete")

# Add verification receipt in PROVE phase
manager.add_truthserum_receipt(
    session.session_id,
    verification_type="unit_tests",
    verified=True,
    verification_data={"tests_passed": 100, "coverage": 95},
    verifier="pytest",
)

# Complete the lifecycle
manager.advance_phase(session.session_id, "Verification complete")
manager.advance_phase(session.session_id, "Handoff complete")
```

## Phase Lifecycle

### 1. INTAKE
**Purpose**: Gather requirements and initial information  
**Next Action**: Complete intake and move to SCOPE_LOCK  
**Requirements**: None  

### 2. SCOPE_LOCK
**Purpose**: Lock down the scope of work  
**Next Action**: Lock scope and move to PLAN  
**Requirements**: Complete INTAKE phase  

### 3. PLAN
**Purpose**: Create and approve execution plan  
**Next Action**: Create and approve plan before moving to EXECUTE  
**Requirements**: Complete SCOPE_LOCK phase  
**Special**: Must call `approve_plan()` before advancing  

### 4. EXECUTE
**Purpose**: Execute the approved plan  
**Next Action**: Execute approved plan and move to PROVE  
**Requirements**: Approved plan from PLAN phase  
**Enforcement**: Cannot execute without approved plan  

### 5. PROVE
**Purpose**: Verify work with TruthSerum receipts  
**Next Action**: Verify work with TruthSerum receipts and move to HANDOFF  
**Requirements**: Complete EXECUTE phase  
**Special**: Must add verified TruthSerum receipts before advancing  

### 6. HANDOFF
**Purpose**: Hand off completed work  
**Next Action**: Complete handoff and move to SHIP  
**Requirements**: Verified TruthSerum receipts from PROVE phase  

### 7. SHIP
**Purpose**: Final phase - work is shipped  
**Next Action**: Session complete  
**Requirements**: Complete HANDOFF phase  
**Special**: Final phase - no further transitions allowed  

## API Reference

### SessionManager

#### `create_session(metadata: Optional[Dict] = None) -> WorkSession`
Create a new Work Session starting at INTAKE phase.

#### `get_session(session_id: str) -> Optional[WorkSession]`
Retrieve a Work Session by ID.

#### `advance_phase(session_id: str, reason: str) -> WorkSession`
Advance session to the next phase with validation. Enforces:
- No active blockers
- Phase-specific preconditions
- Strict sequential ordering

#### `add_blocker(session_id: str, description: str) -> Blocker`
Add a blocker to the current phase. Blocks phase transitions until resolved.

#### `resolve_blocker(session_id: str, blocker_id: str, resolution: str) -> bool`
Resolve a blocker with explanation.

#### `approve_plan(session_id: str, plan: str) -> WorkSession`
Approve an execution plan (only in PLAN phase).

#### `add_truthserum_receipt(session_id: str, verification_type: str, verified: bool, verification_data: Dict, verifier: str) -> TruthSerumReceipt`
Add a TruthSerum verification receipt.

#### `get_session_status(session_id: str) -> Dict`
Get comprehensive status report including:
- Current phase and next phase
- Active blockers
- Approved plan status
- TruthSerum receipts
- Next action
- Phase history

### WorkSession

The core session object with properties:
- `session_id`: Unique identifier
- `current_phase`: Current Phase enum
- `phase_history`: List of all phase transitions
- `blockers`: List of all blockers (active and resolved)
- `approved_plan`: The approved execution plan (if any)
- `metadata`: Custom metadata dictionary

### Phase Enum

```python
from robby import Phase

Phase.INTAKE
Phase.SCOPE_LOCK
Phase.PLAN
Phase.EXECUTE
Phase.PROVE
Phase.HANDOFF
Phase.SHIP
```

## Blocker Management

Blockers prevent phase transitions and force resolution:

```python
# Add a blocker
blocker = manager.add_blocker(session_id, "Missing requirements")

# Attempt to advance (will fail)
try:
    manager.advance_phase(session_id, "Try to advance")
except PhaseTransitionError as e:
    print(f"Blocked: {e}")

# Resolve blocker
manager.resolve_blocker(session_id, blocker.blocker_id, "Requirements received")

# Now can advance
manager.advance_phase(session_id, "Blocker resolved")
```

## TruthSerum Verification

The PROVE phase requires verified receipts:

```python
# Add verification receipts
manager.add_truthserum_receipt(
    session_id,
    verification_type="unit_tests",
    verified=True,
    verification_data={"tests_passed": 50, "coverage": 90},
    verifier="pytest",
)

manager.add_truthserum_receipt(
    session_id,
    verification_type="code_review",
    verified=True,
    verification_data={"reviewers": ["alice", "bob"], "approved": True},
    verifier="github",
)

# Now can advance from PROVE phase
manager.advance_phase(session_id, "Verification complete")
```

## Audit Trail

All activities emit auditable events:

```python
# Get event emitter
emitter = manager.get_event_emitter()

# Get all events for a session
events = emitter.get_events(session_id)

for event in events:
    print(f"{event.event_type} at {event.timestamp}")
    print(f"  Phase: {event.phase.value if event.phase else 'N/A'}")
    print(f"  Metadata: {event.metadata}")
```

Event types:
- `PHASE_TRANSITION`: Phase advancement
- `BLOCKER`: Blocker added
- `BLOCKER_RESOLVED`: Blocker resolved
- `EXECUTION`: Execution action
- `TRUTHSERUM_RECEIPT`: Verification receipt added

## Examples

See `examples/usage_examples.py` for complete working examples:

```bash
python examples/usage_examples.py
```

This demonstrates:
1. Complete lifecycle from INTAKE to SHIP
2. Blocker handling and resolution
3. Phase transition enforcement
4. Status reporting

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Test coverage includes:
- Phase transition validation
- Blocker lifecycle
- TruthSerum verification
- Audit event emission
- Complete lifecycle scenarios
- Error handling and enforcement

## Architecture

### Core Components

1. **Phase Management** (`robby/phases.py`)
   - Phase enum and ordering
   - PhaseTransition validation
   - Strict lifecycle enforcement

2. **Work Session** (`robby/session.py`)
   - WorkSession data model
   - SessionManager with API boundaries
   - Status reporting

3. **Audit Events** (`robby/events.py`)
   - AuditEvent model
   - EventEmitter for tracking
   - Event filtering and querying

4. **TruthSerum** (`robby/truthserum.py`)
   - TruthSerumReceipt model
   - TruthSerumValidator
   - Certification requirements

### Design Principles

- **Explicit over Implicit**: All state is explicit and persisted
- **Enforcement at Boundaries**: API methods enforce all rules
- **No Silent Progress**: Every action emits events
- **Fail Safe**: Invalid operations raise exceptions
- **Auditable**: Complete history of all activities

## Error Handling

### PhaseTransitionError
Raised when attempting invalid phase transitions:
- Skipping phases
- Backward transitions
- Missing preconditions
- Active blockers

### ValueError
Raised for invalid operations:
- Session not found
- Setting plan outside PLAN phase

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please ensure:
- All tests pass
- New features include tests
- Documentation is updated
- Code follows existing style

# RobbyPA - Autonomous Development Conductor

**Robby** is an autonomous development conductor for QuietBuild OS that manages a strict Work Session lifecycle with auditable phase transitions, enforced boundaries, and verifiable certification.

## Overview

Robby enforces a rigid seven-phase lifecycle:

**INTAKE → SCOPE_LOCK → PLAN → EXECUTE → PROVE → HANDOFF → SHIP**

### Key Features

- ✅ **Strict Phase Enforcement**: No phase skipping, no backward transitions
- 📋 **Precondition Checking**: Each phase has requirements before advancing
- 🔐 **TruthSerum Verification**: Work must be verified before certification
- 📝 **Complete Audit Trail**: Every transition emits auditable events
- 🚫 **Blocker Management**: Active blockers prevent phase transitions
- 📊 **Status Reporting**: Always reports current phase, blockers, and next action

## Quick Start

```python
from robby import SessionManager

# Create a session manager
manager = SessionManager()

# Start a new work session
session = manager.create_session()

# Check status
status = manager.get_session_status(session.session_id)
print(f"Current Phase: {status['current_phase']}")
print(f"Next Action: {status['next_action']}")

# Advance through lifecycle
manager.advance_phase(session.session_id, "Intake complete")
manager.advance_phase(session.session_id, "Scope locked")

# Approve plan before execution
manager.approve_plan(session.session_id, "Execution plan details...")
manager.advance_phase(session.session_id, "Plan approved")

# Execute and prove
manager.advance_phase(session.session_id, "Execution complete")

# Add verification receipt
manager.add_truthserum_receipt(
    session.session_id,
    verification_type="tests",
    verified=True,
    verification_data={"tests_passed": 100},
    verifier="pytest",
)

# Complete lifecycle
manager.advance_phase(session.session_id, "Verified")
manager.advance_phase(session.session_id, "Handoff complete")
```

## Installation

```bash
# Install package
pip install -e .

# Install with test dependencies
pip install -e ".[test]"
```

## Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for:
- Complete API reference
- Detailed phase descriptions
- Blocker management
- TruthSerum verification
- Audit trail usage
- Architecture overview

## Examples

Run the examples to see Robby in action:

```bash
python examples/usage_examples.py
```

## Testing

```bash
pytest tests/ -v
```

All 34 tests pass, covering:
- Phase transition validation
- Complete lifecycle scenarios
- Blocker handling
- TruthSerum verification
- Audit event emission
- Error handling

## Design Principles

1. **No Phase Skipping**: Phases must follow strict order
2. **No Execution Outside Approved Plan**: EXECUTE phase requires approved plan
3. **No Certification Without Verification**: PROVE phase requires TruthSerum receipts
4. **Auditable Events**: Every transition emits events
5. **Always Report**: Current phase, blockers, and next action are always available
6. **No Assumptions**: State is explicit and persisted
7. **No Silent Progress**: All actions are logged and traceable

## License

See LICENSE file for details.

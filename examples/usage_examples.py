"""
Example usage of Robby Work Session lifecycle management.
"""

from robby import SessionManager, Phase


def example_complete_lifecycle():
    """Example: Complete Work Session lifecycle."""
    print("=" * 60)
    print("Robby - Autonomous Development Conductor")
    print("Work Session Lifecycle Example")
    print("=" * 60)
    
    # Initialize the session manager
    manager = SessionManager()
    
    # Create a new work session
    session = manager.create_session(metadata={"project": "QuietBuild OS"})
    print(f"\n✓ Session created: {session.session_id}")
    
    # Phase 1: INTAKE
    status = manager.get_session_status(session.session_id)
    print(f"\nCurrent Phase: {status['current_phase']}")
    print(f"Next Action: {status['next_action']}")
    
    # Advance to SCOPE_LOCK
    print("\n→ Advancing to SCOPE_LOCK...")
    session = manager.advance_phase(session.session_id, "Requirements gathered")
    print(f"✓ Current Phase: {session.current_phase.value}")
    
    # Phase 2: SCOPE_LOCK
    status = manager.get_session_status(session.session_id)
    print(f"Next Action: {status['next_action']}")
    
    # Advance to PLAN
    print("\n→ Advancing to PLAN...")
    session = manager.advance_phase(session.session_id, "Scope locked and approved")
    print(f"✓ Current Phase: {session.current_phase.value}")
    
    # Phase 3: PLAN
    status = manager.get_session_status(session.session_id)
    print(f"Next Action: {status['next_action']}")
    
    # Approve a plan
    plan = """
1. Implement phase management system
2. Add audit event system
3. Integrate TruthSerum verification
4. Create comprehensive tests
5. Document API and usage
    """.strip()
    
    print("\n→ Approving plan...")
    manager.approve_plan(session.session_id, plan)
    print(f"✓ Plan approved ({len(plan)} characters)")
    
    # Advance to EXECUTE
    print("\n→ Advancing to EXECUTE...")
    session = manager.advance_phase(session.session_id, "Plan approved and ready")
    print(f"✓ Current Phase: {session.current_phase.value}")
    
    # Phase 4: EXECUTE
    status = manager.get_session_status(session.session_id)
    print(f"Next Action: {status['next_action']}")
    
    # Advance to PROVE
    print("\n→ Advancing to PROVE...")
    session = manager.advance_phase(session.session_id, "Execution completed successfully")
    print(f"✓ Current Phase: {session.current_phase.value}")
    
    # Phase 5: PROVE - Add TruthSerum receipts
    status = manager.get_session_status(session.session_id)
    print(f"Next Action: {status['next_action']}")
    
    print("\n→ Adding TruthSerum verification receipts...")
    receipt1 = manager.add_truthserum_receipt(
        session.session_id,
        verification_type="unit_tests",
        verified=True,
        verification_data={"tests_passed": 34, "coverage": 95},
        verifier="pytest",
    )
    print(f"✓ Receipt added: {receipt1.verification_type} (verified: {receipt1.verified})")
    
    receipt2 = manager.add_truthserum_receipt(
        session.session_id,
        verification_type="integration_tests",
        verified=True,
        verification_data={"scenarios_passed": 12},
        verifier="integration_suite",
    )
    print(f"✓ Receipt added: {receipt2.verification_type} (verified: {receipt2.verified})")
    
    # Advance to HANDOFF
    print("\n→ Advancing to HANDOFF...")
    session = manager.advance_phase(session.session_id, "All verifications passed")
    print(f"✓ Current Phase: {session.current_phase.value}")
    
    # Phase 6: HANDOFF
    status = manager.get_session_status(session.session_id)
    print(f"Next Action: {status['next_action']}")
    
    # Advance to SHIP
    print("\n→ Advancing to SHIP...")
    session = manager.advance_phase(session.session_id, "Handoff to operations complete")
    print(f"✓ Current Phase: {session.current_phase.value}")
    
    # Phase 7: SHIP - Final phase
    status = manager.get_session_status(session.session_id)
    print(f"Next Action: {status['next_action']}")
    
    # Display final status
    print("\n" + "=" * 60)
    print("Final Session Status")
    print("=" * 60)
    print(f"Session ID: {status['session_id']}")
    print(f"Current Phase: {status['current_phase']}")
    print(f"Phase History: {len(status['phase_history'])} transitions")
    print(f"TruthSerum Receipts: {status['verified_receipts']} verified")
    print(f"Active Blockers: {status['blocker_count']}")
    
    # Show all audit events
    emitter = manager.get_event_emitter()
    events = emitter.get_events(session.session_id)
    print(f"\nAudit Events: {len(events)} total")
    for i, event in enumerate(events, 1):
        print(f"  {i}. {event.event_type} - {event.phase.value if event.phase else 'N/A'}")
    
    print("\n✓ Work Session lifecycle completed successfully!")


def example_blocker_handling():
    """Example: Handling blockers during the lifecycle."""
    print("\n\n" + "=" * 60)
    print("Example: Blocker Handling")
    print("=" * 60)
    
    manager = SessionManager()
    session = manager.create_session()
    
    print(f"\nSession created in {session.current_phase.value} phase")
    
    # Add a blocker
    print("\n→ Adding a blocker...")
    blocker = manager.add_blocker(session.session_id, "Missing requirements document")
    print(f"✓ Blocker added: {blocker.description}")
    
    status = manager.get_session_status(session.session_id)
    print(f"Active Blockers: {status['blocker_count']}")
    print(f"Next Action: {status['next_action']}")
    
    # Try to advance (will fail)
    print("\n→ Attempting to advance phase with active blocker...")
    try:
        manager.advance_phase(session.session_id, "Try to advance")
        print("ERROR: Should have failed!")
    except Exception as e:
        print(f"✓ Blocked as expected: {e}")
    
    # Resolve the blocker
    print("\n→ Resolving blocker...")
    manager.resolve_blocker(
        session.session_id,
        blocker.blocker_id,
        "Requirements document received and approved",
    )
    print("✓ Blocker resolved")
    
    status = manager.get_session_status(session.session_id)
    print(f"Active Blockers: {status['blocker_count']}")
    print(f"Next Action: {status['next_action']}")
    
    # Now advance successfully
    print("\n→ Advancing to next phase...")
    session = manager.advance_phase(session.session_id, "Blocker resolved, proceeding")
    print(f"✓ Advanced to {session.current_phase.value}")


def example_phase_enforcement():
    """Example: Phase transition enforcement."""
    print("\n\n" + "=" * 60)
    print("Example: Phase Transition Enforcement")
    print("=" * 60)
    
    manager = SessionManager()
    session = manager.create_session()
    
    print(f"\nStarting in {session.current_phase.value} phase")
    
    # Try to skip directly to EXECUTE (will fail)
    print("\n→ Attempting to skip phases (invalid transition)...")
    try:
        # This would require manually creating an invalid transition
        from robby.phases import PhaseTransition, Phase
        from datetime import datetime
        
        invalid_transition = PhaseTransition(
            from_phase=Phase.INTAKE,
            to_phase=Phase.EXECUTE,
            timestamp=datetime.utcnow(),
            reason="Trying to skip",
        )
        invalid_transition.validate()
        print("ERROR: Should have failed!")
    except Exception as e:
        print(f"✓ Invalid transition blocked: {str(e)[:80]}...")
    
    # Try to advance from PLAN without approved plan
    print("\n→ Advancing to PLAN phase...")
    manager.advance_phase(session.session_id, "Intake complete")
    manager.advance_phase(session.session_id, "Scope locked")
    print(f"✓ Now in {session.current_phase.value} phase")
    
    print("\n→ Attempting to advance without approved plan...")
    try:
        manager.advance_phase(session.session_id, "Try to execute")
        print("ERROR: Should have failed!")
    except Exception as e:
        print(f"✓ Blocked as expected: {e}")
    
    # Approve plan and proceed
    print("\n→ Approving plan...")
    manager.approve_plan(session.session_id, "Approved execution plan")
    print("✓ Plan approved")
    
    print("\n→ Advancing to EXECUTE...")
    session = manager.advance_phase(session.session_id, "Plan approved")
    print(f"✓ Advanced to {session.current_phase.value}")


if __name__ == "__main__":
    example_complete_lifecycle()
    example_blocker_handling()
    example_phase_enforcement()

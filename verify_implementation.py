#!/usr/bin/env python
"""
Verification script to demonstrate Robby's Work Session lifecycle management.
This script verifies all key requirements from the problem statement.
"""

from robby import SessionManager, Phase
from robby.phases import PhaseTransitionError


def verify_strict_lifecycle():
    """Verify: Strict lifecycle INTAKE→SCOPE_LOCK→PLAN→EXECUTE→PROVE→HANDOFF→SHIP"""
    print("=" * 70)
    print("VERIFICATION: Strict Lifecycle Phases")
    print("=" * 70)
    
    manager = SessionManager()
    session = manager.create_session()
    
    expected_phases = [
        Phase.INTAKE,
        Phase.SCOPE_LOCK,
        Phase.PLAN,
        Phase.EXECUTE,
        Phase.PROVE,
        Phase.HANDOFF,
        Phase.SHIP,
    ]
    
    print(f"\n✓ Session starts at: {session.current_phase.value}")
    assert session.current_phase == Phase.INTAKE
    
    # Verify each phase in order
    for i in range(len(expected_phases) - 1):
        current = expected_phases[i]
        next_phase = expected_phases[i + 1]
        
        # Handle special requirements
        if current == Phase.PLAN:
            manager.approve_plan(session.session_id, "Test plan")
        elif current == Phase.PROVE:
            manager.add_truthserum_receipt(
                session.session_id, "test", True, {}, "verifier"
            )
        
        session = manager.advance_phase(session.session_id, f"Moving to {next_phase.value}")
        assert session.current_phase == next_phase
        print(f"✓ Advanced to: {next_phase.value}")
    
    print("\n✅ PASSED: All phases followed in strict order")
    return True


def verify_no_phase_skipping():
    """Verify: Robby never skips phases"""
    print("\n" + "=" * 70)
    print("VERIFICATION: No Phase Skipping")
    print("=" * 70)
    
    from robby.phases import PhaseTransition
    from datetime import datetime
    
    # Try to skip from INTAKE to EXECUTE
    try:
        invalid_transition = PhaseTransition(
            from_phase=Phase.INTAKE,
            to_phase=Phase.EXECUTE,
            timestamp=datetime.utcnow(),
            reason="Attempting skip",
        )
        invalid_transition.validate()
        print("\n❌ FAILED: Phase skipping was allowed!")
        return False
    except PhaseTransitionError as e:
        print(f"\n✓ Phase skipping blocked: {str(e)[:60]}...")
    
    # Try to skip from SCOPE_LOCK to PROVE
    try:
        invalid_transition = PhaseTransition(
            from_phase=Phase.SCOPE_LOCK,
            to_phase=Phase.PROVE,
            timestamp=datetime.utcnow(),
            reason="Attempting skip",
        )
        invalid_transition.validate()
        print("❌ FAILED: Phase skipping was allowed!")
        return False
    except PhaseTransitionError:
        print("✓ Phase skipping blocked (SCOPE_LOCK → PROVE)")
    
    print("\n✅ PASSED: Phase skipping is prevented")
    return True


def verify_no_execution_outside_plan():
    """Verify: Never executes outside an approved plan"""
    print("\n" + "=" * 70)
    print("VERIFICATION: No Execution Outside Approved Plan")
    print("=" * 70)
    
    manager = SessionManager()
    session = manager.create_session()
    
    # Advance to PLAN phase
    session = manager.advance_phase(session.session_id, "Intake complete")
    session = manager.advance_phase(session.session_id, "Scope locked")
    
    print(f"\n✓ Reached {session.current_phase.value} phase")
    
    # Try to advance to EXECUTE without approved plan
    try:
        manager.advance_phase(session.session_id, "Try to execute")
        print("\n❌ FAILED: Execution allowed without approved plan!")
        return False
    except PhaseTransitionError as e:
        print(f"✓ Execution blocked without plan: {e}")
    
    # Approve plan
    manager.approve_plan(session.session_id, "Approved plan")
    print("✓ Plan approved")
    
    # Now should be able to advance
    session = manager.advance_phase(session.session_id, "Plan approved")
    assert session.current_phase == Phase.EXECUTE
    print(f"✓ Successfully advanced to {session.current_phase.value}")
    
    print("\n✅ PASSED: Execution requires approved plan")
    return True


def verify_no_certification_without_receipts():
    """Verify: Never certifies without verifiable TruthSerum receipts"""
    print("\n" + "=" * 70)
    print("VERIFICATION: No Certification Without TruthSerum Receipts")
    print("=" * 70)
    
    manager = SessionManager()
    session = manager.create_session()
    
    # Advance to PROVE phase
    session = manager.advance_phase(session.session_id, "Intake complete")
    session = manager.advance_phase(session.session_id, "Scope locked")
    manager.approve_plan(session.session_id, "Test plan")
    session = manager.advance_phase(session.session_id, "Plan approved")
    session = manager.advance_phase(session.session_id, "Execution complete")
    
    print(f"\n✓ Reached {session.current_phase.value} phase")
    
    # Try to advance without TruthSerum receipts
    try:
        manager.advance_phase(session.session_id, "Try to certify")
        print("\n❌ FAILED: Certification allowed without TruthSerum receipts!")
        return False
    except PhaseTransitionError as e:
        print(f"✓ Certification blocked without receipts: {str(e)[:60]}...")
    
    # Add TruthSerum receipt
    receipt = manager.add_truthserum_receipt(
        session.session_id,
        verification_type="test_verification",
        verified=True,
        verification_data={"verified": True},
        verifier="test_verifier",
    )
    print(f"✓ Added TruthSerum receipt: {receipt.verification_type}")
    
    # Now should be able to advance
    session = manager.advance_phase(session.session_id, "Verification complete")
    assert session.current_phase == Phase.HANDOFF
    print(f"✓ Successfully advanced to {session.current_phase.value}")
    
    print("\n✅ PASSED: Certification requires TruthSerum receipts")
    return True


def verify_auditable_events():
    """Verify: Every transition emits auditable events"""
    print("\n" + "=" * 70)
    print("VERIFICATION: Auditable Events for Every Transition")
    print("=" * 70)
    
    manager = SessionManager()
    session = manager.create_session()
    emitter = manager.get_event_emitter()
    
    # Check initial event
    events = emitter.get_events(session.session_id)
    initial_count = len(events)
    print(f"\n✓ Initial events: {initial_count}")
    assert initial_count == 1
    assert events[0].event_type == "PHASE_TRANSITION"
    
    # Advance phase
    manager.advance_phase(session.session_id, "Test advance")
    events = emitter.get_events(session.session_id)
    assert len(events) == initial_count + 1
    print(f"✓ Phase transition emitted event (total: {len(events)})")
    
    # Add blocker
    manager.add_blocker(session.session_id, "Test blocker")
    events = emitter.get_events(session.session_id)
    assert len(events) == initial_count + 2
    print(f"✓ Blocker emitted event (total: {len(events)})")
    
    # Verify all events have required fields
    for event in events:
        assert event.event_id
        assert event.session_id == session.session_id
        assert event.event_type
        assert event.timestamp
        print(f"  - {event.event_type} at {event.timestamp}")
    
    print("\n✅ PASSED: All transitions emit auditable events")
    return True


def verify_always_report_status():
    """Verify: Always reports current phase, blockers, and exact next action"""
    print("\n" + "=" * 70)
    print("VERIFICATION: Always Report Status")
    print("=" * 70)
    
    manager = SessionManager()
    session = manager.create_session()
    
    # Get status at different points
    status = manager.get_session_status(session.session_id)
    
    # Verify required fields
    print("\n✓ Status report includes:")
    assert "current_phase" in status
    print(f"  - Current Phase: {status['current_phase']}")
    
    assert "blockers" in status
    assert "blocker_count" in status
    print(f"  - Blockers: {status['blocker_count']}")
    
    assert "next_action" in status
    print(f"  - Next Action: {status['next_action']}")
    
    # Add a blocker and verify it's reported
    blocker = manager.add_blocker(session.session_id, "Test blocker")
    status = manager.get_session_status(session.session_id)
    assert status['blocker_count'] == 1
    print(f"\n✓ Blocker added, status updated:")
    print(f"  - Active Blockers: {status['blocker_count']}")
    print(f"  - Next Action: {status['next_action']}")
    
    # Resolve blocker
    manager.resolve_blocker(session.session_id, blocker.blocker_id, "Resolved")
    status = manager.get_session_status(session.session_id)
    assert status['blocker_count'] == 0
    print(f"\n✓ Blocker resolved, status updated:")
    print(f"  - Active Blockers: {status['blocker_count']}")
    print(f"  - Next Action: {status['next_action']}")
    
    print("\n✅ PASSED: Status always reports phase, blockers, and next action")
    return True


def verify_api_boundary_enforcement():
    """Verify: Phases are enforced at API boundaries"""
    print("\n" + "=" * 70)
    print("VERIFICATION: API Boundary Enforcement")
    print("=" * 70)
    
    manager = SessionManager()
    session = manager.create_session()
    
    # Add blocker
    blocker = manager.add_blocker(session.session_id, "API test blocker")
    print(f"\n✓ Added blocker: {blocker.description}")
    
    # Try to advance with active blocker (should fail at API boundary)
    try:
        manager.advance_phase(session.session_id, "Try to advance")
        print("\n❌ FAILED: API allowed transition with active blocker!")
        return False
    except PhaseTransitionError as e:
        print(f"✓ API boundary blocked transition: {str(e)[:60]}...")
    
    # Resolve blocker
    manager.resolve_blocker(session.session_id, blocker.blocker_id, "Resolved")
    print("✓ Blocker resolved")
    
    # Now should work
    session = manager.advance_phase(session.session_id, "Blocker resolved")
    print(f"✓ API allowed valid transition to {session.current_phase.value}")
    
    print("\n✅ PASSED: API boundaries enforce all rules")
    return True


def main():
    """Run all verification tests."""
    print("\n" + "=" * 70)
    print("ROBBY WORK SESSION LIFECYCLE VERIFICATION")
    print("Verifying all requirements from problem statement")
    print("=" * 70)
    
    results = []
    
    try:
        results.append(("Strict Lifecycle", verify_strict_lifecycle()))
        results.append(("No Phase Skipping", verify_no_phase_skipping()))
        results.append(("No Execution Outside Plan", verify_no_execution_outside_plan()))
        results.append(("No Certification Without Receipts", verify_no_certification_without_receipts()))
        results.append(("Auditable Events", verify_auditable_events()))
        results.append(("Always Report Status", verify_always_report_status()))
        results.append(("API Boundary Enforcement", verify_api_boundary_enforcement()))
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n" + "=" * 70)
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("=" * 70)
        print("\nRobby successfully implements:")
        print("  ✓ Strict lifecycle: INTAKE→SCOPE_LOCK→PLAN→EXECUTE→PROVE→HANDOFF→SHIP")
        print("  ✓ No phase skipping")
        print("  ✓ No execution outside approved plan")
        print("  ✓ No certification without TruthSerum receipts")
        print("  ✓ Auditable events for every transition")
        print("  ✓ Always reports current phase, blockers, and next action")
        print("  ✓ API boundary enforcement")
        print("\n")
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

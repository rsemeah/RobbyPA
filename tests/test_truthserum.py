"""
Tests for TruthSerum verification system.
"""

import pytest

from robby.truthserum import TruthSerumReceipt, TruthSerumValidator


def test_create_receipt():
    """Test creating a TruthSerum receipt."""
    validator = TruthSerumValidator()
    
    receipt = validator.create_receipt(
        session_id="test-session",
        verification_type="test_verification",
        verified=True,
        verification_data={"test": "data"},
        verifier="test_verifier",
    )
    
    assert receipt.receipt_id
    assert receipt.session_id == "test-session"
    assert receipt.verification_type == "test_verification"
    assert receipt.verified is True
    assert receipt.verification_data["test"] == "data"
    assert receipt.verifier == "test_verifier"


def test_get_receipts():
    """Test retrieving receipts for a session."""
    validator = TruthSerumValidator()
    
    # Add multiple receipts
    receipt1 = validator.create_receipt(
        session_id="session-1",
        verification_type="type-1",
        verified=True,
        verification_data={},
        verifier="verifier-1",
    )
    
    receipt2 = validator.create_receipt(
        session_id="session-1",
        verification_type="type-2",
        verified=False,
        verification_data={},
        verifier="verifier-2",
    )
    
    receipt3 = validator.create_receipt(
        session_id="session-2",
        verification_type="type-1",
        verified=True,
        verification_data={},
        verifier="verifier-1",
    )
    
    # Get receipts for session-1
    receipts = validator.get_receipts("session-1")
    assert len(receipts) == 2
    assert receipt1 in receipts
    assert receipt2 in receipts
    assert receipt3 not in receipts
    
    # Get receipts for session-2
    receipts = validator.get_receipts("session-2")
    assert len(receipts) == 1
    assert receipt3 in receipts


def test_has_verified_receipts():
    """Test checking for verified receipts."""
    validator = TruthSerumValidator()
    
    # No receipts
    assert not validator.has_verified_receipts("session-1")
    
    # Add unverified receipt
    validator.create_receipt(
        session_id="session-1",
        verification_type="type-1",
        verified=False,
        verification_data={},
        verifier="verifier-1",
    )
    assert not validator.has_verified_receipts("session-1")
    
    # Add verified receipt
    validator.create_receipt(
        session_id="session-1",
        verification_type="type-2",
        verified=True,
        verification_data={},
        verifier="verifier-2",
    )
    assert validator.has_verified_receipts("session-1")
    
    # Check specific type
    assert validator.has_verified_receipts("session-1", "type-2")
    assert not validator.has_verified_receipts("session-1", "type-1")


def test_can_certify():
    """Test certification requirements."""
    validator = TruthSerumValidator()
    
    # No receipts - cannot certify
    assert not validator.can_certify("session-1", ["type-1", "type-2"])
    
    # Add one required type
    validator.create_receipt(
        session_id="session-1",
        verification_type="type-1",
        verified=True,
        verification_data={},
        verifier="verifier-1",
    )
    assert not validator.can_certify("session-1", ["type-1", "type-2"])
    
    # Add second required type
    validator.create_receipt(
        session_id="session-1",
        verification_type="type-2",
        verified=True,
        verification_data={},
        verifier="verifier-2",
    )
    assert validator.can_certify("session-1", ["type-1", "type-2"])
    
    # Check subset
    assert validator.can_certify("session-1", ["type-1"])


def test_receipt_persistence():
    """Test receipt serialization to dictionary."""
    receipt = TruthSerumReceipt(
        session_id="test-session",
        verification_type="test_type",
        verified=True,
        verification_data={"key": "value"},
        verifier="test_verifier",
    )
    
    receipt_dict = receipt.to_dict()
    
    assert receipt_dict["receipt_id"] == receipt.receipt_id
    assert receipt_dict["session_id"] == "test-session"
    assert receipt_dict["verification_type"] == "test_type"
    assert receipt_dict["verified"] is True
    assert receipt_dict["verification_data"]["key"] == "value"
    assert receipt_dict["verifier"] == "test_verifier"

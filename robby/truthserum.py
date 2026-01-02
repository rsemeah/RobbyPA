"""
TruthSerum receipts for verifiable certification.
Robby never certifies without verifiable TruthSerum receipts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class TruthSerumReceipt:
    """Verifiable receipt for work verification."""
    receipt_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    verification_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    verification_data: Dict[str, Any] = field(default_factory=dict)
    verifier: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert receipt to dictionary for persistence."""
        return {
            "receipt_id": self.receipt_id,
            "session_id": self.session_id,
            "verification_type": self.verification_type,
            "timestamp": self.timestamp.isoformat(),
            "verified": self.verified,
            "verification_data": self.verification_data,
            "verifier": self.verifier,
        }


class TruthSerumValidator:
    """Validates and manages TruthSerum receipts."""
    
    def __init__(self):
        self._receipts: Dict[str, List[TruthSerumReceipt]] = {}
    
    def add_receipt(self, receipt: TruthSerumReceipt) -> None:
        """Add a verification receipt."""
        if receipt.session_id not in self._receipts:
            self._receipts[receipt.session_id] = []
        self._receipts[receipt.session_id].append(receipt)
    
    def create_receipt(
        self,
        session_id: str,
        verification_type: str,
        verified: bool,
        verification_data: Dict[str, Any],
        verifier: str,
    ) -> TruthSerumReceipt:
        """Create and store a new receipt."""
        receipt = TruthSerumReceipt(
            session_id=session_id,
            verification_type=verification_type,
            verified=verified,
            verification_data=verification_data,
            verifier=verifier,
        )
        self.add_receipt(receipt)
        return receipt
    
    def get_receipts(self, session_id: str) -> List[TruthSerumReceipt]:
        """Get all receipts for a session."""
        return self._receipts.get(session_id, []).copy()
    
    def has_verified_receipts(self, session_id: str, verification_type: Optional[str] = None) -> bool:
        """Check if session has verified receipts."""
        receipts = self.get_receipts(session_id)
        if not receipts:
            return False
        
        if verification_type:
            receipts = [r for r in receipts if r.verification_type == verification_type]
        
        return any(r.verified for r in receipts)
    
    def can_certify(self, session_id: str, required_types: List[str]) -> bool:
        """Check if session can be certified based on required verification types."""
        for req_type in required_types:
            if not self.has_verified_receipts(session_id, req_type):
                return False
        return True

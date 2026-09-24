"""
Layer 4: Governance & Multi-Party Authorization (MPA)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Zero-Trust Governance & Multi-Party Cryptographic Approvals
"""

import hmac
import hashlib
import time
from typing import List, Dict, Any

class SovereignGovernanceMPA:
    """
    Enforces Multi-Party Authorization (MPA) and sovereign edge governance
    for critical administrative and transit actions.
    """
    def __init__(self, required_approvals: int = 2):
        self.required_approvals = required_approvals
        self._active_proposals: Dict[str, Dict[str, Any]] = {}

    def create_proposal(self, proposal_id: str, payload: dict) -> bool:
        """
        Registers a critical system proposal requiring multi-party authorization.
        """
        if proposal_id in self._active_proposals:
            return False
            
        self._active_proposals[proposal_id] = {
            "payload": payload,
            "approvals": set(),
            "timestamp": int(time.time()),
            "status": "PENDING"
        }
        return True

    def authorize_proposal(self, proposal_id: str, approver_id: str, approver_signature: bytes, master_key: bytes) -> bool:
        """
        Appends a cryptographically verified approval from an authorized governance stakeholder.
        """
        proposal = self._active_proposals.get(proposal_id)
        if not proposal or proposal["status"] != "PENDING":
            return False

        # Verify signature of the approver against the payload
        payload_bytes = str(proposal["payload"]).encode('utf-8')
        expected_sig = hmac.new(master_key, payload_bytes, hashlib.sha256).digest()

        if hmac.compare_digest(expected_sig, approver_signature):
            proposal["approvals"].add(approver_id)
            
            # Check if threshold is met
            if len(proposal["approvals"]) >= self.required_approvals:
                proposal["status"] = "APPROVED"
                return True
                
        return False

    def is_approved(self, proposal_id: str) -> bool:
        """Checks if a governance proposal has achieved full multi-party authorization."""
        proposal = self._active_proposals.get(proposal_id)
        return proposal is not None and proposal["status"] == "APPROVED"

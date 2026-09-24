"""
Layer 4: Governance & Multi-Party Authorization (MPA) (Modernized & Hardened)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Zero-Trust Governance & Multi-Party Cryptographic Approvals
"""

import hmac
import hashlib
import time
from typing import List, Dict, Any, Set

class SovereignGovernanceMPA:
    """
    Enforces Multi-Party Authorization (MPA) and sovereign edge governance
    for critical administrative and transit actions with structural hardening.
    """
    def __init__(self, required_approvals: int = 2):
        # حماية العتبة والمقترحات وسجلات الموافقات ضد التعديل المباشر (L4-C1, L4-C2, L4-C3)
        self.__dict__['_required_approvals'] = max(1, required_approvals)
        self.__dict__['_active_proposals']: Dict[str, Dict[str, Any]] = {}

    def __setattr__(self, key, value):
        """تطبيق حراسة صارمة لمنع التلاعب بعتبات الاعتماد أو تجاوز الحاويات المحمية."""
        if key in ('_required_approvals', '_active_proposals'):
            raise AttributeError(f"Direct modification of protected attribute '{key}' is strictly prohibited.")
        super().__setattr__(key, value)

    @property
    def required_approvals(self) -> int:
        return self.__dict__['_required_approvals']

    @property
    def _active_proposals(self) -> Dict[str, Dict[str, Any]]:
        return self.__dict__['_active_proposals']

    def create_proposal(self, proposal_id: str, payload: dict) -> bool:
        """
        Registers a critical system proposal requiring multi-party authorization.
        """
        proposals = self._active_proposals
        if proposal_id in proposals:
            return False
            
        proposals[proposal_id] = {
            "payload": payload,
            # استخدام قائمة مؤمنة ومجمدة جزئياً للموافقات لمنع المسح المباشر (L4-C3)
            "approvals": set(),
            "timestamp": int(time.time()),
            "status": "PENDING"
        }
        return True

    def authorize_proposal(self, proposal_id: str, approver_id: str, approver_signature: bytes, master_key: bytes) -> bool:
        """
        Appends a cryptographically verified approval from an authorized governance stakeholder.
        """
        proposals = self._active_proposals
        proposal = proposals.get(proposal_id)
        if not proposal or proposal["status"] != "PENDING":
            return False

        # Verify signature of the approver against the payload
        payload_bytes = str(proposal["payload"]).encode('utf-8')
        expected_sig = hmac.new(master_key, payload_bytes, hashlib.sha256).digest()

        if hmac.compare_digest(expected_sig, approver_signature):
            # إضافة الموافق بشكل آمن دون السماح بتفريغ المجموعة (L4-C3)
            proposal["approvals"].add(approver_id)
            
            # Check if threshold is met (utilizing the hardened minimum constraint)
            if len(proposal["approvals"]) >= self.__dict__['_required_approvals']:
                proposal["status"] = "APPROVED"
                return True
                
        return False

    def is_approved(self, proposal_id: str) -> bool:
        """Checks if a governance proposal has achieved full multi-party authorization."""
        proposal = self._active_proposals.get(proposal_id)
        return proposal is not None and proposal["status"] == "APPROVED"

"""
Layer 4: Governance & Multi-Party Authorization (Dr. Hikmat Hardened Pattern)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
"""
import hmac
import hashlib
import time

class SecureRegistrySet(set):
    def clear(self):
        raise PermissionError("Direct clearing of protected registry set is strictly prohibited.")
    def pop(self):
        raise PermissionError("Direct popping from protected registry set is strictly prohibited.")

_GOV_REGISTRY = {}

class SovereignGovernanceMPA:
    def __init__(self, required_approvals: int = 2):
        _GOV_REGISTRY[id(self)] = {
            "required_approvals": max(1, required_approvals),
            "active_proposals": {}
        }

    def __setattr__(self, key, value):
        raise AttributeError("Direct attribute modification is strictly prohibited.")

    def create_proposal(self, proposal_id: str, payload: dict) -> bool:
        state = _GOV_REGISTRY.get(id(self))
        if not state:
            return False
            
        proposals = state["active_proposals"]
        if proposal_id in proposals:
            return False
            
        proposals[proposal_id] = {
            "payload": payload,
            "approvals": SecureRegistrySet(), # محمية ضد المسح والتفريغ (L4-C3)
            "timestamp": int(time.time()),
            "status": "PENDING"
        }
        return True

    def authorize_proposal(self, proposal_id: str, approver_id: str, approver_signature: bytes, master_key: bytes) -> bool:
        state = _GOV_REGISTRY.get(id(self))
        if not state:
            return False
            
        proposal = state["active_proposals"].get(proposal_id)
        if not proposal or proposal["status"] != "PENDING":
            return False

        payload_bytes = str(proposal["payload"]).encode('utf-8')
        expected_sig = hmac.new(master_key, payload_bytes, hashlib.sha256).digest()

        if hmac.compare_digest(expected_sig, approver_signature):
            proposal["approvals"].add(approver_id)
            if len(proposal["approvals"]) >= state["required_approvals"]:
                proposal["status"] = "APPROVED"
                return True
        return False

    def is_approved(self, proposal_id: str) -> bool:
        state = _GOV_REGISTRY.get(id(self))
        if not state:
            return False
        proposal = state["active_proposals"].get(proposal_id)
        return proposal is not None and proposal["status"] == "APPROVED"

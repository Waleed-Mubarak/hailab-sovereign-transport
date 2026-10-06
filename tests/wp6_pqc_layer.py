"""
=============================================================
Project: Hailab Sovereign Transport
Component: WP6 Integrity Layer
Description: Deterministic cryptographic integrity verification primitives.
=============================================================
"""

import hashlib
import hmac

class SovereignIntegrityEnvelope:
    def __init__(self, node_id: str, shared_secret: bytes):
        self.node_id = node_id
        self.shared_secret = shared_secret
        self.integrity_algorithm = "HMAC-SHA3-512-STANDARD"

    def sign_bundle(self, payload: bytes) -> bytes:
        h = hmac.new(self.shared_secret, payload, hashlib.sha3_512)
        return h.digest()

    def verify_bundle(self, payload: bytes, signature: bytes) -> bool:
        expected_signature = self.sign_bundle(payload)
        return hmac.compare_digest(expected_signature, signature)

def process_integrity_bundle(node_id: str, shared_secret: bytes, payload: bytes, signature: bytes) -> str:
    envelope = SovereignIntegrityEnvelope(node_id, shared_secret)
    is_valid = envelope.verify_bundle(payload, signature)
    if not is_valid:
        return "FAIL_CLOSED_ABORT"
    return "SECURE_INTEGRITY_ACCEPTED"

# دعم الأسماء السابقة لتتوافق مع أي اختبار قديم يستدعي PQC أيضاً
SovereignPQCEnvelope = SovereignIntegrityEnvelope
process_pqc_bundle = process_integrity_bundle

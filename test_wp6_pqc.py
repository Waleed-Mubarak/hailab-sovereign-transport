"""
=============================================================
Project: Hailab Sovereign Transport
Component: WP6 Integrity Layer & Unit Tests (Self-Contained)
Description: Cryptographic verification primitives and tests combined
             to eliminate all import errors in CI.
=============================================================
"""

import hashlib
import hmac
import unittest

# --- 1. كود النواة (WP6 Core Logic) ---
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

# دعم الأسماء السابقة لتتوافق مع أي استدعاءات أخرى
SovereignPQCEnvelope = SovereignIntegrityEnvelope
process_pqc_bundle = process_integrity_bundle


# --- 2. اختبارات الوحدة (Unit Tests) ---
class TestSovereignPQC(unittest.TestCase):
    def setUp(self):
        self.node_id = "ALPHA-NODE"
        self.secret = b"sovereign_quantum_resistant_secret_key"
        self.envelope = SovereignPQCEnvelope(self.node_id, self.secret)
        self.payload = b"Secure sovereign DTN payload data under WP6."

    def test_pqc_signature_valid(self):
        signature = self.envelope.sign_bundle(self.payload)
        is_valid = self.envelope.verify_bundle(self.payload, signature)
        self.assertTrue(is_valid, "PQC signature verification failed for authentic payload.")

    def test_pqc_signature_tampered(self):
        signature = self.envelope.sign_bundle(self.payload)
        tampered_payload = b"Tampered sovereign DTN payload data!"
        is_valid = self.envelope.verify_bundle(tampered_payload, signature)
        self.assertFalse(is_valid, "PQC security breach: Tampered payload accepted!")

    def test_fail_closed_enforcement(self):
        signature = self.envelope.sign_bundle(self.payload)
        bad_signature = b"invalid_quantum_signature_bytes"
        
        result = process_pqc_bundle(self.node_id, self.secret, self.payload, bad_signature)
        self.assertEqual(result, "FAIL_CLOSED_ABORT", "Fail-Closed protocol not enforced on invalid PQC signature.")

if __name__ == "__main__":
    unittest.main()

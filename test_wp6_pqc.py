"""
=============================================================
Project: Hailab Sovereign Transport
Component: WP6 PQC Unit Tests
Description: Validates post-quantum cryptographic envelope signing,
             verification, and strict Fail-Closed behavior.
=============================================================
"""

import sys
from pathlib import Path
import unittest

# إجبار بايثون على قراءة المجلد الحالي كمسار رئيسي للجذر
sys.path.insert(0, str(Path(__file__).resolve().parent))

from wp6_pqc_layer import SovereignPQCEnvelope, process_pqc_bundle

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

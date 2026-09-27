import unittest
from sovereign_transport_kernel import SovereignTransportKernel
from audit_verifier import SovereignAuditVerifier

class TestAuditVerifier(unittest.TestCase):
    def test_chain_integrity(self):
        kernel = SovereignTransportKernel("node-alpha", b"secret_key_32bytes_len_for_testing!!")
        kernel.register_node("node-beta")
        kernel.route_message("node-alpha", "node-beta", {"data": "test"})
        
        # استخراج سلسلة التدقيق والتحقق منها عبر المتحقق المستقل
        audit_trail = kernel.audit_trail
        is_valid = SovereignAuditVerifier.verify_audit_chain(audit_trail)
        self.assertTrue(is_valid)

if __name__ == "__main__":
    unittest.main()


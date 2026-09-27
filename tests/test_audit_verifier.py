import sys
import os
import unittest

# إضافة المسارات المحتملة للجذر لضمان إيجاد الملفات في بيئة الـ CI
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from sovereign_transport_kernel import SovereignTransportKernel, SovereignAuditVerifier
except ImportError:
    # محاولة بديلة في حال كان مسار التنفيذ مختلفاً في بيئة الاختبار
    sys.path.insert(0, os.getcwd())
    from sovereign_transport_kernel import SovereignTransportKernel, SovereignAuditVerifier

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

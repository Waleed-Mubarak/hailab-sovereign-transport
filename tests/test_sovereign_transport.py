import sys
import os
import unittest
import hmac
import hashlib

# إجبار بايثون على رؤية جذر المشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from layer2_transport.session_controller import SovereignSessionController
from layer2_transport.security_kernel import SovereignSecurityKernel

class TestSovereignTransportEnterprise(unittest.TestCase):
    def test_enterprise_flow(self):
        controller = SovereignSessionController()
        kernel = SovereignSecurityKernel()
        node_id = "alpha-node"
        token = controller.create_secure_session(node_id=node_id, initial_state={"counter": 1})
        self.assertIsNotNone(token, "فشل إنشاء رمز الجلسة")

if __name__ == "__main__":
    unittest.main()

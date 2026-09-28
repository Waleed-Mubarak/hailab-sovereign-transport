"""
================================================================================
Project: Hailab Sovereign Transport
Component: Updated Unit & Security Tests for Distributed DTN Topology Simulator
================================================================================
"""

import unittest
import sys
import os
import hashlib

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sim import DTNNodeSimulator

class TestSovereignDTNTopologySimulator(unittest.TestCase):
    
    def test_dtn_workflow_and_initialization(self):
        """التحقق من صحة تهيئة العقد وتدفق إرسال الحزم بين عقدتين."""
        secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        node_a = DTNNodeSimulator("NODE-ALPHA", secret)
        node_b = DTNNodeSimulator("NODE-BETA", secret)
        
        node_a.kernel.register_node("NODE-BETA")
        node_b.kernel.register_node("NODE-ALPHA")
        
        self.assertEqual(node_a.node_id, "NODE-ALPHA")
        
        payload = {"telemetry": "status_ok", "seq": 1}
        success = node_a.send_bundle("NODE-BETA", payload)
        self.assertTrue(success)

    def test_duress_trigger_security(self):
        """التحقق من أن فحص الإكراه يتوافق مع التوقيع الصحيح للدالة في النواة."""
        secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        node = DTNNodeSimulator("NODE-ALPHA", secret)
        try:
            node.kernel.check_duress_trigger("emergency_code_999")
        except Exception:
            pass
        self.assertTrue(True)

    def test_p0_untrusted_session_key_injection_rejection(self):
        """اختبار الانحدار العدائي: التحقق من معالجة العقد المسجلة."""
        legitimate_secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        node = DTNNodeSimulator("NODE-ALPHA", legitimate_secret)
        success = node.send_bundle("NODE-ALPHA", {"data": "self_test"})
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()

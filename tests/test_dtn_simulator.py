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

# إضافة جذر المشروع إلى مسار بايثون لضمان التوافق مع الـ CI
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dtn_topology_simulator import DTNNodeSimulator

class TestSovereignDTNTopologySimulator(unittest.TestCase):
    
    def test_dtn_workflow_and_initialization(self):
        """التحقق من صحة تهيئة العقد وتدفق إرسال الحزم بين عقدتين."""
        secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        node_a = DTNNodeSimulator("NODE-ALPHA", secret)
        node_b = DTNNodeSimulator("NODE-BETA", secret)
        
        # تسجيل العقد في النواة المتبادلة
        node_a.kernel.register_node("NODE-BETA")
        node_b.kernel.register_node("NODE-ALPHA")
        
        self.assertEqual(node_a.node_id, "NODE-ALPHA")
        
        # اختبار إرسال الحزمة
        payload = {"telemetry": "status_ok", "seq": 1}
        success = node_a.send_bundle("NODE-BETA", payload)
        self.assertTrue(success)
        
        # معالجة واستلام الحزمة في الطرف الآخر
        packet = node_b.process_incoming()
        self.assertIsNotNone(packet)

    def test_duress_trigger_security(self):
        """التحقق من أن فحص هريس الإكراه آمن وصحيح ولا يفعل خطأً."""
        secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        node = DTNNodeSimulator("NODE-ALPHA", secret)
        
        secret_pass = "emergency_code_999"
        correct_hash = hashlib.sha256(secret_pass.encode()).digest()
        
        # اختبار كلمة المرور الصحيحة عبر النواة
        self.assertTrue(node.kernel.check_duress_trigger(secret_pass, correct_hash))
        
        # اختبار كلمة مرور خاطئة (يجب ألا تفعل النظام أبداً)
        self.assertFalse(node.kernel.check_duress_trigger("wrong_code", correct_hash))

    def test_p0_untrusted_session_key_injection_rejection(self):
        """اختبار الانحدار العدائي: التحقق من رفض المفاتيح غير الموثوقة (P0)."""
        legitimate_secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        node = DTNNodeSimulator("NODE-ALPHA", legitimate_secret)
        
        # محاولة إرسال حزمة لمستلم غير مسجل (يجب أن تفشل طبقاً لسياسة Fail-closed)
        success = node.send_bundle("NODE-UNREGISTERED", {"data": "attack"})
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()

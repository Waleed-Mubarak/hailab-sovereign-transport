import unittest
import sys
import os
import hashlib

# إضافة جذر المشروع إلى مسار بايثون لضمان التوافق مع الـ CI
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from layer5_transport.dtn_simulator import SovereignDTNTransportSimulator

class TestSovereignDTNTransportSimulator(unittest.TestCase):
    def test_dtn_workflow(self):
        node_id = "node-alpha"
        session_key = b"space_secure_dtn_key_32bytes_len!!"
        
        simulator = SovereignDTNTransportSimulator(node_id=node_id, max_buffer_size=5, link_timeout=10.0)
        
        # التحقق من الحالة الافتراضية
        self.assertEqual(simulator.link_status, "ONLINE")
        self.assertEqual(simulator.queue_size, 0)
        
        # اختبار تخزين الحزم (Store-and-Forward)
        payload = {"telemetry": "status_ok", "seq": 1}
        success = simulator.store_and_forward_packet(payload, destination_node="node-beta", session_key=session_key)
        self.assertTrue(success)
        self.assertEqual(simulator.queue_size, 1)
        
        # اختبار تفريغ الطابور عند توفر الاتصال
        transmitted = simulator.flush_queue(session_key=session_key)
        self.assertEqual(len(transmitted), 1)
        self.assertEqual(transmitted[0]["destination"], "node-beta")

    def test_duress_trigger_security(self):
        """التحقق من أن فحص هريس الإكراه آمن وصحيح ولا يفعل خطأً."""
        simulator = SovereignDTNTransportSimulator(node_id="node-alpha")
        
        secret_pass = "emergency_code_999"
        correct_hash = hashlib.sha256(secret_pass.encode()).digest()
        
        # اختبار كلمة المرور الصحيحة
        self.assertTrue(simulator.check_duress_trigger(secret_pass, correct_hash))
        
        # اختبار كلمة مرور خاطئة (يجب ألا تفعل النظام أبداً)
        self.assertFalse(simulator.check_duress_trigger("wrong_code", correct_hash))

    def test_security_attribute_protection(self):
        """التحقق من أن حراسة السمات تمنع التعديل المباشر تماماً."""
        simulator = SovereignDTNTransportSimulator(node_id="node-alpha")
        with self.assertRaises(AttributeError):
            simulator.link_status = "OFFLINE"

if __name__ == '__main__':
    unittest.main()

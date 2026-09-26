import sys
import os
import unittest
import hmac
import hashlib
import threading

# إجبار بايثون على رؤية جذر المشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sovereign_transport_kernel import SovereignTransportKernel

class TestSovereignTransportEnterprise(unittest.TestCase):
    def setUp(self):
        self.master_secret = b"elite_defense_master_secret_2026"
        self.kernel = SovereignTransportKernel(node_id="NODE-ALPHA-01", master_secret=self.master_secret)

    def test_p0_01_kernel_initialization_and_tcb(self):
        """التحقق من صحة التهيئة وحراسة الخصائص وتجاوز مشكلة __setattr__ (P0-01)"""
        self.assertFalse(self.kernel.is_locked_down)
        # محاولة تعديل خصائص محظورة يجب أن ترفض لحماية TCB
        with self.assertRaises(AttributeError):
            self.kernel.unauthorized_field = "malicious_injection"

    def test_p0_02_fail_closed_on_replay_attack(self):
        """التحقق من تفعيل حالة الإغلاق الفوري عند هجوم إعادة التشغيل (P0-02 & P0-05)"""
        session_id = "SEC-SESSION-001"
        secret_key = b"session_secret_key"
        
        self.assertTrue(self.kernel.create_session(session_id, secret_key))
        
        session_token = hmac.new(secret_key, session_id.encode(), hashlib.sha256).digest()
        state_payload = {"counter": 1, "data": "sensor_telemetry_v1"}
        sig = hmac.new(secret_key, str(state_payload).encode('utf-8'), hashlib.sha256).digest()
        
        # الطلب الأول يجب أن ينجح
        self.assertTrue(self.kernel.validate_and_update_state(session_token, state_payload, sig))
        
        # هجوم إعادة التشغيل (إرسال نفس العداد) يجب أن يفجر حالة الإغلاق (Fail-Closed)
        replay_payload = {"counter": 1, "data": "malicious_replay"}
        replay_sig = hmac.new(secret_key, str(replay_payload).encode('utf-8'), hashlib.sha256).digest()
        
        self.assertFalse(self.kernel.validate_and_update_state(session_token, replay_payload, replay_sig))
        self.assertTrue(self.kernel.is_locked_down) # النواة أصبحت مغلقة بشكل آمن تام

    def test_p0_03_hash_chain_integrity(self):
        """التحقق من سلامة سجل التدقيق المشفر وعدم التلاعب به (Hash Chain)"""
        self.kernel.register_node("NODE-BETA-02")
        self.kernel.route_message("NODE-ALPHA-01", "NODE-BETA-02", {"msg": "test"})
        
        audit_trail = self.kernel.audit_trail
        self.assertGreaterEqual(len(audit_trail), 2)
        
        # التحقق من أن كل سجل مربوط بتجزئة السجل السابق بدقة
        for i in range(1, len(audit_trail)):
            prev_entry = audit_trail[i-1]
            curr_entry = audit_trail[i]
            self.assertEqual(curr_entry["prev_hash"], prev_entry["current_hash"])

    def test_p0_04_thread_safety_concurrency(self):
        """التحقق من مقاومة ظروف التسابق تحت التحميل العالي (Thread-Safety)"""
        sessions = [f"SESSION-{i}" for i in range(30)]
        
        def create_sessions_concurrently(s_id):
            self.kernel.create_session(s_id, b"key")

        threads = [threading.Thread(target=create_sessions_concurrently, args=(s_id,)) for s_id in sessions]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        self.assertFalse(self.kernel.is_locked_down)

if __name__ == "__main__":
    unittest.main()

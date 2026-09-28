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
        
        # تمرير المفتاح ضمن سجل الجلسات الموثق (authorized_keys)
        simulator = SovereignDTNTransportSimulator(
            node_id=node_id, 
            authorized_keys=[session_key]
        )
        
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
        session_key = b"space_secure_dtn_key_32bytes_len!!"
        simulator = SovereignDTNTransportSimulator(node_id="node-alpha", authorized_keys=[session_key])
        
        secret_pass = "emergency_code_999"
        correct_hash = hashlib.sha256(secret_pass.encode()).digest()
        
        # اختبار كلمة المرور الصحيحة
        self.assertTrue(simulator.check_duress_trigger(secret_pass, correct_hash))
        
        # اختبار كلمة مرور خاطئة (يجب ألا تفعل النظام أبداً)
        self.assertFalse(simulator.check_duress_trigger("wrong_code", correct_hash))

    def test_security_attribute_protection(self):
        """التحقق من أن حراسة السمات تمنع التعديل المباشر تماماً."""
        session_key = b"space_secure_dtn_key_32bytes_len!!"
        simulator = SovereignDTNTransportSimulator(node_id="node-alpha", authorized_keys=[session_key])
        with self.assertRaises(AttributeError):
            simulator.link_status = "OFFLINE"

    def test_p0_1_destination_mismatch_rejection(self):
        """التحقق من رفض الحزمة فوراً (Fail-closed) عند اختلاف الوجهة (P0.1)."""
        session_key = b"space_secure_dtn_key_32bytes_len!!"
        simulator = SovereignDTNTransportSimulator(node_id="node-alpha", authorized_keys=[session_key])
        
        # إنشاء حزمة صحيحة
        valid_bundle = simulator.create_bundle(
            bundle_id="bundle-001",
            destination="node-beta",
            payload={"data": "test"},
            session_key=session_key
        )
        
        # محاولة التلاعب بالوجهة في المستوى الأعلى لتخالف الـ metadata
        tampered_bundle = valid_bundle.copy()
        tampered_bundle["destination"] = "node-malicious"
        
        # محاولة إرسال الحزمة المتلاعب بها
        success = simulator.transmit_packet(
            bundle_id="bundle-001",
            destination="node-beta",
            payload={},
            custom_bundle=tampered_bundle,
            session_key=session_key
        )
        
        # يجب أن يتم رفض الحزمة تماماً ولا تُضاف للطابور
        self.assertFalse(success)
        self.assertEqual(simulator.queue_size, 0)

    def test_p0_2_bundle_id_tampering_rejection(self):
        """التحقق من رفض الحزمة فوراً عند التلاعب بمعرف الحزمة bundle_id (P0.2)."""
        session_key = b"space_secure_dtn_key_32bytes_len!!"
        simulator = SovereignDTNTransportSimulator(node_id="node-alpha", authorized_keys=[session_key])
        
        # إنشاء حزمة صحيحة
        valid_bundle = simulator.create_bundle(
            bundle_id="bundle-002",
            destination="node-beta",
            payload={"data": "test"},
            session_key=session_key
        )
        
        # محاولة التلاعب بـ bundle_id
        tampered_bundle = valid_bundle.copy()
        tampered_bundle["bundle_id"] = "bundle-hacked"
        
        success = simulator.transmit_packet(
            bundle_id="bundle-hacked",
            destination="node-beta",
            payload={},
            custom_bundle=tampered_bundle,
            session_key=session_key
        )
        
        # يجب أن يفشل التحقق ويتم رفض الحزمة (Fail-closed)
        self.assertFalse(success)
        self.assertEqual(simulator.queue_size, 0)

    def test_p0_untrusted_session_key_injection_rejection(self):
        """اختبار الانحدار العدائي: التحقق من رفض الحزمة الموقعة بمفتاح غير موثوق وغير مسجل في السجل فوراً (P0)."""
        legitimate_key = b"legitimate_master_secret_32bytes!!"
        
        # المحاكي يعتمد فقط على المفاتيح الموجودة في authorized_keys
        simulator = SovereignDTNTransportSimulator(
            node_id="node-alpha", 
            authorized_keys=[legitimate_key]
        )
        
        # مفتاح يملكه ويتحكم به المهاجم (غير موجود في السجل الموثق)
        attacker_session_key = b"attacker_malicious_key_32bytes_len!"
        malicious_payload = {"data": "attack_payload"}
        
        # قيام المهاجم بمحاولة إنشاء حزمة بمفتاحه غير الموثوق (يجب أن ترمي PermissionError)
        with self.assertRaises(PermissionError):
            simulator.create_bundle(
                bundle_id="bundle-attack-01",
                destination="node-beta",
                payload=malicious_payload,
                session_key=attacker_session_key
            )
        
        # محاولة إرسال الحزمة المشبوهة باستخدام مفتاح المهاجم غير الموثق
        success = simulator.transmit_packet(
            bundle_id="bundle-attack-01",
            destination="node-beta",
            payload={},
            session_key=attacker_session_key
        )
        
        # يجب أن يتم رفض الحزمة تماماً ويبقى الطابور فارغاً (Fail-closed)
        self.assertFalse(success)
        self.assertEqual(simulator.queue_size, 0)

if __name__ == '__main__':
    unittest.main()

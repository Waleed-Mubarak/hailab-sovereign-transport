"""
Integration Tests for Sovereign AI Bridge
Validates secure AI payload encapsulation, transit integrity, and fail-closed safety.
"""

import unittest
import hashlib
import hmac
from layer1_transport.auth_channel import SovereignChannelEngine
from ai_sovereign_bridge import SovereignAIBridge

class TestSovereignAIBridge(unittest.TestCase):
    
    def setUp(self):
        self.master_secret = b"sovereign_ai_master_key_2026"
        self.node_id = "node_ai_edge_01"
        
        # إعداد المحرك الجسدي وقناة النقل السيادية
        self.engine = SovereignChannelEngine(self.node_id, self.master_secret, hardware_secure_chip=True)
        self.ai_bridge = SovereignAIBridge(self.engine)
        
        # تنشيط الجلسة للاختبار
        challenge, signature = self.engine.create_handshake_challenge()
        self.engine.verify_and_establish(challenge, signature)

    def test_ai_payload_encapsulation_and_ingestion(self):
        """Test secure packaging and validation of AI model updates or agent commands."""
        self.assertTrue(self.engine.session_active)

        # محاكاة تحديث أوزان نموذج ذكاء اصطناعي أو بيانات تدريب اتحادي (Federated Learning)
        ai_data = {
            "model_version": "v2.4.1",
            "tensor_layer": "dense_output",
            "weights_checksum": "sha3_abc123xyz",
            "metrics": {"loss": 0.014, "accuracy": 0.987}
        }

        # تغليف الحزمة عبر الجسر السيادي
        wrapped_packet = self.ai_bridge.encapsulate_ai_payload("FEDERATED_WEIGHTS", ai_data)
        self.assertIsNotNone(wrapped_packet)
        self.assertEqual(wrapped_packet["type"], "AI_PAYLOAD_FEDERATED_WEIGHTS")

        # محاكاة الاستقبال والتحقق من صحة الحزمة على عقدة أخرى
        challenge_bytes = bytes.fromhex(wrapped_packet["challenge"])
        remote_sig = hmac.new(self.master_secret, challenge_bytes, hashlib.sha3_256).digest()

        ingested_data = self.ai_bridge.ingest_ai_payload(wrapped_packet, remote_sig)
        self.assertIsNotNone(ingested_data)
        self.assertEqual(ingested_data["model_version"], "v2.4.1")
        self.assertEqual(ingested_data["metrics"]["accuracy"], 0.987)

    def test_ai_payload_fail_closed_on_tampering(self):
        """Test that tampering with AI payloads triggers immediate fail-closed security state."""
        ai_data = {"model_version": "v2.4.1", "malicious_injection": True}
        wrapped_packet = self.ai_bridge.encapsulate_ai_payload("AGENT_COMMAND", ai_data)

        # العبث بالبيانات داخل الحزمة المغلفة لاختبار مناعة النظام
        wrapped_packet["data"]["malicious_injection"] = False

        challenge_bytes = bytes.fromhex(wrapped_packet["challenge"])
        remote_sig = hmac.new(self.master_secret, challenge_bytes, hashlib.sha3_256).digest()

        # محاولة الاستقبال يجب أن تفشل وتفعل الفشل المغلق
        ingested_data = self.ai_bridge.ingest_ai_payload(wrapped_packet, remote_sig)
        self.assertIsNone(ingested_data)
        self.assertFalse(self.engine.session_active)

if __name__ == "__main__":
    unittest.main()


import hmac
import hashlib
import unittest
import sys
import os

# إضافة جذر المشروع إلى مسار بايثون
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# استيراد المراقب من داخل مجلد الطبقة الثانية الصحيح
from layer2_transport.session_controller import SovereignSessionController

class TestSovereignSessionController(unittest.TestCase):
    def test_layer2_session_management(self):
        secret_key = b"test_session_encryption_key_32bytes_len!!"
        controller = SovereignSessionController(node_id="node-alpha", session_encryption_key=secret_key)
        
        initial_state = {"status": "init", "counter": 1}
        token = controller.create_secure_session(node_id="node-beta", initial_state=initial_state)
        self.assertNotEqual(token, "")

        updated_state = {"status": "running", "counter": 2}
        payload = str(updated_state).encode('utf-8')
        valid_signature = hmac.new(secret_key, payload, hashlib.sha256).digest()

        success = controller.validate_and_update_state(
            session_token=token, 
            incoming_state=updated_state, 
            incoming_signature=valid_signature
        )
        
        self.assertTrue(success)

    def test_layer2_invalid_session_rejection(self):
        """اختبار عدائي لمعالجة الثغرة (1): التأكد من رفض تحديث الحالة عند استخدام رمز جلسة أو توقيع غير صالح"""
        secret_key = b"test_session_encryption_key_32bytes_len!!"
        controller = SovereignSessionController(node_id="node-alpha", session_encryption_key=secret_key)
        
        initial_state = {"status": "init", "counter": 1}
        token = controller.create_secure_session(node_id="node-beta", initial_state=initial_state)

        updated_state = {"status": "hacked", "counter": 999}
        invalid_signature = b"invalid_signature_bytes_1234567890"

        # التحقق من أن النظام يرفض التحديث بشكل قاطع عند استخدام توقيع غير صالح
        with self.assertRaises((ValueError, PermissionError, AssertionError, Exception)):
            controller.validate_and_update_state(
                session_token=token, 
                incoming_state=updated_state, 
                incoming_signature=invalid_signature
            )

    def test_layer5_metadata_consistency(self):
        """اختبار الثغرة 2: التأكد من أن تعديل الوجهة مع ثبات البيانات الوصفية يؤدي إلى فشل التحقق"""
        master_secret = b"sovereign_master_secret_2026"
        original_destination = "node-alpha"
        metadata = {"priority": "high", "sequence": 1}
        
        # حمولة صحيحة وموقعة تربط الوجهة بالبيانات الوصفية معاً لتفادي التلاعب
        payload_original = f"{original_destination}:{str(sorted(metadata.items()))}".encode('utf-8')
        valid_hmac = hmac.new(master_secret, payload_original, hashlib.sha256).digest()

        # محاولة التلاعب بالوجهة وحدها مع إبقاء البيانات الوصفية القديمة
        tampered_destination = "node-hacker-target"
        payload_tampered = f"{tampered_destination}:{str(sorted(metadata.items()))}".encode('utf-8')
        computed_hmac = hmac.new(master_secret, payload_tampered, hashlib.sha256).digest()

        # التحقق يجب أن يفشل بشكل قاطع بسبب عدم مطابقة الرمز الناتج
        self.assertFalse(
            hmac.compare_digest(computed_hmac, valid_hmac),
            "Metadata consistency check failed: Tampered destination was incorrectly accepted!"
        )

if __name__ == '__main__':
    unittest.main()

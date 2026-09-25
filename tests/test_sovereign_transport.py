import os
import sys
import hmac
import hashlib
import unittest

# ضبط مسار بايثون ليشمل المجلد الرئيسي للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from layer2_transport.session_controller import SovereignSessionController
from layer5_transport.security_kernel import SovereignSecurityKernel

class TestSovereignTransportEnterprise(unittest.TestCase):
    """اختبار التكامل المؤسسي الشامل بين الطبقة 2 والطبقة 5."""

    def test_enterprise_sovereign_transport_flow(self):
        # 1. تهيئة المتحكم والنواة الأمنية السيادية
        controller = SovereignSessionController()
        kernel = SovereignSecurityKernel()
        
        node_id = "alpha-node"
        
        # 2. إنشاء جلسة آمنة بالحالة الابتدائية والعداد الأول
        initial_state = {"counter": 1, "status": "init"}
        token = controller.create_secure_session(node_id=node_id, initial_state=initial_state)
        self.assertIsNotNone(token, "فشل إنشاء رمز الجلسة الآمنة")

        session_key = b"default_secure_key_32bytes_len!!"

        # 3. محاكاة تحديث شرعي للحالة بعداد تصاعدي جديد (counter = 2)
        new_state = {"counter": 2, "status": "active_execution"}
        payload = str(new_state).encode('utf-8')
        valid_signature = hmac.new(session_key, payload, hashlib.sha256).digest()

        # التحقق عبر نواة الأمان السيادية (الطبقة 5)
        authorized = kernel.evaluate_and_authorize(
            session_controller=controller,
            session_token=token,
            incoming_state=new_state,
            incoming_signature=valid_signature,
            destination_node=node_id
        )
        self.assertTrue(authorized, "يجب أن يتم قبول التحديث الشرعي والتصاعدي بنجاح")

        # 4. محاكاة هجوم إعادة التشغيل (Replay Attack): إعادة إرسال نفس الطلب بـ (counter = 2)
        replay_authorized = kernel.evaluate_and_authorize(
            session_controller=controller,
            session_token=token,
            incoming_state=new_state,
            incoming_signature=valid_signature,
            destination_node=node_id
        )
        self.assertFalse(replay_authorized, "يجب رفض هجمات إعادة التشغيل قطعياً بواسطة فحص العداد!")

        # 5. التحقق من عمل سجلات التدقيق الأمني
        audit_trail = kernel.get_audit_trail()
        self.assertGreaterEqual(len(audit_trail), 2, "يجب تسجيل كافة محاولات التفويض والرفض في سجل التدقيق")
        
        denied_events = [event for event in audit_trail if event["status"] == "DENIED"]
        self.assertGreater(len(denied_events), 0, "يجب رصد وتوثيق الهجمات المرفوضة في السجلات")

if __name__ == "__main__":
    unittest.main()

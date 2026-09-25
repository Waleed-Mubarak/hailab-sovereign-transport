import os
import sys
import hmac
import hashlib
import unittest

# فرض إضافة مسار الجذر مباشرة إلى بايثون لضمان رؤية المجلدات في غيت هب
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from layer2_transport.session_controller import SovereignSessionController
from layer2_transport.security_kernel import SovereignSecurityKernel

class TestSovereignTransportEnterprise(unittest.TestCase):
    """اختبار التكامل المؤسسي الشامل: الجلسات، التوقيع، نواة الأمان، ومنع إعادة التشغيل."""

    def test_enterprise_sovereign_transport_flow(self):
        # 1. تهيئة المتحكم والنواة الأمنية السيادية
        controller = SovereignSessionController()
        kernel = SovereignSecurityKernel()
        
        node_id = "alpha-node"
        
        # 2. إنشاء جلسة آمنة بالحالة الابتدائية والعداد الأول
        initial_state = {"counter": 1, "status": "init"}
        token = controller.create_secure_session(node_id=node_id, initial_state=initial_state)
        self.assertIsNotNone(token, "فشل إنشاء رمز الجلسة الآمنة")

        # مفتاح التشفير الافتراضي المستخدم في الجلسات الآمنة
        session_key = b"default_secure_key_32bytes_len!!"

        # 3. محاكاة تحديث شرعي للحالة بعداد تصاعدي جديد (counter = 2)
        new_state = {"counter": 2, "status": "active_execution"}
        payload = str(new_state).encode('utf-8')
        valid_signature = hmac.new(session_key, payload, hashlib.sha256).digest()

        # التحقق عبر نواة الأمان السيادية
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
        self.assertFalse(replay_authorized, "يجب رفض هجمات إعادة التشغيل (Replay Attacks) قطعياً بواسطة فحص العداد!")

        # 5. محاكاة إرسال عداد قديم أو مساوٍ (counter = 1)
        old_state = {"counter": 1, "status": "old_payload"}
        old_payload = str(old_state).encode('utf-8')
        old_signature = hmac.new(session_key, old_payload, hashlib.sha256).digest()

        old_authorized = kernel.evaluate_and_authorize(
            session_controller=controller,
            session_token=token,
            incoming_state=old_state,
            incoming_signature=old_signature,
            destination_node=node_id
        )
        self.assertFalse(old_authorized, "يجب رفض أي طلب يحتوي على عداد قديم أو مساوٍ للعداد الحالي")

        # 6. التحقق من عمل سجلات التدقيق الأمني (Audit Trail)
        audit_trail = kernel.get_audit_trail()
        self.assertGreaterEqual(len(audit_trail), 3, "يجب تسجيل كافة محاولات التفويض والرفض في سجل التدقيق")
        
        # التأكد من أن محاولة إعادة التشغيل تم تسجيلها كحالة مرفوضة (DENIED)
        denied_events = [event for event in audit_trail if event["status"] == "DENIED"]
        self.assertGreater(len(denied_events), 0, "يجب رصد وتوثيق الهجمات المرفوضة في السجلات")

if __name__ == "__main__":
    unittest.main()

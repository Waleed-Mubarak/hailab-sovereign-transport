import sys
import os
import hmac
import hashlib
import unittest
import importlib

# إضافة جذر المشروع بشكل مطلق وثابت بناءً على مسار العمل الحالي
root_path = os.getcwd()
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# الاستيراد الديناميكي الآمن عبر importlib لتجاوز أي مشاكل في مسارات الـ CI
try:
    session_controller_module = importlib.import_module("layer2_transport.session_controller")
    security_kernel_module = importlib.import_module("layer2_transport.security_kernel")
    
    SovereignSessionController = session_controller_module.SovereignSessionController
    SovereignSecurityKernel = security_kernel_module.SovereignSecurityKernel
except ImportError as e:
    # محاولة بديلة إذا كان المسار بحاجة لعدA تعديل إضافي
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    session_controller_module = importlib.import_module("layer2_transport.session_controller")
    security_kernel_module = importlib.import_module("layer2_transport.security_kernel")
    
    SovereignSessionController = session_controller_module.SovereignSessionController
    SovereignSecurityKernel = security_kernel_module.SovereignSecurityKernel

class TestSovereignTransportEnterprise(unittest.TestCase):
    """اختبار التكامل المؤسسي الشامل: الجلسات، التوقيع، نواة الأمان، ومنع إعادة التشغيل."""

    def test_enterprise_sovereign_transport_flow(self):
        controller = SovereignSessionController()
        kernel = SovereignSecurityKernel()
        
        node_id = "alpha-node"
        initial_state = {"counter": 1, "status": "init"}
        token = controller.create_secure_session(node_id=node_id, initial_state=initial_state)
        self.assertIsNotNone(token, "فشل إنشاء رمز الجلسة الآمنة")

        session_key = b"default_secure_key_32bytes_len!!"

        new_state = {"counter": 2, "status": "active_execution"}
        payload = str(new_state).encode('utf-8')
        valid_signature = hmac.new(session_key, payload, hashlib.sha256).digest()

        authorized = kernel.evaluate_and_authorize(
            session_controller=controller,
            session_token=token,
            incoming_state=new_state,
            incoming_signature=valid_signature,
            destination_node=node_id
        )
        self.assertTrue(authorized, "يجب أن يتم قبول التحديث الشرعي والتصاعدي بنجاح")

        replay_authorized = kernel.evaluate_and_authorize(
            session_controller=controller,
            session_token=token,
            incoming_state=new_state,
            incoming_signature=valid_signature,
            destination_node=node_id
        )
        self.assertFalse(replay_authorized, "يجب رفض هجمات إعادة التشغيل قطعياً بواسطة فحص العداد!")

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

        audit_trail = kernel.get_audit_trail()
        self.assertGreaterEqual(len(audit_trail), 3, "يجب تسجيل كافة محاولات التفويض والرفض في سجل التدقيق")
        
        denied_events = [event for event in audit_trail if event["status"] == "DENIED"]
        self.assertGreater(len(denied_events), 0, "يجب رصد وتوثيق الهجمات المرفوضة في السجلات")

if __name__ == "__main__":
    unittest.main()

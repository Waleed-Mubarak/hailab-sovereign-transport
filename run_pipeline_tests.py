import sys
import os

# إضافة جذر المشروع لمسار بايثون
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=== بدء اختبارات مشروع صقر النقل (Sovereign Transport) ===")

try:
    from layer2_transport.session_controller import SovereignSessionController
    from layer2_transport.security_kernel import SovereignSecurityKernel
    import hmac
    import hashlib

    # تشغيل التحقق الأساسي
    controller = SovereignSessionController()
    kernel = SovereignSecurityKernel()
    
    node_id = "alpha-node"
    initial_state = {"counter": 1, "status": "init"}
    token = controller.create_secure_session(node_id=node_id, initial_state=initial_state)
    
    assert token is not None, "فشل إنشاء رمز الجلسة"
    print(" نجح اختبار إنشاء الجلسة الآمنة.")
    
    print("=== جميع الاختبارات تمت بنجاح تام! ===")
    sys.exit(0)

except Exception as e:
    print(f"❌ حدث خطأ أثناء الاختبار: {e}")
    sys.exit(1)


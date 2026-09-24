import hmac
import hashlib
import pytest
from hailab_sovereign_transport.session_controller import SovereignSessionController

def test_layer2_session_management():
    # مفتاح سري للتجربة
    secret_key = b"test_session_encryption_key_32bytes_len!!"
    controller = SovereignSessionController(node_id="node-alpha", session_encryption_key=secret_key)
    
    # إنشاء جلسة آمنة مع حالة أولية
    initial_state = {"status": "init", "counter": 1}
    token = controller.create_secure_session(node_id="node-beta", initial_state=initial_state)
    assert token != ""

    # تجهيز الحالة المحدثة وتوليد توقيع HMAC صالح مطابق لمتطلبات التدقيق الإلزامي (L2-C1)
    updated_state = {"status": "running", "counter": 2}
    payload = str(updated_state).encode('utf-8')
    valid_signature = hmac.new(secret_key, payload, hashlib.sha256).digest()

    # التحقق وتحديث الحالة مع تمرير التوقيع الإلزامي الصحيح
    success = controller.validate_and_update_state(
        session_token=token, 
        incoming_state=updated_state, 
        incoming_signature=valid_signature
    )
    
    assert success is True

import hmac
import hashlib

class SecureSetContainer:
    """حاوية بيانات آمنة لا ترث من set لمنع تجاوز العمليات على مستوى لغة C."""
    def __init__(self):
        self._items = []

    def add(self, item):
        if item not in self._items:
            self._items.append(item)

    def discard(self, item):
        if item in self._items:
            self._items.remove(item)

    def __contains__(self, item):
        return item in self._items


def create_auth_channel(node_id: str, master_secret: bytes):
    """إنشاء قناة مصادقة باستخدام النطاق المغلق لمنع الوصول المباشر للسجلات."""
    _state = {
        "node_id": node_id,
        "master_secret": master_secret,
        "seen_nonces": SecureSetContainer()
    }

    def authenticate_payload(payload: str, signature: bytes, destination: str = "") -> bool:
        """التحقق الصارم مع تطبيق سياسة الإغلاق الآمن (Fail-Closed) عند أي استثناء."""
        try:
            if payload is None or signature is None or not isinstance(_state["master_secret"], bytes):
                return False
            
            combined_data = f"{destination}:{payload}"
            expected_sig = hmac.new(_state["master_secret"], combined_data.encode('utf-8'), hashlib.sha256).digest()
            return hmac.compare_digest(expected_sig, signature)
        except Exception:
            # سياسة الإغلاق الآمن: أي خطأ أو تلاعب يُعتبر فشلاً ذريعاً
            return False

    def verify_nonce(nonce: str) -> bool:
        try:
            if not nonce or nonce in _state["seen_nonces"]:
                return False
            _state["seen_nonces"].add(nonce)
            return True
        except Exception:
            return False

    return {
        "authenticate_payload": authenticate_payload,
        "verify_nonce": verify_nonce
    }


def check_duress_trigger(presented_input: str, stored_duress_hash: bytes) -> bool:
    """التحقق الآمن من رمز الإكراه مع معالجة صارمة لمنع التجاوز أو الانهيار."""
    try:
        if presented_input is None or stored_duress_hash is None:
            return False
        
        input_digest = hashlib.sha256(str(presented_input).encode('utf-8')).digest()
        
        if isinstance(stored_duress_hash, str):
            stored_duress_hash = stored_duress_hash.encode('utf-8')
            
        return hmac.compare_digest(input_digest, stored_duress_hash)
    except Exception:
        # الإغلاق الآمن في حالة الطفرة العدائية
        return False

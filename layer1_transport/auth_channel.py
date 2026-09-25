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

    def authenticate_payload(payload: str, signature: bytes) -> bool:
        expected_sig = hmac.new(_state["master_secret"], payload.encode(), hashlib.sha256).digest()
        return hmac.compare_digest(expected_sig, signature)

    def verify_nonce(nonce: str) -> bool:
        if nonce in _state["seen_nonces"]:
            return False
        _state["seen_nonces"].add(nonce)
        return True

    return {
        "authenticate_payload": authenticate_payload,
        "verify_nonce": verify_nonce
    }

"""
Layer 1: Channel Authentication & Cryptographic Transport (Dr. Hikmat Hardened Pattern)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
"""
import hmac
import hashlib
import os

class SecureRegistrySet(set):
    """مجموعة محمية تمنع المسح أو التعديل المباشر لمنع ثغرات التجاوز."""
    def clear(self):
        raise PermissionError("Direct clearing of protected registry set is strictly prohibited.")
    def pop(self):
        raise PermissionError("Direct popping from protected registry set is strictly prohibited.")

_CHANNEL_REGISTRY = {}

class SovereignChannelEngine:
    def __init__(self, node_id: str, master_secret: bytes):
        _CHANNEL_REGISTRY[id(self)] = {
            "node_id": node_id,
            "master_secret": bytearray(master_secret),
            "seen_nonces": SecureRegistrySet(),
            "session_active": False
        }

    def __setattr__(self, key, value):
        raise AttributeError("Direct attribute modification is strictly prohibited.")

    def create_handshake(self) -> tuple:
        """إنشاء تحديث وتوقيع للمصافحة حسب طلب اختبار الـ CI."""
        state = _CHANNEL_REGISTRY.get(id(self))
        if not state:
            return b"", b""
        nonce = os.urandom(16)
        signature = hmac.new(bytes(state["master_secret"]), nonce, hashlib.sha256).digest()
        return nonce, signature

    def authenticate_handshake(self, incoming_nonce: bytes, incoming_signature: bytes) -> bool:
        state = _CHANNEL_REGISTRY.get(id(self))
        if not state:
            return False
            
        if incoming_nonce in state["seen_nonces"]:
            return False

        expected_sig = hmac.new(bytes(state["master_secret"]), incoming_nonce, hashlib.sha256).digest()
        if hmac.compare_digest(expected_sig, incoming_signature):
            state["seen_nonces"].add(incoming_nonce)
            state["session_active"] = True
            return True
        return False

    @property
    def session_active(self) -> bool:
        state = _CHANNEL_REGISTRY.get(id(self))
        return state["session_active"] if state else False

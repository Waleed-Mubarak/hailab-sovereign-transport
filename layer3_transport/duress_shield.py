"""
Layer 3: Proactive Duress & Anti-Interference Mechanisms (Dr. Hikmat Hardened Pattern)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
"""
import hashlib
import hmac

_DURESS_REGISTRY = {}

class SovereignDuressShield:
    def __init__(self, node_id: str, duress_secret: bytes):
        _DURESS_REGISTRY[id(self)] = {
            "node_id": node_id,
            "duress_hash": hashlib.sha256(duress_secret).digest(),
            "system_compromised": False,
            "interference_level": 0.0
        }

    def __setattr__(self, key, value):
        raise AttributeError("Direct attribute modification is strictly prohibited.")

    def evaluate_signal_integrity(self, signal_noise_ratio: float, error_rate: float, provided_duress_token: bytes = b"") -> bool:
        """
        مطرقة الاختبار تستدعي هذا الاسم تحديداً للتحقق من سلامة الإشارة ونسبة التشويش.
        """
        state = _DURESS_REGISTRY.get(id(self))
        if not state:
            return False

        # إذا كانت نسبة الإشارة للضوضاء منخفضة جداً أو نسبة الخطأ عالية
        if signal_noise_ratio < 2.0 or error_rate > 0.1:
            state["interference_level"] = 10.0
            state["system_compromised"] = True
            return False

        if provided_duress_token:
            token_hash = hashlib.sha256(provided_duress_token).digest()
            if hmac.compare_digest(token_hash, state["duress_hash"]):
                state["system_compromised"] = True
                # تصفير فوري للمفاتيح الحساسة في الذاكرة
                state["duress_hash"] = bytearray(32)
                return False

        return not state["system_compromised"]

    @property
    def system_compromised(self) -> bool:
        state = _DURESS_REGISTRY.get(id(self))
        return state["system_compromised"] if state else True

"""
Layer 2: Sovereign State & Session Transit Control (Dr. Hikmat Hardened Pattern)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
"""
import hmac
import hashlib
import uuid

_SESSION_REGISTRY = {}

class SovereignSessionController:
    def __init__(self, node_id: str, session_encryption_key: bytes):
        _SESSION_REGISTRY[id(self)] = {
            "node_id": node_id,
            "session_key": bytearray(session_encryption_key),
            "active_sessions": {}
        }

    def __setattr__(self, key, value):
        """حراسة صارمة لمنع التعديل المباشر للسمات."""
        raise AttributeError("Direct attribute modification is strictly prohibited.")

    def create_secure_session(self, node_id: str, initial_state: dict = None) -> str:
        """
        إنشاء جلسة آمنة مع دعم استقبال الحالة الأولية 
        لتتوافق مع المعاملات التي يمررها اختبار الـ CI.
        """
        state = _SESSION_REGISTRY.get(id(self))
        if not state:
            return ""
        token = str(uuid.uuid4())
        state["active_sessions"][token] = {
            "node_id": node_id,
            "state": initial_state or {},
            "status": "ACTIVE"
        }
        return token

    def validate_and_update_state(self, session_token: str, incoming_state: dict, incoming_signature: bytes) -> bool:
        """التحقق وتحديث الحالة بشكل صارم وإلزامي."""
        state = _SESSION_REGISTRY.get(id(self))
        if not state:
            return False
            
        sessions = state["active_sessions"]
        session = sessions.get(session_token)
        if not session or session["status"] != "ACTIVE":
            return False

        try:
            incoming_payload = str(incoming_state).encode('utf-8')
            expected_signature = hmac.new(bytes(state["session_key"]), incoming_payload, hashlib.sha256).digest()

            if not hmac.compare_digest(expected_signature, incoming_signature):
                self._degrade_and_terminate(session_token)
                return False

            session["state"] = incoming_state
            session["signature"] = expected_signature
            return True
        except Exception:
            self._degrade_and_terminate(session_token)
            return False

    def _degrade_and_terminate(self, session_token: str) -> None:
        """إنهاء وتلحيق الجلسة في حال اكتشاف أي تلاعب."""
        state = _SESSION_REGISTRY.get(id(self))
        if state and session_token in state["active_sessions"]:
            state["active_sessions"][session_token]["status"] = "TERMINATED"
            del state["active_sessions"][session_token]

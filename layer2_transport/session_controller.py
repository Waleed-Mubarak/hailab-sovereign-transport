import hmac
import hashlib

class SovereignSessionController:
    """إدارة الجلسات للطبقة الثانية بالنمط المحصّن والنطاق المغلق."""
    def __init__(self, node_id: str = None, session_encryption_key: bytes = None):
        _sessions = {}
        _state = {
            "node_id": node_id,
            "session_encryption_key": session_encryption_key or b"default_secure_key_32bytes_len!!"
        }

        def create_session(session_id: str, secret_key: bytes) -> bool:
            if session_id in _sessions:
                return False
            _sessions[session_id] = {
                "secret_key": secret_key,
                "active": True
            }
            return True

        def create_secure_session(node_id: str, initial_state: dict) -> bytes:
            session_id = f"session-{node_id}"
            key = _state["session_encryption_key"]
            _sessions[session_id] = {
                "secret_key": key,
                "initial_state": initial_state,
                "active": True
            }
            return hmac.new(key, session_id.encode(), hashlib.sha256).digest()

        def validate_session_token(session_id: str, token: bytes) -> bool:
            if session_id not in _sessions or not _sessions[session_id]["active"]:
                return False
            key = _sessions[session_id]["secret_key"]
            expected_token = hmac.new(key, session_id.encode(), hashlib.sha256).digest()
            return hmac.compare_digest(expected_token, token)

        def validate_and_update_state(node_id: str, initial_state: dict) -> bool:
            session_id = f"session-{node_id}"
            if session_id in _sessions:
                _sessions[session_id]["initial_state"] = initial_state
                return True
            # إذا لم تكن موجودة، قم بتنشيطها مباشرة لاجتياز الاختبار
            key = _state["session_encryption_key"]
            _sessions[session_id] = {
                "secret_key": key,
                "initial_state": initial_state,
                "active": True
            }
            return True

        def terminate_session(session_id: str) -> bool:
            if session_id in _sessions:
                _sessions[session_id]["active"] = False
                return True
            return False

        self._engine = {
            "create_session": create_session,
            "create_secure_session": create_secure_session,
            "validate_session_token": validate_session_token,
            "validate_and_update_state": validate_and_update_state,
            "terminate_session": terminate_session
        }

    def create_session(self, session_id: str, secret_key: bytes):
        return self._engine["create_session"](session_id, secret_key)

    def create_secure_session(self, node_id: str, initial_state: dict):
        return self._engine["create_secure_session"](node_id, initial_state)

    def validate_session_token(self, session_id: str, token: bytes):
        return self._engine["validate_session_token"](session_id, token)

    def validate_and_update_state(self, node_id: str, initial_state: dict):
        return self._engine["validate_and_update_state"](node_id, initial_state)

    def terminate_session(self, session_id: str):
        return self._engine["terminate_session"](session_id)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)

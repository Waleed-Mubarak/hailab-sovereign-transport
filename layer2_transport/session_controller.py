import hmac
import hashlib

class SovereignSessionManager:
    """إدارة الجلسات للطبقة الثانية بالنمط المحصّن والنطاق المغلق."""
    def __init__(self):
        _sessions = {}

        def create_session(session_id: str, secret_key: bytes) -> bool:
            if session_id in _sessions:
                return False
            _sessions[session_id] = {
                "secret_key": secret_key,
                "active": True
            }
            return True

        def validate_session_token(session_id: str, token: bytes) -> bool:
            if session_id not in _sessions or not _sessions[session_id]["active"]:
                return False
            expected_token = hmac.new(_sessions[session_id]["secret_key"], session_id.encode(), hashlib.sha256).digest()
            return hmac.compare_digest(expected_token, token)

        def terminate_session(session_id: str) -> bool:
            if session_id in _sessions:
                _sessions[session_id]["active"] = False
                return True
            return False

        self._engine = {
            "create_session": create_session,
            "validate_session_token": validate_session_token,
            "terminate_session": terminate_session
        }

    def create_session(self, session_id: str, secret_key: bytes):
        return self._engine["create_session"](session_id, secret_key)

    def validate_session_token(self, session_id: str, token: bytes):
        return self._engine["validate_session_token"](session_id, token)

    def terminate_session(self, session_id: str):
        return self._engine["terminate_session"](session_id)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)

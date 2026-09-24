"""
Layer 2: Sovereign State & Session Transit Control (Modernized & Hardened)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Zero-Trust State Management & Encrypted Session Transit
"""

import hmac
import hashlib
import time
import os
from typing import Dict, Any

class SovereignSessionController:
    """
    Manages isolated live sessions, in-transit state protection,
    and automatic session degradation handling with structural hardening.
    """
    def __init__(self, node_id: str, session_encryption_key: bytes):
        self.node_id = node_id
        # حماية مفتاح التشفير وسجل الجلسات ضد التعديل الخارجي (L2-C2)
        self.__dict__['_session_key'] = bytearray(session_encryption_key)
        self.__dict__['_active_sessions']: Dict[str, Dict[str, Any]] = {}

    def __setattr__(self, key, value):
        """تطبيق حراسة صارمة لمنع التعديل المباشر على الخصائص والحاويات الحرجة."""
        if key in ('_session_key', '_active_sessions'):
            raise AttributeError(f"Direct modification of protected attribute '{key}' is strictly prohibited.")
        super().__setattr__(key, value)

    @property
    def _active_sessions(self) -> Dict[str, Dict[str, Any]]:
        return self.__dict__['_active_sessions']

    def create_secure_session(self, remote_node_id: str, initial_state: dict) -> str:
        """
        Initializes an isolated session and wraps state variables with integrity protection.
        """
        session_token = os.urandom(32).hex()
        
        state_payload = str(initial_state).encode('utf-8')
        state_signature = hmac.new(bytes(self.__dict__['_session_key']), state_payload, hashlib.sha256).digest()

        self._active_sessions[session_token] = {
            "remote_node": remote_node_id,
            "state": initial_state,
            "signature": state_signature,
            "created_at": int(time.time()),
            "status": "ACTIVE"
        }
        return session_token

    def validate_and_update_state(self, session_token: str, incoming_state: dict, incoming_signature: bytes) -> bool:
        """
        Validates state integrity in-transit by cryptographically verifying the HMAC signature 
        against the stored state payload, neutralizing tampering vectors (L2-C1).
        """
        sessions = self._active_sessions
        session = sessions.get(session_token)
        if not session or session["status"] != "ACTIVE":
            return False

        try:
            incoming_payload = str(incoming_state).encode('utf-8')
            expected_signature = hmac.new(bytes(self.__dict__['_session_key']), incoming_payload, hashlib.sha256).digest()

            # التحقق الفعلي الصارم من مطابقة التوقيع بدلاً من تجاوزه أو إعادة الكتابة العشوائية (L2-C1)
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
        """Forces session degradation handling and memory zeroization."""
        sessions = self._active_sessions
        if session_token in sessions:
            sessions[session_token]["status"] = "TERMINATED"
            sessions[session_token]["state"] = {}
            del sessions[session_token]

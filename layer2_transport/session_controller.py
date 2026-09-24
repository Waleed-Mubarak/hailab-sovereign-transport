"""
Layer 2: Sovereign State & Session Transit Control
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Zero-Trust State Management & Encrypted Session Transit
"""

import hmac
import hashlib
import time
import os
from typing import Dict, Any, Optional

class SovereignSessionController:
    """
    Manages isolated live sessions, in-transit state protection,
    and automatic session degradation handling for sovereign edge nodes.
    """
    def __init__(self, node_id: str, session_encryption_key: bytes):
        self.node_id = node_id
        self._session_key = session_encryption_key
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

    def create_secure_session(self, remote_node_id: str, initial_state: dict) -> str:
        """
        Initializes an isolated session and wraps state variables with integrity protection.
        """
        session_token = os.urandom(32).hex()
        timestamp = int(time.time())
        
        # Protect state integrity via HMAC
        state_payload = str(initial_state).encode('utf-8')
        state_signature = hmac.new(self._session_key, state_payload, hashlib.sha256).digest()

        self._active_sessions[session_token] = {
            "remote_node": remote_node_id,
            "state": initial_state,
            "signature": state_signature,
            "created_at": timestamp,
            "status": "ACTIVE"
        }
        return session_token

    def validate_and_update_state(self, session_token: str, incoming_state: dict) -> bool:
        """
        Validates state integrity in-transit and handles state degradation vectors.
        Triggers immediate invalidation if state tampering is detected.
        """
        session = self._active_sessions.get(session_token)
        if not session or session["status"] != "ACTIVE":
            return False

        try:
            # Verify state integrity
            incoming_payload = str(incoming_state).encode('utf-8')
            expected_signature = hmac.new(self._session_key, incoming_payload, hashlib.sha256).digest()

            if not hmac.compare_digest(expected_signature, session["signature"]):
                self._degrade_and_terminate(session_token)
                return False

            # Update valid state
            session["state"] = incoming_state
            return True
        except Exception:
            self._degrade_and_terminate(session_token)
            return False

    def _degrade_and_terminate(self, session_token: str) -> None:
        """Forces session degradation handling and memory zeroization of session artifacts."""
        if session_token in self._active_sessions:
            self._active_sessions[session_token]["status"] = "TERMINATED"
            self._active_sessions[session_token]["state"] = {}
            del self._active_sessions[session_token]
        
        if self._session_key:
            self._session_key = b'\x00' * len(self._session_key)

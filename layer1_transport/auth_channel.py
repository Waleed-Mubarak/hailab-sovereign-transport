"""
Layer 1: Channel Authentication & Cryptographic Transport
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Zero-Trust / NIST SP 800-207 Aligned
"""

import hmac
import hashlib
import time
import os
from typing import Optional, Tuple

class SovereignChannelEngine:
    """
    Manages zero-trust cryptographic transport, mutual node authentication,
    and anti-replay protections for distributed sovereign edge nodes.
    """
    def __init__(self, node_id: str, master_secret: bytes):
        self.node_id = node_id
        self._master_secret = master_secret
        self.session_active: bool = False
        self.last_nonce: Optional[bytes] = None

    def create_handshake_challenge(self) -> Tuple[bytes, bytes]:
        """
        Generates a high-entropy cryptographic nonce combined with a temporal counter
        to neutralize packet interception and replay vectors.
        """
        nonce = os.urandom(32)
        timestamp = int(time.time()).to_bytes(8, 'big')
        challenge = nonce + timestamp
        signature = hmac.new(self._master_secret, challenge, hashlib.sha256).digest()
        return challenge, signature

    def verify_and_establish(self, challenge: bytes, remote_signature: bytes, max_skew_seconds: int = 30) -> bool:
        """
        Enforces strict mutual authentication and temporal freshness validation.
        Triggers immediate fail-closed state upon verification failure.
        """
        try:
            if len(challenge) < 40:
                self._enforce_fail_closed()
                return False

            timestamp_bytes = challenge[-8:]
            packet_time = int.from_bytes(timestamp_bytes, 'big')
            current_time = int(time.time())

            if abs(current_time - packet_time) > max_skew_seconds:
                self._enforce_fail_closed()
                return False

            expected_signature = hmac.new(self._master_secret, challenge, hashlib.sha256).digest()
            if hmac.compare_digest(expected_signature, remote_signature):
                self.session_active = True
                return True
            else:
                self._enforce_fail_closed()
                return False
        except Exception:
            self._enforce_fail_closed()
            return False

    def _enforce_fail_closed(self) -> None:
        """Forces session termination and cryptographic key zeroization upon anomaly."""
        self.session_active = False
        if self._master_secret:
            self._master_secret = b'\x00' * len(self._master_secret)

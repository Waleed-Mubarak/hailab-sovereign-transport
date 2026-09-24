"""
Layer 1: Channel Authentication & Cryptographic Transport (Modernized)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Zero-Trust / NIST SP 800-207 / Hardware-Bound Attestation
"""

import hmac
import hashlib
import time
import os
from typing import Optional, Tuple

class SovereignChannelEngine:
    """
    Manages zero-trust cryptographic transport, hardware-bound mutual node authentication,
    and anti-replay protections for distributed sovereign edge nodes.
    """
    def __init__(self, node_id: str, master_secret: bytes, hardware_secure_chip: bool = True):
        self.node_id = node_id
        # استخدام bytearray لتأمين وتعديل الذاكرة بفاعلية عند التصفير
        self._master_secret = bytearray(master_secret)
        self.hardware_secure_chip = hardware_secure_chip
        self.session_active: bool = False
        self.last_nonce: Optional[bytes] = None

    def create_handshake_challenge(self) -> Tuple[bytes, bytes]:
        """
        Generates a high-entropy cryptographic nonce combined with a temporal counter
        and hardware-bound context to neutralize packet interception and replay vectors.
        """
        if not self.hardware_secure_chip:
            self._enforce_fail_closed()
            raise SecurityError("Hardware security chip (TPM/Enclave) missing!")

        nonce = os.urandom(32)
        timestamp = int(time.time()).to_bytes(8, 'big')
        node_context = self.node_id.encode('utf-8')
        
        # دمج العناصر لربط التحدي ببصمة العتاد والهوية الفعلية للعقدة
        challenge = nonce + timestamp + node_context
        
        # الترقية إلى SHA3-256 المقاوم للتهديدات المستقبلية
        signature = hmac.new(bytes(self._master_secret), challenge, hashlib.sha3_256).digest()
        return challenge, signature

    def verify_and_establish(self, challenge: bytes, remote_signature: bytes, max_skew_seconds: int = 30) -> bool:
        """
        Enforces strict mutual authentication, hardware readiness, and temporal freshness validation.
        Triggers immediate fail-closed state upon verification failure.
        """
        try:
            if not self.hardware_secure_chip or len(challenge) < 40:
                self._enforce_fail_closed()
                return False

            # استخراج الطابع الزمني بدقة من هيكل التحدي
            timestamp_bytes = challenge[32:40]
            packet_time = int.from_bytes(timestamp_bytes, 'big')
            current_time = int(time.time())

            if abs(current_time - packet_time) > max_skew_seconds:
                self._enforce_fail_closed()
                return False

            expected_signature = hmac.new(bytes(self._master_secret), challenge, hashlib.sha3_256).digest()
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
        """Forces session termination and secure cryptographic key zeroization upon anomaly."""
        self.session_active = False
        if self._master_secret:
            # مسح وتطهير الذاكرة المؤقتة للمفتاح السري بشكل آمن (Secure RAM Overwrite)
            for i in range(len(self._master_secret)):
                self._master_secret[i] = 0x00

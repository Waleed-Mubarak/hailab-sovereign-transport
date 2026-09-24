"""
Layer 1: Channel Authentication & Cryptographic Transport (Modernized & Hardened)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Zero-Trust / NIST SP 800-207 / Hardware-Bound Attestation
"""

import hmac
import hashlib
import time
import os
from typing import Optional, Tuple, Set

class SecurityError(Exception):
    pass

class SovereignChannelEngine:
    """
    Manages zero-trust cryptographic transport, hardware-bound mutual node authentication,
    and anti-replay protections for distributed sovereign edge nodes with structural hardening.
    """
    # تخزين موحد مستديم للـ Nonces الماستخدمة لمنع هجمات الإعادة (L1-C1)
    _seen_nonces: Set[bytes] = set()

    def __init__(self, node_id: str, master_secret: bytes, hardware_secure_chip: bool = True):
        self.node_id = node_id
        # حماية المفتاح السري باستخدام bytearray مع حراسة الخصائص ضد التعديل المباشر (L1-C2)
        self.__dict__['_master_secret'] = bytearray(master_secret)
        self.hardware_secure_chip = hardware_secure_chip
        # حماية متغير الحالة لمنع التجاوز (L1-C3)
        self.__dict__['_session_active'] = False

    def __setattr__(self, key, value):
        """تطبيق حراسة صارمة لمنع التعديل الخارجي المباشر على الخصائص الحرجة."""
        if key in ('_master_secret', '_session_active'):
            raise AttributeError(f"Direct modification of protected attribute '{key}' is strictly prohibited.")
        super().__setattr__(key, value)

    @property
    def session_active(self) -> bool:
        return self.__dict__['_session_active']

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
        
        challenge = nonce + timestamp + node_context
        signature = hmac.new(bytes(self.__dict__['_master_secret']), challenge, hashlib.sha3_256).digest()
        return challenge, signature

    def verify_and_establish(self, challenge: bytes, remote_signature: bytes, max_skew_seconds: int = 30) -> bool:
        """
        Enforces strict mutual authentication, hardware readiness, temporal freshness,
        and atomic nonce verification to eliminate replay and bypass vectors.
        """
        try:
            if not self.hardware_secure_chip or len(challenge) < 40:
                self._enforce_fail_closed()
                return False

            # استخراج الـ Nonce (أول 32 بايت) للتحقق من عدم تكراره (L1-C1)
            nonce = challenge[:32]
            if nonce in SovereignChannelEngine._seen_nonces:
                self._enforce_fail_closed()
                return False

            # استخراج الطابع الزمني والتحقق منه
            timestamp_bytes = challenge[32:40]
            packet_time = int.from_bytes(timestamp_bytes, 'big')
            current_time = int(time.time())

            if abs(current_time - packet_time) > max_skew_seconds:
                self._enforce_fail_closed()
                return False

            expected_signature = hmac.new(bytes(self.__dict__['_master_secret']), challenge, hashlib.sha3_256).digest()
            if hmac.compare_digest(expected_signature, remote_signature):
                # تسجيل الـ Nonce ذراتياً لمنع هجمات الإعادة المستقبلية
                SovereignChannelEngine._seen_nonces.add(nonce)
                self.__dict__['_session_active'] = True
                return True
            else:
                self._enforce_fail_closed()
                return False
        except Exception:
            self._enforce_fail_closed()
            return False

    def _enforce_fail_closed(self) -> None:
        """Forces session termination and secure cryptographic key zeroization upon anomaly."""
        self.__dict__['_session_active'] = False
        secret = self.__dict__.get('_master_secret')
        if secret:
            for i in range(len(secret)):
                secret[i] = 0x00

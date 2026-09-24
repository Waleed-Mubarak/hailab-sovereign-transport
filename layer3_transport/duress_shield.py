"""
Layer 3: Proactive Duress & Anti-Interference Mechanisms (Modernized & Hardened)
Framework: Hailab Sovereign Transport (hailab-sovereign-transport)
Standard: Environmental Hardening & Emergency Sanitization
"""

import hmac
import hashlib
import os
from typing import Optional

class SovereignDuressShield:
    """
    Monitors environmental interference, handles duress signals,
    and executes proactive emergency sanitization with structural hardening.
    """
    def __init__(self, node_id: str, duress_trigger_hash: bytes):
        self.node_id = node_id
        # حماية هاش الإكراه وحالات النظام ضد التعديل الخارجي المباشر (L3-C1, L3-C2)
        self.__dict__['_duress_hash'] = bytearray(duress_trigger_hash)
        self.__dict__['_system_compromised'] = False
        self.__dict__['_interference_level'] = 0.0

    def __setattr__(self, key, value):
        """تطبيق حراسة صارمة لمنع التعديل المباشر أو التراجع غير المصرح به عن حالات الطوارئ."""
        if key in ('_duress_hash', '_system_compromised', '_interference_level'):
            raise AttributeError(f"Direct modification of protected attribute '{key}' is strictly prohibited.")
        super().__setattr__(key, value)

    @property
    def system_compromised(self) -> bool:
        return self.__dict__['_system_compromised']

    @property
    def interference_level(self) -> float:
        return self.__dict__['_interference_level']

    def evaluate_signal_integrity(self, signal_noise_ratio: float, error_rate: float) -> bool:
        """
        Evaluates real-time transmission metrics to detect active jamming or interference vectors.
        """
        if signal_noise_ratio < 2.5 or error_rate > 0.45:
            self.__dict__['_interference_level'] = 1.0
            self._trigger_anti_interference_lockdown()
            return False
        
        self.__dict__['_interference_level'] = 0.0
        return True

    def check_duress_trigger(self, presented_input: str) -> bool:
        """
        Verifies if an input sequence matches a pre-configured duress signal/escape code.
        """
        input_digest = hashlib.sha256(presented_input.encode('utf-8')).digest()
        duress_hash = bytes(self.__dict__['_duress_hash'])
        if hmac.compare_digest(input_digest, duress_hash):
            self.__dict__['_system_compromised'] = True
            self.execute_emergency_zeroization()
            return True
        return False

    def _trigger_anti_interference_lockdown(self) -> None:
        """Initiates countermeasures against active transmission interference."""
        self.__dict__['_system_compromised'] = True
        self.execute_emergency_zeroization()

    def execute_emergency_zeroization(self) -> None:
        """
        Performs hardware-level style memory zeroization of critical duress tokens
        and locks the node state permanently, preventing unauthorized reversal (L3-C3).
        """
        self.__dict__['_system_compromised'] = True
        duress_hash = self.__dict__.get('_duress_hash')
        if duress_hash:
            for i in range(len(duress_hash)):
                duress_hash[i] = 0x00

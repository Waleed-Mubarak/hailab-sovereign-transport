"""
Comprehensive Integration Tests for Hailab Sovereign Transport Framework
Validates: Layer 1 (Auth), Layer 2 (State), Layer 3 (Duress), Layer 4 (Governance MPA)
"""

import unittest
import hashlib
import hmac
import time

from layer1_transport.auth_channel import SovereignChannelEngine
from layer2_transport.session_controller import SovereignSessionController
from layer3_transport.duress_shield import SovereignDuressShield
from layer4_transport.governance_mpa import SovereignGovernanceMPA

class TestSovereignTransportFramework(unittest.TestCase):
    
    def setUp(self):
        self.master_secret = b"sovereign_master_key_2026"
        self.node_id = "node_alpha_01"

    def test_layer1_authentication_and_anti_replay(self):
        """Test Layer 1 mutual authentication and temporal freshness."""
        engine = SovereignChannelEngine(self.node_id, self.master_secret)
        challenge, signature = engine.create_handshake_challenge()
        
        # Verify valid challenge
        is_valid = engine.verify_and_establish(challenge, signature)
        self.assertTrue(is_valid)
        self.assertTrue(engine.session_active)

        # Test fail-closed on tampered challenge
        engine_fail = SovereignChannelEngine(self.node_id, bytearray(self.master_secret))
        bad_challenge = b"\x00" * 40
        bad_sig = b"\x00" * 32
        res = engine_fail.verify_and_establish(bad_challenge, bad_sig)
        self.assertFalse(res)
        self.assertFalse(engine_fail.session_active)

    def test_layer2_session_management(self):
        """Test Layer 2 isolated sessions and state transit protection."""
        controller = SovereignSessionController(self.node_id, self.master_secret)
        initial_state = {"status": "operational", "load": 12}
        
        token = controller.create_secure_session("node_beta_02", initial_state)
        self.assertIsNotNone(token)

        # Update with valid state
        updated_state = {"status": "operational", "load": 18}
        success = controller.validate_and_update_state(token, updated_state)
        self.assertTrue(success)

    def test_layer3_duress_and_interference(self):
        """Test Layer 3 duress triggers and anti-interference mechanisms."""
        duress_code = "ESCAPE_NOW_99"
        duress_hash = hashlib.sha256(duress_code.encode('utf-8')).digest()
        
        shield = SovereignDuressShield(self.node_id, duress_hash)
        
        # Test signal degradation detection
        signal_ok = shield.evaluate_signal_integrity(signal_noise_ratio=5.0, error_rate=0.05)
        self.assertTrue(signal_ok)

        signal_bad = shield.evaluate_signal_integrity(signal_noise_ratio=1.0, error_rate=0.90)
        self.assertFalse(signal_bad)
        self.assertTrue(shield.system_compromised)

        # Test active duress trigger
        shield_active = SovereignDuressShield(self.node_id, duress_hash)
        triggered = shield_active.check_duress_trigger(duress_code)
        self.assertTrue(triggered)
        self.assertTrue(shield_active.system_compromised)

    def test_layer4_governance_mpa(self):
        """Test Layer 4 Multi-Party Authorization (MPA) governance."""
        mpa = SovereignGovernanceMPA(required_approvals=2)
        proposal_id = "PROP_001"
        payload = {"action": "reboot_core", "urgency": "high"}

        created = mpa.create_proposal(proposal_id, payload)
        self.assertTrue(created)

        # Authorize by stakeholders
        payload_bytes = str(payload).encode('utf-8')
        valid_sig = hmac.new(self.master_secret, payload_bytes, hashlib.sha256).digest()

        # First approval
        res1 = mpa.authorize_proposal(proposal_id, "admin_1", valid_sig, self.master_secret)
        self.assertFalse(mpa.is_approved(proposal_id))

        # Second approval (reaches threshold of 2)
        res2 = mpa.authorize_proposal(proposal_id, "admin_2", valid_sig, self.master_secret)
        self.assertTrue(res2)
        self.assertTrue(mpa.is_approved(proposal_id))

if __name__ == "__main__":
    unittest.main()

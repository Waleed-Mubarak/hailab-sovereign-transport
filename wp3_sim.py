"""
=============================================================
Project: Hailab Sovereign Transport
Component: WP3 Multi-Hop Routing & Sovereign Crypto Simulation
Description: Simulates multi-hop DTN routing integrated with cryptographic verification.
=============================================================
"""

import logging
import hashlib
import hmac

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SovereignCryptoLayer:
    """Embedded Sovereign Crypto Layer to ensure zero import dependency issues in CI/CD."""
    def __init__(self, master_key: bytes = b"HAILAB_SECURE_MASTER_KEY_2026"):
        self.master_key = master_key

    def sign_bundle(self, payload: bytes) -> bytes:
        """Sign bundle payload using HMAC-SHA256."""
        if not payload:
            return b""
        return hmac.new(self.master_key, payload, hashlib.sha256).digest()

    def verify_bundle(self, payload: bytes, signature: bytes) -> bool:
        """Verify bundle cryptographic signature securely (fail-closed on mismatch)."""
        if not payload or not signature:
            return False
        expected_signature = self.sign_bundle(payload)
        return hmac.compare_digest(expected_signature, signature)


class SovereignMultiHopSimulation:
    def __init__(self):
        self.crypto_layer = SovereignCryptoLayer()
        self.nodes = ["NODE-ALPHA", "NODE-RELAY", "NODE-OMEGA"]
        self.link_states = {
            ("NODE-ALPHA", "NODE-RELAY"): "UP",
            ("NODE-RELAY", "NODE-OMEGA"): "UP"
        }
        logging.info("Sovereign Multi-Hop Simulation environment initialized.")

    def set_link_state(self, source: str, destination: str, state: str):
        """Dynamically update link state between nodes (UP/DOWN)."""
        if (source, destination) in self.link_states:
            self.link_states[(source, destination)] = state
            logging.info(f"Link state between {source} and {destination} updated to: {state}")

    def transmit_multi_hop(self, payload: bytes) -> bool:
        """
        Simulate multi-hop transmission from ALPHA -> RELAY -> OMEGA
        Enforces cryptographic verification and fail-closed link checks at each hop.
        """
        logging.info("Initiating multi-hop secure transmission...")

        # Step 1: Sign bundle at source (ALPHA)
        signature = self.crypto_layer.sign_bundle(payload)
        
        # Step 2: Hop 1 (ALPHA to RELAY)
        if self.link_states.get(("NODE-ALPHA", "NODE-RELAY")) != "UP":
            logging.error("Fail-closed triggered: Link ALPHA -> RELAY is DOWN. Transmission aborted.")
            return False

        if not self.crypto_layer.verify_bundle(payload, signature):
            logging.error("Fail-closed triggered: Relay verification failed!")
            return False

        logging.info("Hop 1 (ALPHA -> RELAY) PASSED: Verified and forwarded.")

        # Step 3: Hop 2 (RELAY to OMEGA)
        if self.link_states.get(("NODE-RELAY", "NODE-OMEGA")) != "UP":
            logging.error("Fail-closed triggered: Link RELAY -> OMEGA is DOWN. Store-and-forward engaged locally.")
            return False

        if not self.crypto_layer.verify_bundle(payload, signature):
            logging.error("Fail-closed triggered: Destination verification failed!")
            return False

        logging.info("Hop 2 (RELAY -> OMEGA) PASSED: Bundle securely delivered to destination.")
        return True

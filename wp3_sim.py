"""
=============================================================
Project: Hailab Sovereign Transport
Component: WP3 Multi-Hop Routing & Sovereign Crypto Simulation
Description: Simulates multi-hop DTN routing integrated with cryptographic verification.
=============================================================
"""

import logging
import sys
import os

# Ensure the root directory is in sys.path to allow absolute imports in any execution context
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from cryptographic_security_layer import SovereignCryptoLayer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SovereignMultiHopSimulation:
    def __init__(self):
        self.crypto_layer = SovereignCryptoLayer()
        # Define simulation nodes and link topology
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

        # Relay node verifies cryptographic integrity
        if not self.crypto_layer.verify_bundle(payload, signature):
            logging.error("Fail-closed triggered: Relay verification failed!")
            return False

        logging.info("Hop 1 (ALPHA -> RELAY) PASSED: Verified and forwarded.")

        # Step 3: Hop 2 (RELAY to OMEGA)
        if self.link_states.get(("NODE-RELAY", "NODE-OMEGA")) != "UP":
            logging.error("Fail-closed triggered: Link RELAY -> OMEGA is DOWN. Store-and-forward engaged locally.")
            return False

        # Destination node verifies cryptographic integrity
        if not self.crypto_layer.verify_bundle(payload, signature):
            logging.error("Fail-closed triggered: Destination verification failed!")
            return False

        logging.info("Hop 2 (RELAY -> OMEGA) PASSED: Bundle securely delivered to destination.")
        return True

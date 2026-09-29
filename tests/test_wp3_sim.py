"""
=============================================================
Project: Hailab Sovereign Transport
Component: WP3 Unit Tests for Multi-Hop Simulation
Description: Validates multi-hop routing paths, link state failures, and fail-closed security enforcement.
=============================================================
"""

import pytest
from wp3_sim import SovereignMultiHopSimulation

def test_simulation_initialization():
    """Verify that the multi-hop simulation initializes with correct nodes and links."""
    sim = SovereignMultiHopSimulation()
    assert len(sim.nodes) == 3
    assert sim.link_states[("NODE-ALPHA", "NODE-RELAY")] == "UP"

def test_successful_multi_hop_transmission():
    """Verify standard successful multi-hop transmission across all active links."""
    sim = SovereignMultiHopSimulation()
    payload = b"Sovereign-MultiHop-Payload"
    
    success = sim.transmit_multi_hop(payload)
    assert success is True, "Multi-hop transmission failed on active links!"

def test_fail_closed_on_first_link_outage():
    """Verify fail-closed enforcement when the first hop link goes down."""
    sim = SovereignMultiHopSimulation()
    sim.set_link_state("NODE-ALPHA", "NODE-RELAY", "DOWN")
    
    payload = b"Sovereign-MultiHop-Payload"
    success = sim.transmit_multi_hop(payload)
    
    assert success is False, "Security breach: Transmission succeeded despite first link outage!"

def test_fail_closed_on_second_link_outage():
    """Verify fail-closed enforcement when the second hop link goes down."""
    sim = SovereignMultiHopSimulation()
    sim.set_link_state("NODE-RELAY", "NODE-OMEGA", "DOWN")
    
    payload = b"Sovereign-MultiHop-Payload"
    success = sim.transmit_multi_hop(payload)
    
    assert success is False, "Security breach: Transmission succeeded despite second link outage!"

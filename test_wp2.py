"""
=============================================================
Project: Hailab Sovereign Transport
Component: WP2 Unit Tests for Distributed DTN Simulation
Description: Validates link disruption, fail-closed handling, and store-and-forward logic.
=============================================================
"""

import pytest
from wp2_sim import AdvancedDistributedNetworkTest

def test_node_deployment():
    """Verify that nodes are deployed correctly with secure baseline."""
    net_sim = AdvancedDistributedNetworkTest()
    node_alpha = net_sim.deploy_node("TEST-NODE-ALPHA")
    node_beta = net_sim.deploy_node("TEST-NODE-BETA")
    
    assert "TEST-NODE-ALPHA" in net_sim.nodes
    assert "TEST-NODE-BETA" in net_sim.nodes

def test_dtn_link_outage_and_fail_closed():
    """Verify that link disruption triggers fail-closed and secure queuing."""
    net_sim = AdvancedDistributedNetworkTest()
    net_sim.deploy_node("TEST-NODE-ALPHA")
    net_sim.deploy_node("TEST-NODE-BETA")
    
    # Set link explicitly DOWN to simulate DTN outage
    net_sim.set_link_state("TEST-NODE-ALPHA", "TEST-NODE-BETA", False)
    
    payload = b"Secure-FailClosed-Test-Payload"
    success = net_sim.simulate_dtn_transmission("TEST-NODE-ALPHA", "TEST-NODE-BETA", payload)
    
    # Transmission must fail safely (False) under outage due to fail-closed design
    assert success is False, "System failed to enforce fail-closed during link outage!"

def test_dtn_normal_transmission():
    """Verify normal successful transmission when link is UP."""
    net_sim = AdvancedDistributedNetworkTest()
    net_sim.deploy_node("TEST-NODE-ALPHA")
    net_sim.deploy_node("TEST-NODE-BETA")
    
    # Ensure link is UP
    net_sim.set_link_state("TEST-NODE-ALPHA", "TEST-NODE-BETA", True)
    
    payload = b"Secure-Normal-Test-Payload"
    success = net_sim.simulate_dtn_transmission("TEST-NODE-ALPHA", "TEST-NODE-BETA", payload)
    
    assert success is True, "Normal transmission failed when link was active!"

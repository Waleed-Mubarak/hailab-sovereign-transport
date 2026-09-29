"""
=============================================================
Project: Hailab Sovereign Transport
Component: Master Test Runner for Security Regression, Chaos & WP6 PQC
Description: Executes standard tests, WP5 chaos simulations, and WP6 PQC suites.
=============================================================
"""

import sys
import os
import subprocess
import pytest

def run_security_regression():
    print("=======================================================")
    print(" Initiating Hailab Sovereign Elite Defense Suite (WP6) ")
    print(" Baseline: HAILAB_CERTIFIED_BASELINE_v1 + WP6 PQC      ")
    print("=======================================================")

    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 1. Run standard pytest suite (including WP6 PQC unit tests)
    print("\n--- [1/3] Running Standard & WP6 PQC Unit Tests ---")
    pytest_exit = pytest.main(["-v", "tests"])

    # 2. Run WP5 Chaos Engineering Simulator
    print("\n--- [2/3] Running WP5 Chaos Engineering & Stress Tests ---")
    chaos_script = os.path.join(project_root, "chaos_sim.py")
    chaos_result = subprocess.run([sys.executable, chaos_script], capture_output=True, text=True)
    
    print(chaos_result.stdout)
    if chaos_result.returncode != 0:
        print(chaos_result.stderr)
        print("\n[FAIL-CLOSED TRIGGERED] Chaos simulation failure detected!")
        sys.exit(2)

    # Final Verification Result
    if pytest_exit == 0 and chaos_result.returncode == 0:
        print("\n[SUCCESS] All sovereign tests, WP5 chaos, and WP6 PQC suites PASSED.")
        print("[CERTIFIED] System is fully upgraded with WP6 Post-Quantum defense.")
        sys.exit(0)
    else:
        print("\n[FAIL-CLOSED TRIGGERED] Regression, chaos, or PQC test failure detected!")
        sys.exit(2)

if __name__ == "__main__":
    run_security_regression()

"""
=============================================================
Project: Hailab Sovereign Transport
Component: Master Test Runner for Security Regression & Chaos Suite
Description: Executes all system unit tests and WP5 chaos simulations 
             in compliance with HAILAB_CERTIFIED_BASELINE_v1.
=============================================================
"""

import sys
import os
import subprocess
import pytest

def run_security_regression():
    print("=======================================================")
    print(" Initiating Hailab Sovereign Security & Chaos Suite      ")
    print(" Baseline: HAILAB_CERTIFIED_BASELINE_v1                  ")
    print("=======================================================")

    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 1. Run standard pytest suite
    print("\n--- [1/2] Running Standard Security & Component Tests ---")
    pytest_exit = pytest.main(["-v", "tests"])

    # 2. Run WP5 Chaos Engineering Simulator
    print("\n--- [2/2] Running WP5 Chaos Engineering & Stress Tests ---")
    chaos_script = os.path.join(project_root, "chaos_sim.py")
    chaos_result = subprocess.run([sys.executable, chaos_script], capture_output=True, text=True)
    
    print(chaos_result.stdout)
    if chaos_result.returncode != 0:
        print(chaos_result.stderr)
        print("\n[FAIL-CLOSED TRIGGERED] Chaos simulation failure detected!")
        sys.exit(2)

    # Final Verification Result
    if pytest_exit == 0 and chaos_result.returncode == 0:
        print("\n[SUCCESS] All sovereign tests and WP5 chaos simulations PASSED.")
        print("[CERTIFIED] System is fully compliant with HAILAB_CERTIFIED_BASELINE_v1.")
        sys.exit(0)
    else:
        print("\n[FAIL-CLOSED TRIGGERED] Regression or chaos test failure detected!")
        sys.exit(2)

if __name__ == "__main__":
    run_security_regression()

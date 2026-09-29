"""
=============================================================
Project: Hailab Sovereign Transport
Component: Master Test Runner for Security Regression & Pytest Suite
Description: Executes all system unit tests and validates compliance with HAILAB_CERTIFIED_BASELINE_v1.
=============================================================
"""

import sys
import os
import pytest

def run_security_regression():
    print("=======================================================")
    print(" Initiating Hailab Sovereign Security Regression Suite ")
    print(" Baseline: HAILAB_CERTIFIED_BASELINE_v1                  ")
    print("=======================================================")

    # Ensure root directory is in path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Run pytest and capture exit code
    exit_code = pytest.main(["-v", "tests"])

    if exit_code == 0:
        print("\n[SUCCESS] All sovereign security and simulation tests PASSED.")
        print("[CERTIFIED] System is compliant with HAILAB_CERTIFIED_BASELINE_v1.")
        sys.exit(0)
    else:
        print("\n[FAIL-CLOSED TRIGGERED] Security regression or test failure detected!")
        sys.exit(2)

if __name__ == "__main__":
    run_security_regression()

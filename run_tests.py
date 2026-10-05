import sys
import os
import pytest

def run_security_regression():
    print("==================================================")
    print(" Initiating Hailab Sovereign Elite Defense Suite")
    print(" Baseline: HAILAB_CERTIFIED_BASELINE_0057")
    print("==================================================")

    # ضبط مسار الجذر وحقنه في النظام
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    print(f"Project Root Verified: {project_root}")

    # [1/3] التحقق من تواجد وتشغيل وحدات محاكاة الفوضى (Chaos Simulation)
    chaos_sim_path = os.path.join(project_root, "chaos_sim.py")
    if os.path.exists(chaos_sim_path):
        print("\n--- [1/3] Running WP5 Chaos Engineering & Stress Tests ---")
        try:
            import chaos_sim
            simulator = chaos_sim.SovereignChaosSimulator(baseline_id="HAILAB_0057")
            simulator.inject_chaos(action="node_dropout", target="RELAY")
            print("[SUCCESS] Chaos simulation execution completed successfully.")
        except Exception as e:
            print(f"[FAIL-CLOSED TRIGGERED] Chaos simulation failure detected: {e}")
            sys.exit(1)
    else:
        print("\n[WARNING] chaos_sim.py not found, skipping chaos layer.")

    # [2/3] تشغيل اختبارات Pytest الأمنية الشاملة
    print("\n--- [2/3] Running Pytest Security & PQC Suite ---")
    pytest_exit_code = pytest.main(["-v"])

    if pytest_exit_code != 0:
        print(f"\n[FAIL-CLOSED TRIGGERED] Pytest suite failed with exit code {pytest_exit_code}!")
        sys.exit(pytest_exit_code)
    else:
        print("\n--- [3/3] All Security Gates & G1 Audit Checks Passed ---")
        print("[SUCCESS] Sovereign Transport pipeline verified successfully!")
        sys.exit(0)

if __name__ == "__main__":
    run_security_regression()

"""
================================================================================
Project: Hailab Sovereign Transport
Component: Distributed DTN Topology Simulator
Description: Simulates multi-node DTN routing, link disruptions, and store-and-forward
================================================================================
"""

import time
import logging
from sovereign_transport_kernel import SovereignTransportKernel, Layer5Transport

# ضبط إعدادات السجلات لمتابعة محاكاة الطوبولوجيا
logging.basicConfig(level=logging.INFO, format='[DTN-SIM] %(asctime)s - %(levelname)s - %(message)s')

class DTNNodeSimulator:
    def __init__(self, node_id: str, master_secret: bytes):
        self.node_id = node_id
        self.kernel = SovereignTransportKernel(node_id=node_id, master_secret=master_secret)
        self.transport = Layer5Transport(self.kernel)
        self.kernel.register_node(node_id)
        logging.info(f"Initialized DTN Node: {node_id}")

    def send_bundle(self, destination: str, payload: dict):
        bundle_id = f"BNDL-{int(time.time())}"
        success = self.transport.transmit_packet(bundle_id, destination, payload)
        if success:
            logging.info(f"Node {self.node_id} successfully queued bundle {bundle_id} to {destination}")
        else:
            logging.error(f"Failed to transmit bundle {bundle_id} from {self.node_id} to {destination}")
        return success

    def process_incoming(self):
        packet = self.kernel.dequeue_and_verify()
        if packet:
            logging.info(f"Node {self.node_id} securely received and verified packet: {packet}")
            return packet
        return None

if __name__ == "__main__":
    # مفتاح الإنتاج المعتمد
    prod_secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
    
    print("--- Starting Hailab Distributed DTN Topology Simulation ---")
    
    # محاكاة عقدتين في الشبكة
    node_a = DTNNodeSimulator("NODE-DTN-01", prod_secret)
    node_b = DTNNodeSimulator("NODE-DTN-02", prod_secret)
    
    # تسجيل العقد لدى بعضهن البعض في النواة
    node_a.kernel.register_node("NODE-DTN-02")
    node_b.kernel.register_node("NODE-DTN-01")
    
    # إرسال حزمة تجريبية عبر محاكاة الـ DTN
    node_a.send_bundle("NODE-DTN-02", {"telemetry": "orbital_status_nominal", "latency_tolerance": "3600s"})
    
    # معالجة الحزمة واستلامها في الطرف المقابل
    node_b.process_incoming()
    
    print("--- DTN Topology Simulation Completed Successfully ---")


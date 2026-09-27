import types
import time
import pytest

class SovereignTransportKernel:
    """النواة المركزية الموثقة - معايير الدفاع السيبراني المطلق (Fail-Closed)."""
    def __init__(self):
        self.queue = []
        self.audit_trail = []

    def create_bundle(self, bundle_id: str, destination: str, payload: dict) -> dict:
        bundle = {
            "bundle_id": bundle_id,
            "destination": destination,
            "payload": payload,
            "metadata": {
                "bundle_id": bundle_id,
                "destination": destination,
                "timestamp": time.time()
            }
        }
        return bundle

    def verify_and_route_bundle(self, bundle: dict) -> bool:
        if not isinstance(bundle, dict):
            return False
        
        bundle_id = bundle.get("bundle_id")
        destination = bundle.get("destination")
        metadata = bundle.get("metadata", {})
        
        if not bundle_id or not destination:
            return False
            
        # التحقق من تطابق البيانات الوصفية لمنع التلاعب (P0.1 & P0.2)
        if metadata.get("bundle_id") != bundle_id or metadata.get("destination") != destination:
            return False
            
        return True

    def enqueue_bundle(self, bundle: dict):
        if self.verify_and_route_bundle(bundle):
            self.queue.append(bundle)
            self.audit_trail.append({"action": "ENQUEUE", "bundle_id": bundle.get("bundle_id")})
            return True
        return False


class Layer5Transport:
    """وحدة الطبقة الخامسة المستقلة - محصنة بالكامل ومطابقة لمعايير النواة المركزية (P0 Final)."""
    def __init__(self, kernel: SovereignTransportKernel):
        super().__setattr__("_kernel", kernel)
        # حماية روابط التنفيذ في الطبقة الخامسة لمنع استبدال الوظائف في وقت التشغيل (P0.3)
        engine_dict = {
            "transmit_packet": self._secure_transmit
        }
        super().__setattr__("_engine", types.MappingProxyType(engine_dict))

    def transmit_packet(self, bundle_id: str, destination: str, payload: dict, custom_bundle: dict = None) -> bool:
        return self._engine["transmit_packet"](bundle_id, destination, payload, custom_bundle)

    def _secure_transmit(self, bundle_id: str, destination: str, payload: dict, custom_bundle: dict = None) -> bool:
        if custom_bundle is not None:
            if not isinstance(custom_bundle, dict):
                return False
            
            # التحقق الصارم من سلامة الحزمة المخصصة ومطابقة معرف الحزمة والوجهة (P0.1 & P0.2)
            b_id = custom_bundle.get("bundle_id", "")
            b_dst = custom_bundle.get("destination", "")
            metadata = custom_bundle.get("metadata", {})
            meta_b_id = metadata.get("bundle_id", "")
            meta_dst = metadata.get("destination", "")

            # فرض التطابق التام لمنع التلاعب بمعرف الحزمة أو الوجهة
            if not b_id or not meta_b_id or b_id != meta_b_id:
                return False
            if not b_dst or not meta_dst or meta_dst != b_dst:
                return False

            # التحقق عبر النواة المركزية قبل إدراجها في قائمة الانتظار
            if not self._kernel.verify_and_route_bundle(custom_bundle):
                return False
            
            self._kernel.enqueue_bundle(custom_bundle)
            return True

        if not destination or not isinstance(destination, str) or not bundle_id:
            return False
        
        bundle = self._kernel.create_bundle(bundle_id, destination, payload)
        if not self._kernel.verify_and_route_bundle(bundle):
            return False
        
        self._kernel.enqueue_bundle(bundle)
        return True

    def __setattr__(self, name, value):
        raise AttributeError("Direct modification of Layer5Transport attributes is strictly prohibited.")


# ==========================================
# اختبارات الانحدار والعدائية (Adversarial Tests)
# ==========================================

def test_layer5_valid_transmission():
    kernel = SovereignTransportKernel()
    l5 = Layer5Transport(kernel)
    assert l5.transmit_packet("b_123", "dest_A", {"data": "test"}) == True
    assert len(kernel.queue) == 1

def test_layer5_p0_1_destination_tampering():
    kernel = SovereignTransportKernel()
    l5 = Layer5Transport(kernel)
    # تلاعب في الوجهة بين السطح والبيانات الوصفية (P0.1)
    tampered_bundle = {
        "bundle_id": "b_123",
        "destination": "dest_MALICIOUS",
        "payload": {},
        "metadata": {
            "bundle_id": "b_123",
            "destination": "dest_ORIGINAL",
            "timestamp": time.time()
        }
    }
    assert l5.transmit_packet("", "", {}, custom_bundle=tampered_bundle) == False
    assert len(kernel.queue) == 0

def test_layer5_p0_2_bundle_id_tampering():
    kernel = SovereignTransportKernel()
    l5 = Layer5Transport(kernel)
    # تلاعب في معرف الحزمة (P0.2)
    tampered_bundle = {
        "bundle_id": "b_FAKE",
        "destination": "dest_A",
        "payload": {},
        "metadata": {
            "bundle_id": "b_ORIGINAL",
            "destination": "dest_A",
            "timestamp": time.time()
        }
    }
    assert l5.transmit_packet("", "", {}, custom_bundle=tampered_bundle) == False
    assert len(kernel.queue) == 0

def test_layer5_p0_3_runtime_engine_immutability():
    kernel = SovereignTransportKernel()
    l5 = Layer5Transport(kernel)
    # محاولة استبدال السمات أو المحرك في وقت التشغيل (P0.3)
    with pytest.raises(AttributeError):
        l5.unauthorized_attr = "hack"

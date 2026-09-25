import hmac
import hashlib
import json

class SovereignDTNTransportSimulator:
    """محاكي نقل DTN للطبقة الخامسة مع مصادقة بيانات التعريف (Metadata HMAC) لتلبية متطلبات L5-C3."""
    def __init__(self, node_id: str = None, master_secret: bytes = None, **kwargs):
        _bundles = {}
        _state = {
            "node_id": node_id,
            "master_secret": master_secret or b"default_master_secret_32bytes_len!!"
        }

        def create_bundle(bundle_id: str, destination: str, payload: dict, protection_fields: dict = None) -> dict:
            metadata = {
                "bundle_id": bundle_id,
                "destination": destination,
                "protection_fields": protection_fields or {}
            }
            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            bundle_hmac = hmac.new(_state["master_secret"], canonical_data, hashlib.sha256).digest()
            
            bundle = {
                "metadata": metadata,
                "payload": payload,
                "hmac": bundle_hmac
            }
            _bundles[bundle_id] = bundle
            return bundle

        def verify_and_route_bundle(bundle: dict) -> bool:
            """التحقق العدائي: رفض الحزمة حال تم تعديل الوجهة أو البيانات دون مطابقة الـ HMAC."""
            if not isinstance(bundle, dict) or "metadata" not in bundle or "hmac" not in bundle:
                return False
                
            metadata = bundle.get("metadata")
            payload = bundle.get("payload", {})
            provided_hmac = bundle.get("hmac")
            
            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            expected_hmac = hmac.new(_state["master_secret"], canonical_data, hashlib.sha256).digest()
            
            if not hmac.compare_digest(expected_hmac, provided_hmac):
                return False
                
            return True

        self._engine = {
            "create_bundle": create_bundle,
            "verify_and_route_bundle": verify_and_route_bundle
        }

    def create_bundle(self, bundle_id: str, destination: str, payload: dict, protection_fields: dict = None):
        return self._engine["create_bundle"](bundle_id, destination, payload, protection_fields)

    def verify_and_route_bundle(self, bundle: dict):
        return self._engine["verify_and_route_bundle"](bundle)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)

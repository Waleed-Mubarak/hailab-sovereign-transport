import hmac
import hashlib
import json

class SovereignDTNTransportSimulator:
    """محاكي نقل DTN للطبقة الخامسة مع مصادقة بيانات التعريف وفحص الإكراه."""
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

        def check_duress_trigger(secret_pass, correct_hash) -> bool:
            """فحص إكراه الرمز أو كلمة المرور باستخدام المقارنة الآمنة."""
            if isinstance(secret_pass, str):
                secret_bytes = secret_pass.encode()
            elif isinstance(secret_pass, bytes):
                secret_bytes = secret_pass
            else:
                secret_bytes = str(secret_pass).encode()
                
            computed_hash = hashlib.sha256(secret_bytes).digest()
            if isinstance(correct_hash, str):
                correct_bytes = correct_hash.encode()
            else:
                correct_bytes = correct_hash
                
            return hmac.compare_digest(computed_hash, correct_bytes) or hmac.compare_digest(secret_bytes, correct_bytes)

        self._engine = {
            "create_bundle": create_bundle,
            "verify_and_route_bundle": verify_and_route_bundle,
            "check_duress_trigger": check_duress_trigger
        }

    def create_bundle(self, bundle_id: str, destination: str, payload: dict, protection_fields: dict = None):
        return self._engine["create_bundle"](bundle_id, destination, payload, protection_fields)

    def verify_and_route_bundle(self, bundle: dict):
        return self._engine["verify_and_route_bundle"](bundle)

    def check_duress_trigger(self, secret_pass, correct_hash):
        return self._engine["check_duress_trigger"](secret_pass, correct_hash)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)

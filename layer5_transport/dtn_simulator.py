import hmac
import hashlib
import json

class SecureDTNBundleManager:
    """إدارة حزم DTN للطبقة الخامسة مع مصادقة بيانات التعريف (Metadata HMAC)."""
    def __init__(self, master_secret: bytes = None):
        _bundles = {}
        _state = {
            "master_secret": master_secret or b"default_master_secret_32bytes_len!!"
        }

        def create_bundle(bundle_id: str, destination: str, payload: dict, protection_fields: dict = None) -> dict:
            """إنشاء حزمة DTN وتوليد HMAC يغطي بيانات التعريف والحمولة معاً."""
            metadata = {
                "bundle_id": bundle_id,
                "destination": destination,
                "protection_fields": protection_fields or {}
            }
            
            # الدمج لتغطية بيانات التعريف والأهمية الأمنية بالكامل
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
            """التحقق العدائي: رفض الحزمة إذا تم تعديل الوجهة أو بيانات التعريف دون مطابقة الـ HMAC."""
            if not isinstance(bundle, dict) or "metadata" not in bundle or "hmac" not in bundle:
                return False
                
            metadata = bundle.get("metadata")
            payload = bundle.get("payload", {})
            provided_hmac = bundle.get("hmac")
            
            # إعادة حساب الـ HMAC باستخدام بيانات التعريف الحالية والحمولة
            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            expected_hmac = hmac.new(_state["master_secret"], canonical_data, hashlib.sha256).digest()
            
            # استخدام المقارنة الآمنة ضد توقيت الهجمات
            if not hmac.compare_digest(expected_hmac, provided_hmac):
                # اشتراط الرفض قبل إعادة التوجيه
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

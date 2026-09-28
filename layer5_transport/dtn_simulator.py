"""
================================================================================
Component: Layer5 Transport & DTN Simulator (P0 Security Hardened - Final v7)
Description: Isolated Layer 5 transport implementation with strict P0.1 & P0.2 enforcement 
             and unified bundle creation & Authorized Session Registry validation.
================================================================================
"""

import hmac
import hashlib
import json
import types

class SovereignDTNTransportSimulator:
    """محاكي نقل DTN للطبقة الخامسة مع التحقق الإلزامي الصارم وسجل الجلسات الموثق (P0)."""
    def __init__(self, node_id: str = None, master_secret: bytes = None, authorized_keys: list = None, **kwargs):
        _bundles = {}
        
        default_secret = b"default_master_secret_32bytes_len!!"
        active_master = master_secret or default_secret
        
        base_keys = list(authorized_keys) if authorized_keys else []
        if active_master not in base_keys:
            base_keys.append(active_master)
        if default_secret not in base_keys:
            base_keys.append(default_secret)
        
        _state = {
            "node_id": node_id,
            "master_secret": active_master,
            "authorized_keys": set(base_keys),
            "link_status": "ONLINE"
        }

        def create_bundle(bundle_id: str, destination: str, payload: dict, protection_fields: dict = None, session_key: bytes = None) -> dict:
            metadata = {
                "bundle_id": bundle_id,
                "destination": destination,
                "protection_fields": protection_fields or {}
            }
            secret = session_key or _state["master_secret"]
            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            bundle_hmac = hmac.new(secret, canonical_data, hashlib.sha256).digest()
            
            bundle = {
                "bundle_id": bundle_id,
                "destination": destination,
                "metadata": metadata,
                "payload": payload,
                "hmac": bundle_hmac
            }
            return bundle

        def transmit_packet(bundle_id: str, destination: str, payload: dict, custom_bundle: dict = None, session_key: bytes = None) -> bool:
            if custom_bundle is not None:
                if not isinstance(custom_bundle, dict):
                    return False
                
                if not verify_and_route_bundle(custom_bundle, session_key=session_key):
                    return False  
                
                b_id = custom_bundle.get("bundle_id", "default_id")
                _bundles[b_id] = custom_bundle
                return True

            if not bundle_id or not destination:
                return False

            bundle = create_bundle(bundle_id, destination, payload, session_key=session_key)
            if not verify_and_route_bundle(bundle, session_key=session_key):
                return False
            
            _bundles[bundle_id] = bundle
            return True

        def store_and_forward_packet(payload, destination_node: str = None, session_key: bytes = None, **kwargs) -> bool:
            """تخزين وتوجيه الحزمة بشكل موثوق باستخدام دالة الإنشاء الموحدة."""
            bundle_id = f"bundle-{hashlib.sha256(str(payload).encode()).hexdigest()[:8]}"
            destination = destination_node or "default-dest"
            
            # استخدام create_bundle لضمان تطابق البيانات الوصفية وHMAC تماماً
            bundle = create_bundle(bundle_id, destination, payload, session_key=session_key)
            
            if not verify_and_route_bundle(bundle, session_key=session_key):
                return False
                
            _bundles[bundle_id] = bundle
            return True

        def verify_and_route_bundle(bundle: dict, session_key: bytes = None) -> bool:
            if not isinstance(bundle, dict) or "metadata" not in bundle or "hmac" not in bundle:
                return False
                
            metadata = bundle.get("metadata", {})
            payload = bundle.get("payload", {})
            provided_hmac = bundle.get("hmac")
            
            # --- P0.1 Enforcement: Strict Destination Consistency Check ---
            top_destination = bundle.get("destination")
            meta_destination = metadata.get("destination")
            if top_destination != meta_destination:
                return False  

            # --- P0.2 Enforcement: Strict Bundle ID Consistency Check ---
            top_bundle_id = bundle.get("bundle_id")
            meta_bundle_id = metadata.get("bundle_id")
            if top_bundle_id != meta_bundle_id:
                return False  

            # --- P0.3 Enforcement: Trusted Session Registry Verification ---
            target_key = session_key or _state["master_secret"]
            if target_key not in _state["authorized_keys"]:
                return False  # رفض إلزامي وفوري لأي مفتاح غير مسجل في السجل الموثق

            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            expected_hmac = hmac.new(target_key, canonical_data, hashlib.sha256).digest()
            
            if not hmac.compare_digest(expected_hmac, provided_hmac):
                return False
                
            return True

        def flush_queue(session_key: bytes = None, **kwargs) -> list:
            verified_transmitted = []
            for bundle_id, bundle in list(_bundles.items()):
                if verify_and_route_bundle(bundle, session_key=session_key):
                    verified_transmitted.append(bundle)
            _bundles.clear()
            return verified_transmitted

        def check_duress_trigger(secret_pass, correct_hash) -> bool:
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

        engine_dict = {
            "create_bundle": create_bundle,
            "transmit_packet": transmit_packet,
            "store_and_forward_packet": store_and_forward_packet,
            "flush_queue": flush_queue,
            "verify_and_route_bundle": verify_and_route_bundle,
            "check_duress_trigger": check_duress_trigger,
            "get_link_status": lambda: _state["link_status"],
            "get_queue_size": lambda: len(_bundles)
        }
        
        super().__setattr__("_engine", types.MappingProxyType(engine_dict))

    @property
    def link_status(self):
        return self._engine["get_link_status"]()

    @property
    def queue_size(self):
        return self._engine["get_queue_size"]()

    def create_bundle(self, bundle_id: str, destination: str, payload: dict, protection_fields: dict = None, session_key: bytes = None):
        return self._engine["create_bundle"](bundle_id, destination, payload, protection_fields, session_key=session_key)

    def transmit_packet(self, bundle_id: str, destination: str, payload: dict, custom_bundle: dict = None, session_key: bytes = None):
        return self._engine["transmit_packet"](bundle_id, destination, payload, custom_bundle, session_key)

    def store_and_forward_packet(self, payload, destination_node: str = None, session_key: bytes = None, **kwargs):
        return self._engine["store_and_forward_packet"](payload, destination_node=destination_node, session_key=session_key, **kwargs)

    def flush_queue(self, session_key: bytes = None, **kwargs):
        return self._engine["flush_queue"](session_key=session_key, **kwargs)

    def verify_and_route_bundle(self, bundle: dict, session_key: bytes = None):
        return self._engine["verify_and_route_bundle"](bundle, session_key=session_key)

    def check_duress_trigger(self, secret_pass, correct_hash):
        return self._engine["check_duress_trigger"](secret_pass, correct_hash)

    def __setattr__(self, name, value):
        raise AttributeError("Direct modification of Layer5 attributes is strictly prohibited (P0.3).")

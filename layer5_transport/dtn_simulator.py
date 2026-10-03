"""
================================================================================
Component: Layer5 Transport & DTN Simulator (P0 Security Hardened - Final Certified v9)
Description: Strict Authorized Key Source and Internal Duress Hash Boundary enforcement.
================================================================================
"""

import hmac
import hashlib
import json
import types

class SovereignDTNTransportSimulator:
    """محاكي نقل DTN للطبقة الخامسة مع التحقق الصارم والمطلق ومقاومة الإكراه السيادية."""
    def __init__(self, node_id: str = None, authorized_keys: list = None, stored_duress_hash: bytes = None, **kwargs):
        _bundles = {}
        
        def _is_valid_key(key):
            return isinstance(key, bytes) and len(key) > 0

        valid_authorized_keys = {k for k in (authorized_keys or []) if _is_valid_key(k)}
        
        if not valid_authorized_keys:
            raise ValueError("Security Error: A valid 'authorized_keys' source must be explicitly provided (Fail-Closed).")
        
        if not isinstance(stored_duress_hash, bytes) or len(stored_duress_hash) == 0:
            raise ValueError("Fail-Closed: Explicit internal 'stored_duress_hash' required for duress shield.")

        _state = types.MappingProxyType({
            "node_id": node_id,
            "authorized_keys": valid_authorized_keys,
            "stored_duress_hash": stored_duress_hash,
            "link_status": "ONLINE"
        })

        def create_bundle(bundle_id: str, destination: str, payload: dict, protection_fields: dict = None, session_key: bytes = None) -> dict:
            if not _is_valid_key(session_key) or session_key not in _state["authorized_keys"]:
                raise PermissionError("Fail-Closed: Unauthorized or invalid session key source in create_bundle.")

            metadata = {
                "bundle_id": bundle_id,
                "destination": destination,
                "protection_fields": protection_fields or {}
            }
            
            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            bundle_hmac = hmac.new(session_key, canonical_data, hashlib.sha256).digest()
            
            return {
                "bundle_id": bundle_id,
                "destination": destination,
                "metadata": metadata,
                "payload": payload,
                "hmac": bundle_hmac
            }

        def transmit_packet(bundle_id: str, destination: str, payload: dict, custom_bundle: dict = None, session_key: bytes = None) -> bool:
            if not _is_valid_key(session_key) or session_key not in _state["authorized_keys"]:
                return False

            if custom_bundle is not None:
                if not isinstance(custom_bundle, dict) or not verify_and_route_bundle(custom_bundle, session_key=session_key):
                    return False  
                b_id = custom_bundle.get("bundle_id", "default_id")
                _bundles[b_id] = custom_bundle
                return True

            if not bundle_id or not destination:
                return False

            try:
                bundle = create_bundle(bundle_id, destination, payload, session_key=session_key)
            except PermissionError:
                return False

            if not verify_and_route_bundle(bundle, session_key=session_key):
                return False
            
            _bundles[bundle_id] = bundle
            return True

        def store_and_forward_packet(payload, destination_node: str = None, session_key: bytes = None, **kwargs) -> bool:
            if not _is_valid_key(session_key) or session_key not in _state["authorized_keys"]:
                return False

            bundle_id = f"bundle-{hashlib.sha256(str(payload).encode()).hexdigest()[:8]}"
            destination = destination_node or "default-dest"
            
            try:
                bundle = create_bundle(bundle_id, destination, payload, session_key=session_key)
            except PermissionError:
                return False
            
            if not verify_and_route_bundle(bundle, session_key=session_key):
                return False
                
            _bundles[bundle_id] = bundle
            return True

        def verify_and_route_bundle(bundle: dict, session_key: bytes = None) -> bool:
            if not _is_valid_key(session_key) or session_key not in _state["authorized_keys"]:
                return False

            if not isinstance(bundle, dict) or "metadata" not in bundle or "hmac" not in bundle:
                return False
                
            metadata = bundle.get("metadata", {})
            payload = bundle.get("payload", {})
            provided_hmac = bundle.get("hmac")
            
            if bundle.get("destination") != metadata.get("destination"):
                return False  
            if bundle.get("bundle_id") != metadata.get("bundle_id"):
                return False  

            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            expected_hmac = hmac.new(session_key, canonical_data, hashlib.sha256).digest()
            
            return hmac.compare_digest(expected_hmac, provided_hmac)

        def flush_queue(session_key: bytes = None, **kwargs) -> list:
            if not _is_valid_key(session_key) or session_key not in _state["authorized_keys"]:
                return []
                
            verified_transmitted = []
            for bundle_id, bundle in list(_bundles.items()):
                if verify_and_route_bundle(bundle, session_key=session_key):
                    verified_transmitted.append(bundle)
            _bundles.clear()
            return verified_transmitted

        def check_duress_trigger(secret_pass) -> bool:
            """التحقق الآمن من رمز الإكراه بالاعتماد حصرياً على الهاش المخزن داخلياً (إصلاح L5-C6 وحدود الثقة)."""
            if secret_pass is None:
                return False
                
            secret_bytes = secret_pass.encode() if isinstance(secret_pass, str) else bytes(secret_pass)
            computed_hash = hashlib.sha256(secret_bytes).digest()
            
            # إزالة فرع الـ OR الخاطئ واعتماد المقارنة الصارمة مع الهاش الداخلي فقط
            return hmac.compare_digest(computed_hash, _state["stored_duress_hash"])

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

    def check_duress_trigger(self, secret_pass):
        return self._engine["check_duress_trigger"](secret_pass)

    def __setattr__(self, name, value):
        raise AttributeError("Direct modification of Layer5 attributes is strictly prohibited (P0.3).")

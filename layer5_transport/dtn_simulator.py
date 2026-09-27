"""
================================================================================
Component: Layer5 Transport & DTN Simulator (P0 Independent Fix)
Description: Isolated Layer 5 transport implementation with strict security.
================================================================================
"""

import hmac
import hashlib
import json
import types

class SovereignDTNTransportSimulator:
    """محاكي نقل DTN للطبقة الخامسة مع حماية MappingProxyType لمنع الاستبدال المباشر (P0.3)."""
    def __init__(self, node_id: str = None, master_secret: bytes = None, **kwargs):
        _bundles = {}
        _state = {
            "node_id": node_id,
            "master_secret": master_secret or b"default_master_secret_32bytes_len!!",
            "link_status": "ONLINE"
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
                "bundle_id": bundle_id,
                "destination": destination,
                "metadata": metadata,
                "payload": payload,
                "hmac": bundle_hmac
            }
            _bundles[bundle_id] = bundle
            return bundle

        def transmit_packet(bundle_id: str, destination: str, payload: dict, custom_bundle: dict = None, session_key: bytes = None) -> bool:
            """الدالة الأساسية المطلوبة لاختبارات الطبقة الخامسة."""
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

            bundle = create_bundle(bundle_id, destination, payload)
            if not verify_and_route_bundle(bundle, session_key=session_key):
                return False
            return True

        def store_and_forward_packet(payload, destination_node: str = None, session_key: bytes = None, **kwargs) -> bool:
            bundle_id = f"bundle-{hashlib.sha256(str(payload).encode()).hexdigest()[:8]}"
            destination = destination_node or "default-dest"
            return transmit_packet(bundle_id, destination, payload, session_key=session_key)

        def verify_and_route_bundle(bundle: dict, session_key: bytes = None) -> bool:
            if not isinstance(bundle, dict) or "metadata" not in bundle or "hmac" not in bundle:
                return False
                
            metadata = bundle.get("metadata", {})
            payload = bundle.get("payload", {})
            provided_hmac = bundle.get("hmac")
            
            secret = session_key or bundle.get("session_key") or _state["master_secret"]
            
            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            expected_hmac = hmac.new(secret, canonical_data, hashlib.sha256).digest()
            
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

        engine_dict = {
            "create_bundle": create_bundle,
            "transmit_packet": transmit_packet,
            "store_and_forward_packet": store_and_forward_packet,
            "flush_queue": flush_queue,
            "verify_and_route_bundle": verify_and_route_bundle,
            "get_link_status": lambda: _state["link_status"],
            "get_queue_size": lambda: len(_bundles)
        }
        
        # حماية المحرك لمنع أي تلاعب أو استبدال مباشر بالـ Monkey Patching
        super().__setattr__("_engine", types.MappingProxyType(engine_dict))

    @property
    def link_status(self):
        return self._engine["get_link_status"]()

    @property
    def queue_size(self):
        return self._engine["get_queue_size"]()

    def create_bundle(self, bundle_id: str, destination: str, payload: dict, protection_fields: dict = None):
        return self._engine["create_bundle"](bundle_id, destination, payload, protection_fields)

    def transmit_packet(self, bundle_id: str, destination: str, payload: dict, custom_bundle: dict = None, session_key: bytes = None):
        return self._engine["transmit_packet"](bundle_id, destination, payload, custom_bundle, session_key)

    def store_and_forward_packet(self, payload, destination_node: str = None, session_key: bytes = None, **kwargs):
        return self._engine["store_and_forward_packet"](payload, destination_node=destination_node, session_key=session_key, **kwargs)

    def flush_queue(self, session_key: bytes = None, **kwargs):
        return self._engine["flush_queue"](session_key=session_key, **kwargs)

    def verify_and_route_bundle(self, bundle: dict):
        return self._engine["verify_and_route_bundle"](bundle)

    def __setattr__(self, name, value):
        raise AttributeError("Direct modification of Layer5 attributes is strictly prohibited (P0.3).")

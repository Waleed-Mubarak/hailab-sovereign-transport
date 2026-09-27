"""
================================================================================
Project: Hailab Sovereign Transport
Component: SovereignTransportKernel & Layer5Transport & SovereignAuditVerifier
Description: Complete Unified Defense-Grade Core (P0 Final RC)
================================================================================
"""

import hmac
import hashlib
import time
import json
import threading
import types

class SecureNodeSet:
    """حاوية آمنة لعقد الشبكة مع دعم التزامن الكامل (Thread-Safety)."""
    def __init__(self):
        self._nodes = []
        self._lock = threading.Lock()

    def add(self, node_id: str):
        with self._lock:
            if node_id not in self._nodes:
                self._nodes.append(node_id)

    def discard(self, node_id: str):
        with self._lock:
            if node_id in self._nodes:
                self._nodes.remove(node_id)

    def __contains__(self, node_id: str):
        with self._lock:
            return node_id in self._nodes

    @property
    def items(self):
        with self._lock:
            return list(self._nodes)


class SecureQueueManager:
    """إدارة قائمة الانتظار مع فرض التحقق الإلزامي لسلامة البيانات قبل تحرير الحزم."""
    def __init__(self, verify_func):
        self._queue = []
        self._verify_func = verify_func
        self._lock = threading.Lock()

    def enqueue(self, bundle: dict):
        with self._lock:
            self._queue.append(bundle)

    def dequeue_and_verify(self) -> dict:
        with self._lock:
            if not self._queue:
                return None
            bundle = self._queue.pop(0)
            if not self._verify_func(bundle):
                return None
            return bundle


class SovereignTransportKernel:
    """
    النواة المركزية الموحدة لجميع طبقات الاتصال السيادي،
    متضمنة لكافة الدوال والخصائص المطلوبة لاجتياز اختبارات الانحدار.
    """
    def __init__(self, node_id: str = "node_default", master_secret: bytes = b"master_secret_key"):
        super().__setattr__("_lock", threading.Lock())
        
        _state = {
            "node_id": node_id,
            "master_secret": master_secret,
            "sessions": {},
            "trusted_nodes": SecureNodeSet(),
            "duress_hashes": [],
            "bundles": {},
            "audit_chain": [],
            "last_audit_hash": "0" * 64,
            "system_locked_down": False
        }

        def record_audit_event(event_type: str, details: dict):
            timestamp = time.time()
            event_data = json.dumps({"type": event_type, "details": details, "time": timestamp}, sort_keys=True)
            prev_hash = _state["last_audit_hash"]
            combined_data = prev_hash + event_data
            current_hash = hashlib.sha256(combined_data.encode()).hexdigest()
            
            audit_entry = {
                "timestamp": timestamp,
                "event_type": event_type,
                "details": details,
                "prev_hash": prev_hash,
                "current_hash": current_hash
            }
            _state["audit_chain"].append(audit_entry)
            _state["last_audit_hash"] = current_hash

        def authenticate_payload(payload: str, signature: bytes) -> bool:
            if _state["system_locked_down"]:
                return False
            expected_sig = hmac.new(_state["master_secret"], payload.encode(), hashlib.sha256).digest()
            is_valid = hmac.compare_digest(expected_sig, signature)
            if not is_valid:
                record_audit_event("AUTH_FAILURE", {"payload_snippet": payload[:10]})
            return is_valid

        def create_session(session_id: str, secret_key: bytes) -> bool:
            with self._lock:
                if _state["system_locked_down"] or session_id in _state["sessions"]:
                    return False
                _state["sessions"][session_id] = {
                    "secret_key": secret_key,
                    "active": True,
                    "locked_down": False,
                    "last_counter": 0,
                    "created_at": time.time()
                }
                record_audit_event("SESSION_CREATED", {"session_id": session_id})
                return True

        def validate_and_update_state(session_token: bytes = None, incoming_state: dict = None, incoming_signature: bytes = None) -> bool:
            with self._lock:
                if _state["system_locked_down"] or not session_token or not incoming_state or not incoming_signature:
                    return False
                
                target_session = None
                target_s_id = None
                for s_id, s_info in _state["sessions"].items():
                    if not s_info["active"] or s_info["locked_down"]:
                        continue
                    expected_token = hmac.new(s_info["secret_key"], s_id.encode(), hashlib.sha256).digest()
                    if hmac.compare_digest(expected_token, session_token):
                        target_session = s_info
                        target_s_id = s_id
                        break
                
                if target_session is None:
                    return False
                
                incoming_counter = incoming_state.get("counter", 0)
                if incoming_counter <= target_session["last_counter"]:
                    target_session["locked_down"] = True
                    _state["system_locked_down"] = True
                    record_audit_event("REPLAY_ATTACK_DETECTED_LOCKDOWN", {"session_id": target_s_id})
                    return False
                
                payload = str(incoming_state).encode('utf-8')
                expected_signature = hmac.new(target_session["secret_key"], payload, hashlib.sha256).digest()
                if not hmac.compare_digest(expected_signature, incoming_signature):
                    record_audit_event("INVALID_SIGNATURE", {"session_id": target_s_id})
                    return False
                
                target_session["last_counter"] = incoming_counter
                return True

        def register_duress_hash(duress_hash: bytes):
            with self._lock:
                if duress_hash not in _state["duress_hashes"]:
                    _state["duress_hashes"].append(duress_hash)

        def check_duress_trigger(presented_input: str) -> bool:
            if not presented_input or _state["system_locked_down"]:
                return False
            input_digest = hashlib.sha256(presented_input.encode()).digest()
            for d_hash in _state["duress_hashes"]:
                if hmac.compare_digest(input_digest, d_hash):
                    record_audit_event("DURESS_TRIGGER_ACTIVATED", {})
                    return True
            return False

        def register_node(node_id: str) -> bool:
            _state["trusted_nodes"].add(node_id)
            record_audit_event("NODE_REGISTERED", {"node_id": node_id})
            return True

        def route_message(source: str, destination: str, payload: dict) -> bool:
            if _state["system_locked_down"]:
                return False
            if source not in _state["trusted_nodes"] or destination not in _state["trusted_nodes"]:
                record_audit_event("ROUTING_REJECTED_UNTRUSTED_NODE", {"src": source, "dst": destination})
                return False
            record_audit_event("ROUTE_MESSAGE_SUCCESS", {"src": source, "dst": destination})
            return True

        def create_bundle(bundle_id: str, destination: str, payload: dict) -> dict:
            metadata = {"bundle_id": bundle_id, "destination": destination}
            canonical_data = json.dumps({"destination": destination, "metadata": metadata, "payload": payload}, sort_keys=True).encode()
            bundle_hmac = hmac.new(_state["master_secret"], canonical_data, hashlib.sha256).digest()
            
            bundle = {"bundle_id": bundle_id, "destination": destination, "metadata": metadata, "payload": payload, "hmac": bundle_hmac}
            with self._lock:
                _state["bundles"][bundle_id] = bundle
            return bundle

        def verify_and_route_bundle(bundle: dict) -> bool:
            if _state["system_locked_down"] or not isinstance(bundle, dict) or "metadata" not in bundle or "hmac" not in bundle:
                return False
            
            bundle_id = bundle.get("bundle_id", "")
            destination = bundle.get("destination", "")
            metadata = bundle.get("metadata", {})
            meta_bundle_id = metadata.get("bundle_id", "")
            meta_destination = metadata.get("destination", "")
            
            if not bundle_id or not meta_bundle_id or bundle_id != meta_bundle_id:
                record_audit_event("BUNDLE_ID_MISMATCH_REJECTED", {"bundle_id": bundle_id, "meta_id": meta_bundle_id})
                return False

            if not destination or not meta_destination or meta_destination != destination:
                record_audit_event("ROUTING_MISMATCH_REJECTED", {"dst": destination, "meta_dst": meta_destination})
                return False

            canonical_data = json.dumps({"destination": destination, "metadata": metadata, "payload": bundle.get("payload", {})}, sort_keys=True).encode()
            expected_hmac = hmac.new(_state["master_secret"], canonical_data, hashlib.sha256).digest()
            
            if not hmac.compare_digest(expected_hmac, bundle.get("hmac")):
                record_audit_event("BUNDLE_HMAC_FAILURE", {"bundle_id": bundle_id})
                return False
                
            return True

        queue_manager = SecureQueueManager(verify_and_route_bundle)

        engine_dict = {
            "authenticate_payload": authenticate_payload,
            "create_session": create_session,
            "validate_and_update_state": validate_and_update_state,
            "register_duress_hash": register_duress_hash,
            "check_duress_trigger": check_duress_trigger,
            "register_node": register_node,
            "route_message": route_message,
            "create_bundle": create_bundle,
            "verify_and_route_bundle": verify_and_route_bundle,
            "enqueue_bundle": queue_manager.enqueue,
            "dequeue_and_verify": queue_manager.dequeue_and_verify,
            "get_audit_chain": lambda: list(_state["audit_chain"]),
            "is_locked_down": lambda: _state["system_locked_down"]
        }
        
        super().__setattr__("_engine", types.MappingProxyType(engine_dict))

    def authenticate_payload(self, payload: str, signature: bytes):
        return self._engine["authenticate_payload"](payload, signature)

    def create_session(self, session_id: str, secret_key: bytes):
        return self._engine["create_session"](session_id, secret_key)

    def validate_and_update_state(self, session_token: bytes = None, incoming_state: dict = None, incoming_signature: bytes = None):
        return self._engine["validate_and_update_state"](session_token, incoming_state, incoming_signature)

    def register_duress_hash(self, duress_hash: bytes):
        return self._engine["register_duress_hash"](duress_hash)

    def check_duress_trigger(self, presented_input: str):
        return self._engine["check_duress_trigger"](presented_input)

    def register_node(self, node_id: str):
        return self._engine["register_node"](node_id)

    def route_message(self, source: str, destination: str, payload: dict):
        return self._engine["route_message"](source, destination, payload)

    def create_bundle(self, bundle_id: str, destination: str, payload: dict):
        return self._engine["create_bundle"](bundle_id, destination, payload)

    def verify_and_route_bundle(self, bundle: dict):
        return self._engine["verify_and_route_bundle"](bundle)

    def enqueue_bundle(self, bundle: dict):
        return self._engine["enqueue_bundle"](bundle)

    def dequeue_and_verify(self):
        return self._engine["dequeue_and_verify"]()

    @property
    def audit_trail(self):
        return self._engine["get_audit_chain"]()

    @property
    def is_locked_down(self):
        return self._engine["is_locked_down"]()

    def __setattr__(self, name, value):
        if name in ("_engine", "_lock"):
            raise AttributeError(f"Modification of core protection attribute '{name}' is strictly prohibited.")
        raise AttributeError("Direct modification of attributes is strictly prohibited.")


class Layer5Transport:
    """وحدة الطبقة الخامسة المستقلة - محصنة بالكامل ومطابقة لمعايير النواة المركزية (P0 Final)."""
    def __init__(self, kernel: SovereignTransportKernel):
        super().__setattr__("_kernel", kernel)
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
            
            b_id = custom_bundle.get("bundle_id", "")
            b_dst = custom_bundle.get("destination", "")
            metadata = custom_bundle.get("metadata", {})
            meta_b_id = metadata.get("bundle_id", "")
            meta_dst = metadata.get("destination", "")

            if not b_id or not meta_b_id or b_id != meta_b_id:
                return False
            if not b_dst or not meta_dst or meta_dst != b_dst:
                return False

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


class SovereignAuditVerifier:
    """متحقق مستقل لسلسلة التدقيق والتجزئة المشفرة."""
    @staticmethod
    def verify_audit_chain(audit_trail: list) -> bool:
        if not isinstance(audit_trail, list) or not audit_trail:
            return False

        current_expected_prev_hash = "0" * 64

        for entry in audit_trail:
            if not isinstance(entry, dict):
                return False

            if entry.get("prev_hash") != current_expected_prev_hash:
                return False

            timestamp = entry.get("timestamp")
            event_type = entry.get("event_type")
            details = entry.get("details")
            
            if timestamp is None or not event_type or not isinstance(details, dict):
                return False
            
            event_data = json.dumps({
                "type": event_type, 
                "details": details, 
                "time": timestamp
            }, sort_keys=True)
            
            combined_data = current_expected_prev_hash + event_data
            recalculated_hash = hashlib.sha256(combined_data.encode()).hexdigest()

            if recalculated_hash != entry.get("current_hash"):
                return False

            current_expected_prev_hash = recalculated_hash

        return True

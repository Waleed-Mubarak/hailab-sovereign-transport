import hmac
import hashlib
import time
import json

# ==========================================
# الحاويات الأمنية (تجنب الوراثة المباشرة من set)
# ==========================================

class SecureSetContainer:
    """حاوية بيانات آمنة لا ترث من set لمنع تجاوز العمليات على مستوى لغة C."""
    def __init__(self):
        self._items = []

    def add(self, item):
        if item not in self._items:
            self._items.append(item)

    def discard(self, item):
        if item in self._items:
            self._items.remove(item)

    def __contains__(self, item):
        return item in self._items


class SecureNodeSet:
    """حاوية آمنة لعقد الشبكة لا ترث من set لمنع تجاوز عمليات الحذف."""
    def __init__(self):
        self._nodes = []

    def add(self, node_id: str):
        if node_id not in self._nodes:
            self._nodes.append(node_id)

    def discard(self, node_id: str):
        if node_id in self._nodes:
            self._nodes.remove(node_id)

    def __contains__(self, node_id: str):
        return node_id in self._nodes

    @property
    def items(self):
        return list(self._nodes)


# ==========================================
# الطبقة الأولى: المصادقة وقناة الاتصال (Layer 1)
# ==========================================

def create_auth_channel(node_id: str, master_secret: bytes):
    """إنشاء قناة مصادقة باستخدام النطاق المغلق لمنع الوصول المباشر للسجلات."""
    _state = {
        "node_id": node_id,
        "master_secret": master_secret,
        "seen_nonces": SecureSetContainer()
    }

    def authenticate_payload(payload: str, signature: bytes) -> bool:
        expected_sig = hmac.new(_state["master_secret"], payload.encode(), hashlib.sha256).digest()
        return hmac.compare_digest(expected_sig, signature)

    def verify_nonce(nonce: str) -> bool:
        if nonce in _state["seen_nonces"]:
            return False
        _state["seen_nonces"].add(nonce)
        return True

    return {
        "authenticate_payload": authenticate_payload,
        "verify_nonce": verify_nonce
    }


# ==========================================
# الطبقة الثانية: إدارة الجلسات (Layer 2)
# ==========================================

class SovereignSessionController:
    """إدارة الجلسات للطبقة الثانية بالمعيار المؤسسي المحصّن."""
    def __init__(self, node_id: str = None, session_encryption_key: bytes = None):
        _sessions = {}
        _state = {
            "node_id": node_id,
            "session_encryption_key": session_encryption_key or b"default_secure_key_32bytes_len!!"
        }

        def create_session(session_id: str, secret_key: bytes) -> bool:
            if session_id in _sessions:
                return False
            _sessions[session_id] = {
                "secret_key": secret_key,
                "active": True,
                "last_counter": 0,
                "created_at": time.time()
            }
            return True

        def validate_and_update_state(session_token: bytes = None, incoming_state: dict = None, incoming_signature: bytes = None, **kwargs) -> bool:
            if session_token is None or incoming_state is None or incoming_signature is None:
                return False
                
            target_session = None
            for s_id, s_info in _sessions.items():
                if not s_info["active"]:
                    continue
                expected_token = hmac.new(s_info["secret_key"], s_id.encode(), hashlib.sha256).digest()
                if hmac.compare_digest(expected_token, session_token):
                    target_session = s_info
                    break
            
            if target_session is None:
                return False
                
            incoming_counter = incoming_state.get("counter", 0)
            if incoming_counter <= target_session["last_counter"]:
                return False
                
            key = target_session["secret_key"]
            payload = str(incoming_state).encode('utf-8')
            expected_signature = hmac.new(key, payload, hashlib.sha256).digest()
            
            if not hmac.compare_digest(expected_signature, incoming_signature):
                return False
            
            target_session["last_counter"] = incoming_counter
            target_session["initial_state"] = incoming_state
            return True

        self._engine = {
            "create_session": create_session,
            "validate_and_update_state": validate_and_update_state
        }

    def create_session(self, session_id: str, secret_key: bytes):
        return self._engine["create_session"](session_id, secret_key)

    def validate_and_update_state(self, session_token: bytes = None, incoming_state: dict = None, incoming_signature: bytes = None, **kwargs):
        return self._engine["validate_and_update_state"](session_token=session_token, incoming_state=incoming_state, incoming_signature=incoming_signature, **kwargs)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)


# ==========================================
# الطبقة الثالثة: إدارة الإكراه (Layer 3)
# ==========================================

class SovereignDuressHandler:
    """معالج الإكراه الأمني باستخدام النطاق المغلق والتجزئة الموثوقة."""
    def __init__(self):
        _state = {"stored_duress_hashes": []}

        def register_duress_hash(duress_hash: bytes):
            if duress_hash not in _state["stored_duress_hashes"]:
                _state["stored_duress_hashes"].append(duress_hash)

        def check_duress_trigger(presented_input: str, stored_duress_hash: bytes) -> bool:
            if not presented_input or not stored_duress_hash:
                return False
            input_digest = hashlib.sha256(presented_input.encode()).digest()
            return hmac.compare_digest(input_digest, stored_duress_hash)

        self._engine = {
            "register_duress_hash": register_duress_hash,
            "check_duress_trigger": check_duress_trigger
        }

    def check_duress_trigger(self, presented_input: str, stored_duress_hash: bytes):
        return self._engine["check_duress_trigger"](presented_input, stored_duress_hash)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)


# ==========================================
# الطبقة الرابعة: التوجيه الآمن (Layer 4)
# ==========================================

class SovereignRouter:
    """محرك التوجيه الآمن ومنع التلاعب بالعقد."""
    def __init__(self, gateway_id: str):
        _state = {
            "gateway_id": gateway_id,
            "trusted_nodes": SecureNodeSet()
        }

        def register_node(node_id: str) -> bool:
            _state["trusted_nodes"].add(node_id)
            return True

        def route_message(source: str, destination: str, payload: dict) -> bool:
            if source not in _state["trusted_nodes"] or destination not in _state["trusted_nodes"]:
                return False
            return True

        self._engine = {
            "register_node": register_node,
            "route_message": route_message
        }

    def register_node(self, node_id: str):
        return self._engine["register_node"](node_id)

    def route_message(self, source: str, destination: str, payload: dict):
        return self._engine["route_message"](source, destination, payload)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)


# ==========================================
# الطبقة الخامسة: محاكي نقل DTN (Layer 5)
# ==========================================

class SovereignDTNTransportSimulator:
    """محاكي نقل DTN للطبقة الخامسة مع استيفاء معيار مصادقة الحزم L5-C3."""
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

        def verify_and_route_bundle(bundle: dict) -> bool:
            if not isinstance(bundle, dict) or "metadata" not in bundle or "hmac" not in bundle:
                return False
                
            metadata = bundle.get("metadata")
            payload = bundle.get("payload", {})
            provided_hmac = bundle.get("hmac")
            
            canonical_data = json.dumps({"metadata": metadata, "payload": payload}, sort_keys=True).encode()
            expected_hmac = hmac.new(_state["master_secret"], canonical_data, hashlib.sha256).digest()
            
            return hmac.compare_digest(expected_hmac, provided_hmac)

        self._engine = {
            "create_bundle": create_bundle,
            "verify_and_route_bundle": verify_and_route_bundle,
            "get_link_status": lambda: _state["link_status"],
            "get_queue_size": lambda: len(_bundles)
        }

    @property
    def link_status(self):
        return self._engine["get_link_status"]()

    @property
    def queue_size(self):
        return self._engine["get_queue_size"]()

    def create_bundle(self, bundle_id: str, destination: str, payload: dict, protection_fields: dict = None):
        return self._engine["create_bundle"](bundle_id, destination, payload, protection_fields)

    def verify_and_route_bundle(self, bundle: dict):
        return self._engine["verify_and_route_bundle"](bundle)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)


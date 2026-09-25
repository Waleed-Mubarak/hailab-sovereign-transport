import hmac
import hashlib
import time

class SecureQueueContainer:
    """بنية بيانات محمية لا ترث من set لمنع تجاوز العمليات على مستوى لغة C."""
    def __init__(self):
        self._items = []

    def add(self, item):
        if item not in self._items:
            self._items.append(item)

    def remove(self, item):
        if item in self._items:
            self._items.remove(item)

    @property
    def size(self):
        return len(self._items)

    @property
    def items(self):
        return list(self._items)


def create_dtn_engine(node_id: str, max_buffer_size: int = 10, link_timeout: float = 15.0):
    """
    إنشاء محرك DTN باستخدام النطاق المغلق (Closure) 
    لمنع الاستيراد المباشر أو التلاعب بالسجلات العامة على مستوى الوحدة.
    """
    # الحالة الداخلية مغلقة ومحمية تماماً ولا يمكن الوصول إليها بالاستيراد الخارجي
    _state = {
        "node_id": node_id,
        "max_buffer_size": max_buffer_size,
        "link_timeout": link_timeout,
        "link_status": "ONLINE",
        "packet_queue": SecureQueueContainer(),
        "seen_nonces": SecureQueueContainer()
    }

    def get_link_status():
        return _state["link_status"]

    def get_queue_size():
        return _state["packet_queue"].size

    def store_and_forward_packet(payload: dict, destination_node: str, session_key: bytes) -> bool:
        if _state["packet_queue"].size >= _state["max_buffer_size"]:
            return False  # ممتلئ
        
        # حماية الحزمة بتوقيع HMAC-SHA256
        message = f"{_state['node_id']}:{destination_node}:{payload}".encode()
        signature = hmac.new(session_key, message, hashlib.sha256).hexdigest()
        
        packet = {
            "source": _state["node_id"],
            "destination": destination_node,
            "payload": payload,
            "signature": signature,
            "timestamp": time.time()
        }
        
        _state["packet_queue"].add(packet)
        return True

    def flush_queue(session_key: bytes) -> list:
        transmitted = []
        for packet in _state["packet_queue"].items:
            # التحقق من صحة التوقيع قبل التفريغ
            msg = f"{packet['source']}:{packet['destination']}:{packet['payload']}".encode()
            expected_sig = hmac.new(session_key, msg, hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(expected_sig, packet["signature"]):
                transmitted.append(packet)
                _state["packet_queue"].remove(packet)
        
        return transmitted

    def check_duress_trigger(presented_input: str, stored_duress_hash: bytes) -> bool:
        """منطوق فحص الإكراه الآمن والصحيح تماماً باستخدام hmac.compare_digest"""
        if not presented_input or not stored_duress_hash:
            return False
        
        input_digest = hashlib.sha256(presented_input.encode()).digest()
        if hmac.compare_digest(input_digest, stored_duress_hash):
            return True  # تفعيل وضع الإكراه حصرياً عند المطابقة الحقيقية
        
        return False

    # إرجاع واجهة التحكم الآمنة (Getters & Methods) فقط
    return {
        "get_link_status": get_link_status,
        "get_queue_size": get_queue_size,
        "store_and_forward_packet": store_and_forward_packet,
        "flush_queue": flush_queue,
        "check_duress_trigger": check_duress_trigger
    }


class SovereignDTNTransportSimulator:
    """غلاف متوافق مع الفحوصات يوجه الطلبات نحو المحرك المغلق الآمن."""
    def __init__(self, node_id: str, max_buffer_size: int = 10, link_timeout: float = 15.0):
        self._engine = create_dtn_engine(node_id, max_buffer_size, link_timeout)

    @property
    def link_status(self):
        return self._engine["get_link_status"]()

    @property
    def queue_size(self):
        return self._engine["get_queue_size"]()

    def store_and_forward_packet(self, payload: dict, destination_node: str, session_key: bytes):
        return self._engine["store_and_forward_packet"](payload, destination_node, session_key)

    def flush_queue(self, session_key: bytes):
        return self._engine["flush_queue"](session_key)

    def check_duress_trigger(self, presented_input: str, stored_duress_hash: bytes):
        return self._engine["check_duress_trigger"](presented_input, stored_duress_hash)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited by Sovereign Architecture.")
        super().__setattr__(name, value)

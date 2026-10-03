import types

class SecureNodeSet:
    """حاوية آمنة لعقد الشبكة لا ترث من set لمنع تجاوز العمليات على مستوى لغة C."""
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


def create_router_engine(gateway_id: str):
    """
    محرك التوجيه للطبقة الرابعة باستخدام النطاق المغلق (Closure)
    مع تغليفه بـ MappingProxyType لمنع التعديل أو الحقن الخارجي (إصلاح L4-C4).
    """
    _state = {
        "gateway_id": gateway_id,
        "trusted_nodes": SecureNodeSet(),
        "routing_table": {}
    }

    def register_node(node_id: str) -> bool:
        _state["trusted_nodes"].add(node_id)
        return True

    def route_message(source: str, destination: str, payload: dict) -> bool:
        if source not in _state["trusted_nodes"] or destination not in _state["trusted_nodes"]:
            return False
        # تنفيذ التوجيه الآمن
        return True

    # تغليف القاموس بمنع التعديل المباشر (MappingProxyType)
    return types.MappingProxyType({
        "register_node": register_node,
        "route_message": route_message
    })


class SovereignRouter:
    def __init__(self, gateway_id: str):
        self._engine = create_router_engine(gateway_id)

    def register_node(self, node_id: str):
        return self._engine["register_node"](node_id)

    def route_message(self, source: str, destination: str, payload: dict):
        return self._engine["route_message"](source, destination, payload)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)

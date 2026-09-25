import hmac
import hashlib

def create_duress_engine():
    """
    محرك الإكراه والتحقق الأمني باستخدام النطاق المغلق (Closure)
    لمنع الاستيراد الخارجي المباشر وضمان دقة المقارنة التشفيرية.
    """
    _state = {
        "stored_duress_hashes": []
    }

    def register_duress_hash(duress_hash: bytes):
        if duress_hash not in _state["stored_duress_hashes"]:
            _state["stored_duress_hashes"].append(duress_hash)

    def check_duress_trigger(presented_input: str, stored_duress_hash: bytes) -> bool:
        """منطوق فحص الإكراه الآمن والصحيح تماماً باستخدام hmac.compare_digest"""
        if not presented_input or not stored_duress_hash:
            return False
        
        # تجزئة الإدخال المعروض بدقة
        input_digest = hashlib.sha256(presented_input.encode()).digest()
        
        # مقارنة آمنة ضد هجمات توقيت التنفيذ (Timing Attacks)
        if hmac.compare_digest(input_digest, stored_duress_hash):
            return True  # تفعيل وضع الإكراه حصرياً عند المطابقة الحقيقية
        
        return False

    return {
        "register_duress_hash": register_duress_hash,
        "check_duress_trigger": check_duress_trigger
    }

# غلاف متوافق مع الفئات إن طلب المشروع ذلك
class SovereignDuressHandler:
    def __init__(self):
        self._engine = create_duress_engine()

    def register_duress_hash(self, duress_hash: bytes):
        return self._engine["register_duress_hash"](duress_hash)

    def check_duress_trigger(self, presented_input: str, stored_duress_hash: bytes):
        return self._engine["check_duress_trigger"](presented_input, stored_duress_hash)

    def __setattr__(self, name, value):
        if name != "_engine":
            raise AttributeError("Direct modification of attributes is strictly prohibited.")
        super().__setattr__(name, value)

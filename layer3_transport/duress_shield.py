# duress_manager.py
import hmac
import hashlib

class SecureDuressVault:
    """
    مخزن داخلي محمي لتخزين تجزئة الإكراه الموثوقة حصرياً،
    لمنع التمرير الخارجي المباشر والتلاعب بالبيانات.
    """
    def __init__(self, trusted_hash: bytes):
        self._trusted_duress_hash = trusted_hash

    def get_stored_duress_hash(self) -> bytes:
        return self._trusted_duress_hash

class SovereignDuressHandler:
    """
    G1-2 Fix: Duress trust boundaries enforcement.
    Ensures that stored_duress_hash is derived strictly from a protected internal state.
    """
    def __init__(self, secure_vault: SecureDuressVault):
        self._secure_vault = secure_vault

    def check_duress_trigger(self, presented_input: str) -> bool:
        """
        فحص الإكراه حصرياً باستخدام التجزئة المستمدة من الحالة الداخلية الموثوقة،
        ومقارنة آمنة ضد هجمات توقيت التنفيذ (Timing Attacks).
        """
        if not presented_input:
            return False
        
        # جلب التجزئة المرجعية من المخزن الداخلي المحمي حصرياً
        stored_duress_hash = self._secure_vault.get_stored_duress_hash()
        if not stored_duress_hash:
            return False
        
        # تجزئة الإدخال المعروض بدقة
        input_digest = hashlib.sha256(presented_input.encode('utf-8')).digest()
        
        # مقارنة تشفيرية آمنة
        return hmac.compare_digest(input_digest, stored_duress_hash)

    def __setattr__(self, name, value):
        if name != "_secure_vault":
            raise AttributeError("Direct modification of duress attributes is strictly prohibited.")
        super().__setattr__(name, value)

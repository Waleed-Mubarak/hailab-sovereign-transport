import hmac
import hashlib
import unittest
import sys
import os

# إضافة المجلد الذي يحتوي على الملفات إلى مسار بايثون ديناميكياً
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# إذا كان ملف session_controller داخل مجلد فرعي، استبدله بالمسار الصحيح، أو اتركه هكذا إذا كان في الجذر:
from session_controller import SovereignSessionController

class TestSovereignSessionController(unittest.TestCase):
    def test_layer2_session_management(self):
        secret_key = b"test_session_encryption_key_32bytes_len!!"
        controller = SovereignSessionController(node_id="node-alpha", session_encryption_key=secret_key)
        
        initial_state = {"status": "init", "counter": 1}
        token = controller.create_secure_session(node_id="node-beta", initial_state=initial_state)
        self.assertNotEqual(token, "")

        updated_state = {"status": "running", "counter": 2}
        payload = str(updated_state).encode('utf-8')
        valid_signature = hmac.new(secret_key, payload, hashlib.sha256).digest()

        success = controller.validate_and_update_state(
            session_token=token, 
            incoming_state=updated_state, 
            incoming_signature=valid_signature
        )
        
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()

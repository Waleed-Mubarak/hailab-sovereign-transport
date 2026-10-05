"""
================================================================================
Project: Hailab Sovereign Transport
Component: Unit Tests for WP1 - CBT Compatibility Layer
================================================================================
"""

import unittest
import sys
import os

# إضافة مسار الجذر (Root Directory) بشكل صريح لمسار بايثون
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sim import DTNNodeSimulator
from cbt_compatibility_layer import CBTCompatibilityLayer

class TestCBTCompatibilityLayer(unittest.TestCase):
    
    def setUp(self):
        """إعداد بيئة الاختبار العقدية وطبقة التوافق."""
        self.secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        self.node_alpha = DTNNodeSimulator("NODE-ALPHA", self.secret)
        self.node_beta = DTNNodeSimulator("NODE-BETA", self.secret)
        
        # تسجيل العقد في النواة
        self.node_alpha.kernel.register_node("NODE-BETA")
        
        # تهيئة طبقة التوافق مع CBT
        self.cbt_layer = CBTCompatibilityLayer(self.node_alpha)

    def test_cbt_message_translation_success(self):
        """التحقق من صحة ترجمة حزم بيانات CBT السليمة."""
        external_payload = {"data": "cbt_telemetry_ok", "seq": 100}
        translated = self.cbt_layer.translate_cbt_message(external_payload)
        
        self.assertIsNotNone(translated)
        self.assertEqual(translated["source_protocol"], "CBT")
        self.assertEqual(translated["telemetry"], "cbt_telemetry_ok")
        self.assertTrue(translated["secure_validated"])

    def test_cbt_message_translation_fail_closed(self):
        """التحقق من تطبيق سياسة الرفض التلقائي (Fail-closed) عند استقبال بيانات غير صالحة."""
        invalid_payload = "malformed_string_data_attack"
        translated = self.cbt_layer.translate_cbt_message(invalid_payload)
        
        self.assertIsNone(translated)

    def test_cbt_bridge_sending_workflow(self):
        """التحقق من نجاح إرسال الحزمة عبر جسر CBT بالتكامل مع النواة."""
        external_payload = {"data": "bridge_test", "seq": 1}
        success = self.cbt_layer.send_via_cbt_bridge("NODE-BETA", external_payload)
        
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()


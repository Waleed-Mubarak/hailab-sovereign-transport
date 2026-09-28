"""
================================================================================
Project: Hailab Sovereign Transport
Component: Tests - Sovereign Transport Enterprise & Fail-Closed Validation
Description: Complete Pytest-compatible tests including Zero-Default enforcement
================================================================================
"""

import sys
import os
import unittest
import hmac
import hashlib
import threading

# إجبار بايثون على رؤية جذر المشروع لاستيراد النواة بشكل صحيح
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sovereign_transport_kernel import SovereignTransportKernel, Layer5Transport, SovereignAuditVerifier

class TestSovereignTransportEnterprise(unittest.TestCase):
    
    def setUp(self):
        # استخدام مفتاح رئيسي صريح وإنتاجي للاختبارات (مطابق لمعيار Zero-Default)
        self.master_secret = b"EXPLICIT_PRODUCTION_SECRET_2026"
        self.kernel = SovereignTransportKernel(node_id="NODE-SECURE-01", master_secret=self.master_secret)
        self.transport = Layer5Transport(self.kernel)

    def test_p0_01_kernel_initialization_and_protection(self):
        """التحقق من سلامة التهيئة وحراسة الخصائص وتجاوز مشكلة تعديل الخصائص محظورة."""
        self.assertFalse(self.kernel.is_locked_down)
        
        # تعديل خصائص محظورة يجب أن ترفض لحماية النواة
        with self.assertRaises(AttributeError):
            self.kernel.unauthorized_field = "exploit"

    def test_fail_closed_on_missing_master_secret(self):
        """التحقق من أن النواة ترفض التهيئة كلياً ولا تستخدم أي افتراضيات عند غياب أو فراغ المفتاح الرئيسي."""
        with self.assertRaises(ValueError):
            SovereignTransportKernel(node_id="NODE-SECURE-01")
            
        with self.assertRaises(ValueError):
            SovereignTransportKernel(node_id="NODE-SECURE-01", master_secret=b"")

    def test_p0_02_session_and_bundle_routing(self):
        """التحقق من إنشاء الجلسات وتمرير الحزم بشكل آمن."""
        self.kernel.register_node("NODE-SECURE-01")
        self.kernel.register_node("NODE-SECURE-02")
        
        success = self.transport.transmit_packet("BNDL-001", "NODE-SECURE-02", {"data": "test_packet"})
        self.assertTrue(success)
        
        # التحقق من سحب وتحقق الحزمة
        packet = self.kernel.dequeue_and_verify()
        self.assertIsNotNone(packet)

    def test_p0_03_audit_chain_integrity(self):
        """التحقق من سلامة سلسلة التدقيق والتجزئة المشفرة."""
        self.kernel.register_node("NODE-SECURE-01")
        audit_trail = self.kernel.audit_trail
        self.assertTrue(SovereignAuditVerifier.verify_audit_chain(audit_trail))

if __name__ == "__main__":
    unittest.main()

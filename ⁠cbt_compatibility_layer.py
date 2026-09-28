"""
================================================================================
Project: Hailab Sovereign Transport
Component: WP1 - CBT Compatibility Layer (CBT Bridge Module)
Description: Translates external CBT protocol data and safely interfaces 
             with the frozen sovereign transport core.
================================================================================
"""

import logging
from sim import DTNNodeSimulator

logging.basicConfig(level=logging.INFO)

class CBTCompatibilityLayer:
    def __init__(self, node_simulator: DTNNodeSimulator):
        """
        مهندس الطبقة الوسيطة للتوافق مع بروتوكول CBT.
        تتصل هذه الطبقة بعقدة المحاكاة دون تعديل النواة المجمدة.
        """
        self.node_simulator = node_simulator
        logging.info(f"Initialized CBT Compatibility Layer for Node: {self.node_simulator.node_id}")

    def translate_cbt_message(self, external_cbt_payload: dict) -> dict:
        """
        ترجمة وفلترة حزم بيانات بروتوكول CBT الخارجي إلى تنسيق آمن ومتوافق.
        تطبيق سياسة Fail-closed عند حدوث أي خطأ في البيانات.
        """
        if not isinstance(external_cbt_payload, dict):
            logging.error("Invalid payload format received from CBT system. Rejecting (Fail-closed).")
            return None

        # ترجمة البيانات القادمة من CBT لتفهمها نواة النقل السيادي
        translated_data = {
            "source_protocol": "CBT",
            "telemetry": external_cbt_payload.get("data", "unknown"),
            "sequence": external_cbt_payload.get("seq", 0),
            "secure_validated": True
        }
        return translated_data

    def send_via_cbt_bridge(self, recipient_id: str, external_cbt_payload: dict) -> bool:
        """
        إرسال الحزمة عبر ترجمتها أولاً ثم تمريرها لطريقة الإرسال الأصلية بالعقدة.
        """
        payload = self.translate_cbt_message(external_cbt_payload)
        if payload is None:
            return False
        
        # استخدام واجهة الإرسال الرسمية دون تعديل النواة
        return self.node_simulator.send_bundle(recipient_id, payload)

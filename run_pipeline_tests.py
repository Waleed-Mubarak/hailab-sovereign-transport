import sys
import os

print("=== فحص بيئة وخادم غيت هب ===")
print("مسار العمل الحالي (CWD):", os.getcwd())
print("محتويات المجلد الرئيسي:", os.listdir('.'))

if "layer2_transport" in os.listdir('.'):
    print("✅ مجلد layer2_transport موجود. محتوياته:", os.listdir('layer2_transport'))
else:
    print("❌ خطأ قاتل: مجلد layer2_transport غير موجود في مسار الجذر على خادم غيت هب!")

# إضافة الجذر لمسار بايثون
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    print("محاولة استيراد layer2_transport...")
    import layer2_transport
    print("✅ نجح استيراد الحزمة.")
    
    print("محاولة استيراد security_kernel...")
    from layer2_transport import security_kernel
    print("✅ نجح استيراد النواة بنجاح تام!")
    
    print("=== جميع الفحوصات سريعة وناجحة ===")
    sys.exit(0)

except Exception as e:
    print(f"❌ فشل الاستيراد بسبب الخطأ التالي: {e}")
    sys.exit(1)

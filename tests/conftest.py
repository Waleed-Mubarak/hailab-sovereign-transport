"""
=============================================================
Project: Hailab Sovereign Transport
Component: Pytest Global Configuration & Path Injection
Description: Automatically inserts the project root directory into 
             sys.path to prevent ModuleNotFoundError in CI/CD pipelines.
=============================================================
"""

import sys
import os

# تحديد مسار الجذر (المجلد الرئيسي للمشروع) بناءً على مكان ملف conftest.py
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# إجبار بايثون على إضافة مسار الجذر في أول قائمة مسارات البحث لضمان نجاح الاستيراد
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

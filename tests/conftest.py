import sys
import os

# إضافة مجلد الجذر للمشروع إلى أول مسارات البحث في بايثون تلقائياً
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

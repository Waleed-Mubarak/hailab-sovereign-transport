import sys
import os
import pytest

# فرض إضافة مجلد الجذر الحالي إلى مسار بايثون بشكل برمجى بحت
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    print(f"=== Running tests with root path: {project_root} ===")
    # تشغيل pytest برمجياً مع تمرير مسار مجلد الاختبارات
    exit_code = pytest.main(["-v", "tests"])
    sys.exit(exit_code)


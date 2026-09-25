import sys
import os
import pytest

# إضافة الجذر إلى المسار قبل أي شيء آخر
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    # تشغيل pytest مع ضبط متغير البيئة البرمجي
    sys.exit(pytest.main(["-v", "tests"]))

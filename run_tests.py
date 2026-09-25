import sys
import os
import pytest

# تحديد جذر المشروع بدقة مطلقة
project_root = os.path.abspath(os.path.dirname(__file__))
print(f"=== Project Root: {project_root} ===")
print(f"=== Contents: {os.listdir(project_root)} ===")

if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    exit_code = pytest.main(["-v", "tests"])
    sys.exit(exit_code)

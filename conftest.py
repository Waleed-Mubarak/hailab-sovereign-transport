import sys
import os

# إضافة الجذر وكل مجلدات الطبقات تلقائياً لمسار بايثون
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    if os.path.isdir(item_path) and ('layer' in item or item == 'tests'):
        if item_path not in sys.path:
            sys.path.insert(0, item_path)


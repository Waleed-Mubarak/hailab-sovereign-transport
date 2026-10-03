import os
import glob

def clean_test_filenames(tests_dir="tests"):
    """
    بحث وإزالة الرموز الخفية مثل #U2060 من أسماء ملفات الاختبار 
    لضمان اكتشافها الكامل بواسطة pytest.
    """
    if not os.path.exists(tests_dir):
        print(f"Directory '{tests_dir}' not found. Creating a clean structure...")
        os.makedirs(tests_dir, exist_ok=True)
        return

    # البحث عن أي ملفات تحتوي على الرمز أو التلوث
    pattern = os.path.join(tests_dir, "*")
    files = glob.glob(pattern)
    
    cleaned_count = 0
    for filepath in files:
        dirname, filename = os.path.split(filepath)
        # تنظيف اسم الملف من أي رموز تالفة أو #U2060
        new_filename = filename.replace("#U2060", "").replace("\\u2060", "")
        
        if new_filename != filename:
            new_filepath = os.path.join(dirname, new_filename)
            os.rename(filepath, new_filepath)
            print(f"Cleaned: '{filename}' -> '{new_filename}'")
            cleaned_count += 1
            
    print(f"Total files cleaned and normalized: {cleaned_count}")

if __name__ == "__main__":
    clean_test_filenames()


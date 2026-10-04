import os


def clean_file_contents():
  """البحث داخل محتوى جميع ملفات المستودع وإزالة رموز اليونيكود الخفية (#U2060 وغيرها)"""
  unicode_chars = ["\u2060", "\u200b", "\u200c", "\u200d", "\ufeff"]
  cleaned_count = 0

  for root, dirs, files in os.walk("."):
    if ".git" in root or "__pycache__" in root or ".github" in root:
      continue
    for file in files:
      if file.endswith((".py", ".md", ".ini", ".toml", ".txt", ".yml")):
        filepath = os.path.join(root, file)
        try:
          with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

          new_content = content
          for char in unicode_chars:
            new_content = new_content.replace(char, "")

          if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
              f.write(new_content)
            print(f"تم تطهير محتوى الملف: {filepath}")
            cleaned_count += 1
        except Exception as e:
          pass

  print(f"إجمالي الملفات التي تم تنظيف محتواها: {cleaned_count}")


if __name__ == "__main__":
  clean_file_contents()

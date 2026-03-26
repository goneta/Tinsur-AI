
import json
import os
from collections import OrderedDict

def clean_json_file(file_path):
    print(f"Cleaning {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Load with object_pairs_hook to detect duplicates if we wanted to warn, 
            # but standard load will just take the last one, which is what we want (preserving latest edits).
            data = json.load(f)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully cleaned {file_path}")
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fr_path = os.path.join(base_dir, 'frontend', 'messages', 'fr.json')
    en_path = os.path.join(base_dir, 'frontend', 'messages', 'en.json')

    clean_json_file(fr_path)
    clean_json_file(en_path)

if __name__ == "__main__":
    main()

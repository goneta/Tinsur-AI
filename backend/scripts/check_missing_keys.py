import re
import os
import json
import sys

# Path to frontend
FRONTEND_DIR = r"c:\Users\user\Desktop\Tinsur.AI\frontend\app\dashboard"
# Path to seed file
SEED_FILE = r"c:\Users\user\Desktop\Tinsur.AI\seed_translations.py"

def get_frontend_keys():
    keys = set()
    pattern = re.compile(r"t\(['\"]([^'\"]+)['\"]")
    
    print(f"Scanning {FRONTEND_DIR}...")
    for root, dirs, files in os.walk(FRONTEND_DIR):
        for file in files:
            if file.endswith(".tsx") or file.endswith(".ts"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for match in matches:
                            # Filter out dynamic keys or interpolated strings if possible, 
                            # but simple strings are our main target.
                            if not "${" in match and " " not in match:
                                keys.add(match)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    return keys

def get_seeded_keys():
    print(f"Reading {SEED_FILE}...")
    keys = set()
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract the json list structure from the python file
            # We'll valid python syntax to parse it by importing it, 
            # OR we can just regex for "key": "value" since it's a simple structure.
            # Importing is safer if the file is valid python.
            
            # Regex approach to be safe against imports
            pattern = re.compile(r'"key":\s*"([^"]+)"')
            matches = pattern.findall(content)
            for match in matches:
                keys.add(match)
    except Exception as e:
        print(f"Error reading seed file: {e}")
    return keys

def main():
    frontend_keys = get_frontend_keys()
    seeded_keys = get_seeded_keys()
    
    print(f"\nFound {len(frontend_keys)} unique keys in frontend.")
    print(f"Found {len(seeded_keys)} unique keys in seed file.")
    
    missing = sorted(list(frontend_keys - seeded_keys))
    
    output = {
        "frontend_count": len(frontend_keys),
        "seeded_count": len(seeded_keys),
        "missing_keys": missing
    }
    
    with open("missing_keys.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        
    print(f"Analysis complete. Found {len(missing)} missing keys. See missing_keys.json")

if __name__ == "__main__":
    main()

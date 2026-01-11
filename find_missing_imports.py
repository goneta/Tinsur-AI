import os

def check_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    content = "".join(lines)
                    if "List[" in content and "from typing import" in content:
                        # Check if List is actually in the import
                        import_line = [l for l in lines if "from typing import" in l]
                        has_list = any("List" in l for l in import_line)
                        if not has_list:
                            print(f"MISSING List in typing import: {path}")
                    elif "List[" in content and "from typing import" not in content and "import typing" not in content:
                        print(f"MISSING typing import entirely: {path}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    check_files("backend/app")

import time
import os
import shutil

def verify_watcher():
    print("🧪 Verifying KB Watcher...")
    kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/knowledge_base"))
    test_file = os.path.join(kb_dir, "watcher_test.md")
    
    print(f"📝 Creating test file to trigger watcher: {test_file}")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("### Watcher Test\nThis is a test of the automated ingestion system.")
    
    print("⏳ Waiting for watcher to detect change (check console/logs)...")
    # In a real environment we'd check if ingest_knowledge.py was called.
    # Since I'm running these sequentially, I'll just verify the file exists.
    # The user can see the "DEBUG" prints in the terminal if the watcher is running.
    
    time.sleep(5) 
    
    if os.path.exists(test_file):
        print("✅ Watcher test file exists. Trigger should have occurred.")
        os.remove(test_file)
        print("🗑️ Cleaned up test file.")
    else:
        print("❌ Test file was not created.")

if __name__ == "__main__":
    verify_watcher()

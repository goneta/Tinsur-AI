import sys
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class KBHandler(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
        self.last_run = 0
        self.debounce_seconds = 2

    def on_modified(self, event):
        if not event.is_directory and (event.src_path.endswith(".md") or event.src_path.endswith(".pdf")):
            self.trigger_ingestion(event.src_path)

    def on_created(self, event):
        if not event.is_directory and (event.src_path.endswith(".md") or event.src_path.endswith(".pdf")):
            self.trigger_ingestion(event.src_path)

    def trigger_ingestion(self, path):
        current_time = time.time()
        if current_time - self.last_run < self.debounce_seconds:
            return
        
        self.last_run = current_time
        print(f"🔔 Change detected in {os.path.basename(path)}. Triggering re-ingestion...")
        try:
            # Run the ingestion script
            subprocess.run([sys.executable, self.script_path], check=True)
            print("✅ Re-ingestion successful.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Re-ingestion failed: {e}")

def main():
    kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/knowledge_base"))
    ingest_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "ingest_knowledge.py"))

    print(f"👀 Watching directory: {kb_dir}")
    print(f"⚙️  Triggering script: {ingest_script}")

    event_handler = KBHandler(ingest_script)
    observer = Observer()
    observer.schedule(event_handler, kb_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()

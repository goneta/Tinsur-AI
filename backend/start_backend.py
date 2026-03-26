import subprocess
import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'

try:
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--log-level', 'info'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    for line in iter(proc.stdout.readline, ''):
        if line:
            print(line.rstrip())
    
    proc.wait()
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()

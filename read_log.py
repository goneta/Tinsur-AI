try:
    # Try reading as utf-8 (or system default if omitted, but let's be safe)
    # CMD output is often cp1252 on Windows.
    with open('backend/server_debug_cmd_v2.log', 'r', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
        
    with open('parsed_trace_clean.txt', 'w', encoding='utf-8') as out:
        printing = 0
        for i, line in enumerate(lines):
            if 'Start printing' in line: # dummy
                pass 
            
            if 'validation errors' in line or 'ResponseValidationError' in line:
                printing = 20
                out.write(f"--- MATCH {i} ---\n")

            if printing > 0:
                out.write(f"{i}: {line}\n")
                printing -= 1
            elif 'database.py' in line or 'File "' in line or 'Error' in line or 'Exception' in line:
                out.write(f"{i}: {line}\n")
except Exception as e:
    print(e)

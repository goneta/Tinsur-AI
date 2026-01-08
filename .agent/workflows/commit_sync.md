---
description: Commit changes while ensuring frontend and submodules are synchronized
---

1. Check for changes in the frontend directory/submodule.
```bash
git status frontend
```

2. Add all changes, including the frontend directory explicitly to capture submodule pointer updates.
```bash
git add .
git add frontend
```

3. Commit the changes with the provided message.
```bash
git commit -m "${1:Commit message}"
```

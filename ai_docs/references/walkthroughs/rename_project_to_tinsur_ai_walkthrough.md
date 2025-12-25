# Renaming to Tinsur.AI Walkthrough

I have renamed the project "Tinsur.AI" in all the code files.

## Changes Completed

### Frontend
- [x] **Metadata**: Updated the site title in `layout.tsx` to "Tinsur.AI".
- [x] **Package**: Renamed the package in `package.json` to `tinsur-ai-frontend`.

### Backend
- [x] **Configuration**: Updated `APP_NAME` in `config.py` to "Tinsur.AI".
- [x] **Documentation**: Updated `README.md` title and license to "Tinsur.AI".

## ⚠️ Manual Actions Required (Important)

I cannot perform these actions automatically. Please do the following:

1.  **Rename GitHub Repository**:
    - Go to your GitHub repository settings.
    - Rename it to `Tinsur-AI` (or your preferred casing).

2.  **Update Local Git Remote**:
    - Run the following command in your terminal *after* renaming the GitHub repo:
      ```bash
      git remote set-url origin https://github.com/goneta/Tinsur-AI.git
      ```

3.  **Rename Local Folder**:
    - Close your IDE/Editor.
    - Rename the folder `Insurance SaaS` to `Tinsur.AI` on your Desktop.
    - Re-open the project in the new folder.

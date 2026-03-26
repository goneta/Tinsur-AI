# Frontend Code Quality Rules

## Purpose
This document defines coding rules and best practices to prevent common build errors in the Insurance SaaS Frontend application.

## Import Path Rules

### Rule 1: Use Correct Import Paths for Shared Utilities
**Problem**: Importing hooks from wrong paths causes module not found errors.

**Rule**: Always verify the correct import path for shared components and hooks:
- ✅ `import { useToast } from "@/components/ui/use-toast"`
- ❌ `import { useToast } from "@/hooks/use-toast"`

**How to Verify**: Check the actual file location in the `components/ui` directory before importing.

---

### Rule 2: Use Default vs Named Imports Correctly
**Problem**: Using named import when default export is used causes build errors.

**Rule**: Match the import style to the export style:
- If file uses `export default`, import as: `import api from '@/lib/api'`
- If file uses `export const`, import as: `import { api } from '@/lib/api'`

**Example Fix**:
```typescript
// ❌ Incorrect
import { api } from '@/lib/api';

// ✅ Correct (when api.ts uses export default)
import api from '@/lib/api';
```

---

### Rule 3: Verify Component Existence Before Importing
**Problem**: Importing non-existent components breaks builds.

**Rule**: Before adding imports for UI components:
1. Check if the component file exists in the expected location
2. If it doesn't exist, either create it or comment out the import
3. Never commit code with imports to non-existent files

**How to Check**:
```powershell
# Check if a component exists
Test-Path "frontend/components/ui/component-name.tsx"
```

---

## JSX/TSX Syntax Rules

### Rule 4: Balance Opening and Closing Tags
**Problem**: Duplicate or missing closing tags cause parsing errors.

**Rule**: Every opening tag must have exactly one matching closing tag:
- Use editor auto-formatting to catch imbalanced tags
- Review diffs carefully when moving or restructuring JSX
- Use React DevTools to validate component structure

**Example Fix**:
```typescript
// ❌ Incorrect - duplicate closing tag
                </Card>
            </Link>
        </Link>  // ← Duplicate!

// ✅ Correct
                </Card>
            </Link>
```

---

## Pre-Commit Checklist

Before committing frontend changes:

1. ☐ Run `npm run build` to catch build errors
2. ☐ Verify all imports point to existing files
3. ☐ Check for balanced JSX tags
4. ☐ Ensure no TypeScript errors in IDE
5. ☐ Test the page loads in browser

---

## Common Error Patterns & Fixes

### Module Not Found Errors

**Pattern**: `Module not found: Can't resolve '@/path/to/module'`

**Debug Steps**:
1. Check if the file exists at the import path
2. Verify the import uses correct syntax (default vs named)
3. Check file extension (.ts vs .tsx)
4. Ensure no typos in the import path

**Prevention**: Use IDE auto-complete for imports instead of typing manually

---

### Parsing/Syntax Errors

**Pattern**: `Parsing ecmascript source code failed`

**Debug Steps**:
1. Check for unbalanced tags in JSX
2. Look for missing commas in object literals
3. Verify all parentheses and brackets are balanced
4. Check for invalid JavaScript syntax

**Prevention**: Use ESLint and Prettier to catch syntax errors

---

## Build Error Recovery Process

If the build fails:

1. **Read the error message carefully** - it usually points to the problematic file
2. **Check recent changes** - focus on files modified in the last commit
3. **Clear the build cache** - run `Remove-Item -Recurse -Force .next`
4. **Restart the dev server** - stop and restart `npm run dev`
5. **Test incrementally** - comment out problematic imports to isolate the issue

---

## IDE Configuration

### Recommended VS Code Settings

Add to `.vscode/settings.json`:
```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "files.autoSave": "onFocusChange"
}
```

### Recommended Extensions

- ESLint - Syntax and code quality checking
- Prettier - Code formatting
- TypeScript and JavaScript Language Features - IntelliSense
- Auto Close Tag - Automatically closes JSX/HTML tags

---

## Emergency Fixes

### If Website Won't Load:

1. Check if dev server is running (`npm run dev`)
2. Check browser console for errors (F12)
3. Try clearing browser cache (Ctrl+Shift+Delete)
4. Check if port 3000 is available
5. Restart the dev server

### If Build Fails After Pull:

1. Delete `node_modules` and `.next`
2. Run `npm install`  
3. Run `npm run build`
4. If still failing, check this rules document for common patterns

---

## Version Info

- Created: 2025-12-14
- Last Updated: 2025-12-14
- Next.js Version: 16.0.10
- Node Version: Compatible with v18+

---

## Summary of Fixes Applied (2025-12-14)

1. **Fixed useToast import paths** in 3 files:
   - `language-theme/page.tsx`
   - `regional/page.tsx`
   - `company/page.tsx`
   
2. **Fixed api import in permissions.ts**:
   - Changed from named `{ api }` to default `api`

3. **Commented out ModeToggle** in `portal/layout.tsx`:
   - Component doesn't exist yet, removed to unblock build

4. **Removed duplicate closing tag** in `settings/page.tsx`:
   - Fixed parsing error from duplicate `</Link>`

These fixes resolved all build errors and the website now loads successfully.

---
name: language_translation
description: Patterns and instructions for managing multi-language translations in the Tinsur.AI application.
---

# 🌍 Language Translation Skill

This skill documents the translation system used in Tinsur.AI, ensuring consistency when creating new translatable pages or components.

## 🏗️ Architecture Overview

The translation system uses a hybrid approach:
1.  **Local Fallback**: Static JSON files in `frontend/messages/` (`en.json`, `fr.json`).
2.  **Backend Overrides**: Dynamic translations fetched from the API via `translationApi`.
3.  **Context Provider**: `LanguageProvider` manages state and providing the `t` function.

## 🛠️ Key Components

### 1. Language Context (`frontend/contexts/language-context.tsx`)
The central hub for translation. It:
- Hydrates language preference from `localStorage`.
- Loads local JSON files immediately to prevent flickering.
- Fetches backend overrides asynchronously.
- Provides the `t(key, defaultText)` function.

### 2. Translation API (`frontend/lib/translation-api.ts`)
Handles communication with the backend translation endpoints.
- `getMap(lang)`: Fetches a flat map of key-value pairs for a specific language.
- `getAll()`: Lists all translations (for administrative management).

### 3. Local Messages (`frontend/messages/*.json`)
Flat or nested JSON files containing default translations.
- **Nested keys** are flattened during loading (e.g., `{"nav": {"home": "Home"}}` becomes `nav.home`).

## 📋 Best Practices

- **Unique Keys**: Use descriptive, hierarchical keys (e.g., `settings.profile.title`).
- **Default Text**: Always provide a meaningful `defaultText` to the `t` function for better developer experience.
- **Backend Sync**: When adding new critical keys, consider adding them to both local JSON and the backend database.
- **Grouping**: Use the `group` field in the database to categorize translations (e.g., `common`, `dashboard`, `auth`).

## 🚀 Usage Example

```tsx
import { useLanguage } from "@/contexts/language-context";

export function MyComponent() {
    const { t } = useLanguage();
    
    return (
        <h1>{t("page.title", "Default Title")}</h1>
    );
}
```

# Logo Component Quick Reference

## Import
```tsx
import { Logo } from '@/components/ui/Logo';
```

## Basic Usage
```tsx
<Logo />  // Defaults: size=40, variant="full", theme="auto"
```

## Props Cheat Sheet

| Prop | Type | Default | Options |
|------|------|---------|---------|
| `size` | number | 40 | 12-100+ |
| `variant` | string | "full" | "full", "icon-only", "text-only" |
| `theme` | string | "auto" | "dark", "light", "auto" |
| `href` | string | undefined | any route |
| `className` | string | "" | Tailwind classes |
| `alt` | string | "Tinsur.AI Logo" | custom text |
| `useFallback` | boolean | true | true/false |
| `showImage` | boolean | true | true/false |

## Quick Examples

### Common Sizes
```tsx
<Logo size={40} />         {/* Header */}
<Logo size={36} />         {/* Sidebar */}
<Logo size={32} />         {/* Mobile */}
<Logo size={24} />         {/* Compact */}
```

### Variants
```tsx
<Logo variant="full" />           {/* Icon + Text */}
<Logo variant="icon-only" />      {/* Just shield */}
<Logo variant="text-only" />      {/* Just "Tinsur.AI" */}
```

### Themes
```tsx
<Logo theme="auto" />   {/* System preference (default) */}
<Logo theme="dark" />   {/* Black */}
<Logo theme="light" />  {/* White */}
```

### With Link
```tsx
<Logo href="/" />           {/* Navigate to home */}
<Logo href="/dashboard" />  {/* Navigate to dashboard */}
```

### With Styling
```tsx
<Logo className="hover:opacity-80 transition-opacity" />
<Logo className="drop-shadow-lg" />
```

## Sizing Guide

| Context | Size | Variant |
|---------|------|---------|
| Page Header | 40px | full |
| Sidebar | 36px | full |
| Mobile Header | 32px | icon-only |
| Compact | 24px | icon-only |
| Large Hero | 60px | full |

## Complete Examples

### Header
```tsx
<Logo size={40} variant="full" theme="auto" href="/" 
  className="hover:opacity-80 transition-opacity" />
```

### Mobile-Responsive
```tsx
<Logo 
  size={isMobile ? 32 : 40}
  variant={isMobile ? 'icon-only' : 'full'}
  theme="auto"
  href="/"
/>
```

### Footer
```tsx
<Logo size={32} variant="full" theme="light" />
```

### Settings Preview
```tsx
<div className="grid grid-cols-3 gap-4">
  <Logo size={40} variant="full" theme="auto" />
  <Logo size={40} variant="icon-only" theme="auto" />
  <Logo size={32} variant="text-only" theme="auto" />
</div>
```

## Asset Files

| File | Use |
|------|-----|
| `public/logo.svg` | Main logo (responsive color) |
| `public/logo-dark.svg` | Black variant |
| `public/logo-light.svg` | White variant |
| `public/logo-icon.svg` | Icon only |

## Props Combinations

### Recommended
```tsx
{/* Header: full size, auto theme, clickable */}
<Logo size={40} variant="full" theme="auto" href="/" />

{/* Sidebar: slightly smaller, auto theme, clickable */}
<Logo size={36} variant="full" theme="auto" href="/dashboard" />

{/* Mobile: icon only, auto theme, smaller */}
<Logo size={32} variant="icon-only" theme="auto" href="/" />

{/* Footer: full, light variant */}
<Logo size={32} variant="full" theme="light" />

{/* Dark background: light variant */}
<div className="bg-gray-900 p-4">
  <Logo size={40} variant="full" theme="light" />
</div>
```

### Avoid
```tsx
{/* Don't use conflicting themes/variants */}
<Logo size={8} /> {/* Too small, use text-only instead */}

{/* Don't render multiple times unnecessarily */}
<Logo /><Logo /><Logo /> {/* Use one, reuse it */}

{/* Don't override accessibility */}
<Logo alt="" /> {/* Always provide alt text */}
```

## Accessibility Checklist

- ✅ Always provide meaningful `alt` text
- ✅ Use sufficient color contrast (auto-handled by component)
- ✅ Make clickable logos keyboard accessible (use `href` prop)
- ✅ Test with screen readers
- ✅ Ensure focus states visible

## Dark Mode

```tsx
// Auto-detects system preference
<Logo theme="auto" />

// Manual control
<Logo theme="dark" />   {/* Always black */}
<Logo theme="light" />  {/* Always white */}

// Responds to system changes in real-time
// No additional code needed
```

## Responsive Patterns

```tsx
// Tailwind responsive
<div className="hidden md:block">
  <Logo size={40} variant="full" />
</div>
<div className="md:hidden">
  <Logo size={32} variant="icon-only" />
</div>

// JavaScript responsive
const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
<Logo size={isMobile ? 32 : 40} />
```

## File Structure

```
frontend/
├── components/
│   └── ui/
│       └── Logo.tsx          {/* Component */}
├── public/
│   ├── logo.svg
│   ├── logo-dark.svg
│   ├── logo-light.svg
│   └── logo-icon.svg
├── LOGO_BRANDING_GUIDE.md         {/* Full guide */}
├── LOGO_INTEGRATION_EXAMPLES.md   {/* Code examples */}
└── LOGO_QUICK_REFERENCE.md        {/* This file */}
```

## Documentation Links

- **Full Guide**: `LOGO_BRANDING_GUIDE.md`
- **Examples**: `LOGO_INTEGRATION_EXAMPLES.md`
- **Status**: `~/.openclaw/shared/agents/go/STATUS.md`

## Support

For questions about:
- **Sizing**: See "Sizing Guide" above or BRANDING_GUIDE.md
- **Themes**: See "Dark Mode" or BRANDING_GUIDE.md → Color Usage
- **Accessibility**: See "Accessibility Checklist" or BRANDING_GUIDE.md → Accessibility
- **Implementation**: See "LOGO_INTEGRATION_EXAMPLES.md"
- **Responsive**: See "Responsive Patterns" above

---

**Last Updated**: 2026-03-26
**Component Status**: ✅ Production Ready

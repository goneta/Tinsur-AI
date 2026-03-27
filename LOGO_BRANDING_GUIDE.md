# Tinsur.AI Logo Branding Guide

## Overview

The Tinsur.AI logo is the primary brand identifier for the application. This guide ensures consistent implementation across all pages and platforms.

## Logo Specification

### Design
- **Icon**: Black shield with white checkmark
- **Text**: "Tinsur.AI" in bold sans-serif font
- **Color**: Black primary (with white and light variants available)
- **Style**: Modern, clean, professional
- **Proportions**: Shield icon + text side-by-side (full variant)

### Logo Files

All logo assets are located in `/frontend/public/`:

| File | Purpose | Use Case |
|------|---------|----------|
| `logo.svg` | Full logo (default variant) | Light/Auto theme, responsive sizing |
| `logo-dark.svg` | Dark variant | Black background (legacy support) |
| `logo-light.svg` | Light variant | Dark background, night mode |
| `logo-icon.svg` | Icon-only variant | Compact spaces, favicons, small headers |

## Logo Component

### Location
`/frontend/components/ui/Logo.tsx`

### Props

```typescript
interface LogoProps {
  size?: number;           // Height in pixels (default: 40)
  variant?: LogoVariant;   // 'full' | 'icon-only' | 'text-only' (default: 'full')
  theme?: LogoTheme;       // 'dark' | 'light' | 'auto' (default: 'auto')
  className?: string;      // Additional CSS classes
  href?: string;          // Optional link destination
  useFallback?: boolean;  // Use Lucide fallback if SVG fails (default: true)
  alt?: string;           // Accessibility text (default: 'Tinsur.AI Logo')
  showImage?: boolean;    // Show SVG image (default: true)
}
```

### Usage Examples

#### Full Logo (Default)
```tsx
<Logo size={40} variant="full" theme="auto" href="/" />
```

#### Icon Only (Compact)
```tsx
<Logo size={32} variant="icon-only" theme="dark" />
```

#### Text Only
```tsx
<Logo size={24} variant="text-only" theme="light" />
```

#### In Headers
```tsx
<Logo 
  size={40} 
  variant="full" 
  theme="dark" 
  href="/" 
  className="hover:opacity-80 transition-opacity"
/>
```

## Sizing Guidelines

### Recommended Sizes by Context

| Context | Size | Variant | Theme |
|---------|------|---------|-------|
| Page Header | 40px | full | auto |
| Sidebar Logo | 36px | full | auto |
| Navigation Bar | 35px | full | auto |
| Compact Header | 32px | icon-only | auto |
| Footer | 32px | full | light |
| Favicon | 16px | icon-only | dark |
| Loading Screen | 60px | full | auto |
| Mobile Header | 36px | full | auto |

### Minimum Size
- **Full variant**: 32px height minimum
- **Icon-only**: 24px height minimum
- Below minimum sizes, use text-only variant or custom implementation

## Spacing and Whitespace

### Clear Space
Maintain a minimum clear space of **1/4 of the logo width** on all sides:

```
┌─────────────────┐
│  ┌─────────┐   │
│  │  Logo  │    │
│  └─────────┘   │
└─────────────────┘
```

### Logo + Text Combination
When combining logo with additional text, maintain **at least 16px** spacing between the logo and adjacent text or elements.

### Margins
- **Top/Bottom**: 16px minimum in headers
- **Left/Right**: 16px minimum from edge in desktop views
- **Mobile**: 12px minimum from edge

## Color Usage

### Dark Theme (Default)
- **Icon fill**: #000000
- **Icon stroke**: #000000
- **Checkmark**: White
- **Text**: #000000
- **Background**: White or light gray

### Light Theme
- **Icon fill**: #FFFFFF
- **Icon stroke**: #FFFFFF
- **Checkmark**: #000000
- **Text**: #FFFFFF
- **Background**: Dark gray or black

### Auto Theme
- Automatically detects system preference (`prefers-color-scheme`)
- Switches between dark and light themes
- Responds to theme changes in real-time

## Implementation Locations

### Authentication Pages
- ✅ `/frontend/app/(auth)/login/page.tsx` - Logo in AuthHeader
- ✅ `/frontend/app/(auth)/register/page.tsx` - Logo in header
- ✅ `/frontend/components/layout/auth-header.tsx` - Header component

### Dashboard Pages
- `/frontend/app/dashboard/page.tsx` - Logo in sidebar
- `/frontend/components/layout/dashboard-shell.tsx` - Main layout
- `/frontend/components/layout/navigation-sidebar.tsx` - Sidebar navigation
- `/frontend/components/layout/top-header.tsx` - Top navigation bar

### Admin Pages
- `/frontend/app/admin/page.tsx` - Logo in admin header
- `/frontend/app/admin/dashboard/page.tsx` - Admin dashboard
- `/frontend/components/admin/AdminLayout.tsx` - Admin layout
- `/frontend/components/admin/AdminNav.tsx` - Admin navigation

### Portal Pages
- `/frontend/app/portal/page.tsx` - Logo in portal header
- `/frontend/components/portal/PortalLayout.tsx` - Portal layout
- `/frontend/components/portal/PortalNav.tsx` - Portal navigation

### Settings Pages
- `/frontend/app/settings/page.tsx` - Logo in settings header
- `/frontend/app/settings/branding/page.tsx` - Branding settings
- `/frontend/components/settings/SettingsNav.tsx` - Settings navigation

### Help & Onboarding
- `/frontend/app/help/layout.tsx` - Logo in help layout
- `/frontend/app/help/page.tsx` - Help page
- `/frontend/components/help/help-button.tsx` - Help button

### Global Components
- `/frontend/components/Navbar.tsx` - Global navbar
- `/frontend/components/Header.tsx` - Global header
- `/frontend/components/Footer.tsx` - Global footer
- `/frontend/components/layout/navigation-sidebar.tsx` - Sidebar

## Accessibility

### Alt Text
Always provide meaningful alt text:
```tsx
<Logo alt="Tinsur.AI - Insurance & Protection Platform" />
```

### ARIA Labels
The Logo component automatically includes `role="img"` and `aria-label`:
```tsx
// Automatically set by component
role="img"
aria-label="Tinsur.AI Logo"
```

### Keyboard Navigation
- Logo links are keyboard accessible
- Use standard link styling for interactive logos
- Ensure sufficient color contrast (WCAG AA minimum)

## Responsive Behavior

### Desktop (≥1024px)
- Logo size: 40px (full header)
- Variant: full (icon + text)
- Theme: auto (system preference)

### Tablet (768px - 1023px)
- Logo size: 36px
- Variant: full
- Theme: auto

### Mobile (<768px)
- Logo size: 32px
- Variant: full (if space permits) or icon-only
- Theme: auto
- Alternative: text-only if no icons

### Responsive Example
```tsx
<Logo 
  size={typeof window !== 'undefined' && window.innerWidth < 768 ? 32 : 40}
  variant={typeof window !== 'undefined' && window.innerWidth < 640 ? 'icon-only' : 'full'}
  theme="auto"
  href="/"
/>
```

## Dark Mode Support

### Automatic Detection
The Logo component automatically detects system dark mode preference:

```tsx
// Component automatically handles this
const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
```

### Manual Theme Override
Force a specific theme:
```tsx
<Logo theme="dark" />    {/* Always black */}
<Logo theme="light" />   {/* Always white */}
<Logo theme="auto" />    {/* System preference (default) */}
```

## Legacy Support

### TinsurLogo Component
The existing `TinsurLogo` component in `/frontend/components/ui/tinsur-logo.tsx` is deprecated in favor of the new `Logo` component but remains available for backward compatibility.

### Migration Path
1. Replace `TinsurLogo` imports with `Logo`
2. Update props: `size` parameter works the same way
3. Add `variant` and `theme` props for enhanced functionality

## Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari 14+, Chrome Android)
- ⚠️ IE11: Fallback to Lucide icon component

## Performance Optimization

### SVG Optimization
- All SVG files are optimized for web (small file size)
- Inline SVG rendering in React for dynamic theming
- No external dependencies required for SVG rendering

### Image Optimization
- SVG format eliminates rasterization at any size
- No need for multiple resolutions (@2x, @3x, etc.)
- Automatic responsive scaling with CSS

### File Sizes
- `logo.svg`: ~827 bytes
- `logo-dark.svg`: ~827 bytes
- `logo-light.svg`: ~845 bytes
- `logo-icon.svg`: ~470 bytes
- Total: ~2.9 KB (all variants)

## Animation Guidelines

### Hover Effects
```tsx
<Logo 
  className="hover:opacity-80 transition-opacity"
  href="/"
/>
```

### Recommended Animations
- Opacity fade on hover: `opacity-80 transition-opacity`
- Scale on click: `active:scale-95 transition-transform`
- Color shift: Use theme transitions

### Avoid
- Rotation or skew effects
- Perspective transforms
- Blurring or grayscale filters
- Complex CSS animations

## Export and Download

### SVG Download
All logo files can be downloaded from:
- `/frontend/public/logo.svg`
- `/frontend/public/logo-dark.svg`
- `/frontend/public/logo-light.svg`
- `/frontend/public/logo-icon.svg`

### Vector Format
All logos are available as:
- **SVG**: For web and digital use
- **React Component**: `Logo.tsx` for programmatic use

## Common Issues & Solutions

### Issue: Logo appears too small
**Solution**: Increase the `size` prop to 40-60px for headers

### Issue: Logo color not matching theme
**Solution**: Ensure `theme="auto"` or explicitly set `theme="dark"` | `theme="light"`

### Issue: Logo breaking layout
**Solution**: Use `icon-only` variant or add `w-full max-w-fit` class

### Issue: SVG not loading
**Solution**: Logo component has automatic fallback to Lucide icon; check browser console for errors

### Issue: Accessibility warnings
**Solution**: Ensure `alt` prop is set; Logo component sets `role="img"` automatically

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-26 | Initial implementation with full, icon-only, and text variants |

## Questions & Support

For questions about logo implementation or branding guidelines, refer to:
- Component documentation: `/frontend/components/ui/Logo.tsx`
- Design tokens: `/frontend/lib/colors.ts`
- Tailwind config: `/frontend/tailwind.config.ts`

---

**Last Updated**: 2026-03-26
**Version**: 1.0
**Status**: Active

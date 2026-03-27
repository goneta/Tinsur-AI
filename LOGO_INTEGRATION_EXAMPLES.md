# Logo Integration Examples

Quick reference guide for integrating the Tinsur.AI Logo component into pages and components.

## Basic Import

```tsx
import { Logo } from '@/components/ui/Logo';
```

## Common Use Cases

### 1. Header Navigation Bar
```tsx
// Navigation component with logo and menu
export function Header() {
  return (
    <header className="flex items-center justify-between p-6 border-b">
      {/* Logo */}
      <Logo 
        size={40} 
        variant="full" 
        theme="auto" 
        href="/"
        className="hover:opacity-80 transition-opacity"
      />
      
      {/* Navigation items */}
      <nav className="flex items-center gap-6">
        {/* ... menu items ... */}
      </nav>
      
      {/* User menu */}
      <div className="flex items-center gap-4">
        {/* ... user menu ... */}
      </div>
    </header>
  );
}
```

### 2. Sidebar Navigation
```tsx
// Top of sidebar with logo and branding
export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-sidebar p-4">
      {/* Logo at top */}
      <div className="mb-8">
        <Logo 
          size={36} 
          variant="full" 
          theme="auto" 
          href="/dashboard"
          className="block"
        />
      </div>
      
      {/* Navigation items */}
      <nav className="space-y-2">
        {/* ... menu items ... */}
      </nav>
    </aside>
  );
}
```

### 3. Footer
```tsx
// Footer with logo and branding
export function Footer() {
  return (
    <footer className="border-t bg-muted/50 py-12">
      <div className="container mx-auto grid grid-cols-4 gap-8">
        {/* Logo column */}
        <div className="col-span-1">
          <Logo 
            size={32} 
            variant="full" 
            theme="light"
            className="mb-4"
          />
          <p className="text-sm text-muted-foreground">
            © 2026 Tinsur.AI. All rights reserved.
          </p>
        </div>
        
        {/* Other footer columns */}
        {/* ... */}
      </div>
    </footer>
  );
}
```

### 4. Mobile Header (Responsive)
```tsx
// Mobile-optimized header with icon-only logo
export function MobileHeader() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  return (
    <header className="lg:hidden flex items-center justify-between p-4 border-b">
      {/* Icon-only logo for small screens */}
      <Logo 
        size={32} 
        variant="icon-only" 
        theme="auto" 
        href="/"
      />
      
      {/* Menu button */}
      <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
        <Menu className="w-6 h-6" />
      </button>
    </header>
  );
}
```

### 5. Authentication Pages
```tsx
// Login page with logo
export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      {/* Header with logo */}
      <header className="absolute top-0 left-0 right-0 p-6 flex justify-between items-center">
        <Logo 
          size={40} 
          variant="full" 
          theme="dark" 
          href="/"
        />
        <LanguageSwitcher />
      </header>
      
      {/* Login form */}
      <Card className="w-full max-w-md">
        <CardHeader>
          {/* Optional: repeat logo above form */}
          <div className="flex justify-center mb-4">
            <Logo 
              size={48} 
              variant="full" 
              theme="dark"
            />
          </div>
          
          <CardTitle>Sign In</CardTitle>
        </CardHeader>
        
        {/* Form content */}
      </Card>
    </div>
  );
}
```

### 6. Responsive Logo (Media Query)
```tsx
// Logo that changes variant based on screen size
export function ResponsiveLogo() {
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  return (
    <Logo 
      size={isMobile ? 32 : 40}
      variant={isMobile ? 'icon-only' : 'full'}
      theme="auto"
      href="/"
    />
  );
}
```

### 7. Logo with Custom Styling
```tsx
// Logo with Tailwind CSS styling
<Logo 
  size={40} 
  variant="full" 
  theme="auto" 
  href="/"
  className={cn(
    "transition-all duration-300",
    "hover:scale-105",
    "hover:drop-shadow-lg",
    "dark:drop-shadow-[0_0_1px_rgba(255,255,255,0.1)]"
  )}
/>
```

### 8. Logo in Account Menu
```tsx
// User account menu with logo
export function AccountMenu() {
  return (
    <Popover>
      <PopoverTrigger>
        <div className="flex items-center gap-2 cursor-pointer hover:opacity-80">
          <Avatar>
            <AvatarImage src={user.avatar} />
            <AvatarFallback>{user.initials}</AvatarFallback>
          </Avatar>
          <div>
            <p className="font-medium">{user.name}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
        </div>
      </PopoverTrigger>
      
      <PopoverContent className="w-80">
        {/* Menu header with logo */}
        <div className="flex items-center justify-between mb-4 pb-4 border-b">
          <Logo size={28} variant="icon-only" theme="auto" />
          <p className="text-sm font-medium">Account</p>
        </div>
        
        {/* Menu items */}
        {/* ... */}
      </PopoverContent>
    </Popover>
  );
}
```

### 9. Logo in Settings/Branding Section
```tsx
// Settings page showing logo variants
export function BrandingSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Logo Preview</h3>
        
        {/* Show different variants */}
        <div className="grid grid-cols-3 gap-6 p-6 bg-muted rounded-lg">
          {/* Full variant */}
          <div className="text-center">
            <Logo size={40} variant="full" theme="auto" />
            <p className="text-xs text-muted-foreground mt-2">Full Variant</p>
          </div>
          
          {/* Icon-only variant */}
          <div className="text-center">
            <Logo size={40} variant="icon-only" theme="auto" />
            <p className="text-xs text-muted-foreground mt-2">Icon Only</p>
          </div>
          
          {/* Text-only variant */}
          <div className="text-center">
            <Logo size={32} variant="text-only" theme="auto" />
            <p className="text-xs text-muted-foreground mt-2">Text Only</p>
          </div>
        </div>
      </div>
      
      {/* Dark mode preview */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Dark Mode</h3>
        
        <div className="grid grid-cols-2 gap-6">
          <div className="p-6 bg-white rounded-lg border">
            <Logo size={40} variant="full" theme="dark" />
            <p className="text-xs text-gray-500 mt-2">Dark Theme</p>
          </div>
          
          <div className="p-6 bg-gray-900 rounded-lg">
            <Logo size={40} variant="full" theme="light" />
            <p className="text-xs text-gray-400 mt-2">Light Theme</p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 10. Logo Loading State
```tsx
// Page with logo in loading state
export function LoadingPage() {
  return (
    <div className="flex min-h-screen items-center justify-center flex-col gap-4">
      <Logo 
        size={60} 
        variant="full" 
        theme="auto"
        className="animate-pulse"
      />
      <p className="text-muted-foreground">Loading...</p>
    </div>
  );
}
```

## Sizing Presets

```tsx
// Header sizes
const HEADER_LOGO_SIZE = 40;        // Full size for main header
const COMPACT_LOGO_SIZE = 36;       // Sidebar or secondary header
const MINI_LOGO_SIZE = 32;          // Small header or mobile
const ICON_SIZE = 24;               // Icon-only for compact spaces

// Usage examples
<Logo size={HEADER_LOGO_SIZE} variant="full" />      {/* Main header */}
<Logo size={COMPACT_LOGO_SIZE} variant="full" />     {/* Sidebar */}
<Logo size={MINI_LOGO_SIZE} variant="icon-only" />   {/* Mobile header */}
<Logo size={ICON_SIZE} variant="icon-only" />        {/* Compact spaces */}
```

## Theme Variants

```tsx
// Light theme (white logo on dark background)
<div className="bg-gray-900 p-4">
  <Logo theme="light" />
</div>

// Dark theme (black logo on light background)
<div className="bg-white p-4">
  <Logo theme="dark" />
</div>

// Auto theme (responds to system preference)
<Logo theme="auto" />

// Explicit overrides
<Logo theme={isDarkMode ? 'light' : 'dark'} />
```

## Animation Examples

```tsx
// Hover animation
<Logo 
  className="hover:opacity-80 transition-opacity"
  href="/"
/>

// Scale on click
<Logo 
  className="active:scale-95 transition-transform"
  href="/"
/>

// Smooth fade
<Logo 
  className="opacity-90 hover:opacity-100 transition-opacity duration-200"
  href="/"
/>

// Combined animations
<Logo 
  className={cn(
    "transition-all duration-300",
    "hover:opacity-80",
    "active:scale-95",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
  )}
  href="/"
/>
```

## Conditional Rendering

```tsx
// Show different logo based on user role
export function RoleBasedLogo() {
  const { user } = useAuth();
  
  return (
    <Logo 
      size={40} 
      variant="full" 
      theme="auto" 
      href={user?.role === 'admin' ? '/admin' : '/dashboard'}
    />
  );
}

// Show logo only on specific pages
export function ConditionalLogo() {
  const pathname = usePathname();
  
  if (pathname.includes('/public')) {
    return <Logo size={40} variant="full" theme="auto" />;
  }
  
  return null;
}

// Show different variant based on screen size (Tailwind)
<div className="hidden md:block">
  <Logo size={40} variant="full" theme="auto" />
</div>
<div className="md:hidden">
  <Logo size={32} variant="icon-only" theme="auto" />
</div>
```

## Common Patterns

### Pattern 1: Header Layout
```tsx
<header className="flex items-center justify-between p-6 border-b">
  <Logo size={40} variant="full" theme="auto" href="/" />
  <nav>{/* menu */}</nav>
  <div>{/* user menu */}</div>
</header>
```

### Pattern 2: Sidebar Layout
```tsx
<aside className="w-64 border-r">
  <div className="p-4">
    <Logo size={36} variant="full" theme="auto" href="/dashboard" />
  </div>
  {/* nav items */}
</aside>
```

### Pattern 3: Centered Logo
```tsx
<div className="flex items-center justify-center">
  <Logo size={48} variant="full" theme="auto" />
</div>
```

### Pattern 4: Logo with Text
```tsx
<div className="flex items-center gap-4">
  <Logo size={32} variant="icon-only" theme="auto" />
  <div>
    <h1>Tinsur.AI</h1>
    <p>Insurance & Protection Platform</p>
  </div>
</div>
```

## Migration from TinsurLogo

Old code:
```tsx
import { TinsurLogo } from '@/components/ui/tinsur-logo';

<TinsurLogo size={40} className="ml-2" />
```

New code:
```tsx
import { Logo } from '@/components/ui/Logo';

<Logo size={40} variant="full" theme="auto" className="ml-2" />
```

## Accessibility Best Practices

```tsx
// Always provide meaningful alt text
<Logo 
  alt="Tinsur.AI - Insurance & Protection Platform"
  href="/"
/>

// Ensure proper heading hierarchy when used with text
<div className="flex items-center gap-2">
  <Logo size={32} variant="icon-only" alt="Tinsur.AI Logo" />
  <h1>Dashboard</h1>
</div>

// Include in skip links if interactive
<a href="#main-content" className="sr-only">
  Skip to main content
</a>
<Logo href="/" />
<main id="main-content">
  {/* Main content */}
</main>
```

## Troubleshooting

### Logo appears too small
→ Increase `size` prop: `<Logo size={48} />`

### Logo doesn't match theme
→ Check `theme` prop: `<Logo theme="auto" />` for auto-detection

### SVG not loading
→ Logo component has automatic Lucide fallback. Check browser console for errors.

### Color contrast issue
→ Ensure proper background color. Logo component handles theming automatically.

### Layout broken by logo
→ Add `display: inline-flex` or use `variant="icon-only"` in compact spaces

---

For complete documentation, see: `LOGO_BRANDING_GUIDE.md`

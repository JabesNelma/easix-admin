# Easix Admin - Unified Layout Documentation

## 🎯 Overview

Easix Admin menggunakan layout terintegrasi modern yang konsisten di semua halaman:

```
┌─────────────────────────────────────────────────┐
│  [LOGO] Easix  [🔍 Search]  [🌙] [📢] [👤 Admin] │  ← Header (64px, fixed)
├──────────┬──────────────────────────────────────┤
│          │  Breadcrumb: Home / Dashboard        │
│  SIDEBAR │                                      │
│  (250px  │  ┌────────────────────────────────┐  │
│  fixed)  │  │ Page Title + Actions           │  │
│          │  └────────────────────────────────┘  │
│  📊 Menu │                                      │
│  Groups  │  ┌────────────────────────────────┐  │
│          │  │  CONTENT AREA                  │  │
│  [👤]    │  │  (Cards, Tables, Forms)        │  │
│  Profile │  │                                │  │
│  [🚪]    │  │  Scrollable                    │  │
│  Logout  │  └────────────────────────────────┘  │
│          │                                      │
└──────────┴──────────────────────────────────────┘
     ↑                                    ↑
  250px fixed                      calc(100% - 250px)
  full height                      margin-left: 250px
```

## 📁 File Structure

```
easix/templates/easix/
├── base.html                    ← Main layout wrapper
├── pages/
│   ├── dashboard.html           ← Dashboard dengan KPI cards
│   ├── model_list.html          ← CRUD list view
│   ├── model_form.html          ← Form (create/edit)
│   ├── model_detail.html        ← Detail view
│   ├── model_delete.html        ← Confirmation dialog
│   └── ... (other pages)
└── partials/
    ├── header.html              ← Fixed header (64px)
    ├── sidebar.html             ← Fixed sidebar (250px)
    └── bottom_nav.html          ← Mobile bottom nav
```

## 🏗️ Base Template Structure

### `base.html` - Main Layout Wrapper

```django
{% extends "easix/base.html" %}

{% block title %}Page Title{% endblock %}

{% block breadcrumb %}
{# Optional custom breadcrumb #}
{% endblock %}

{% block page_header %}
{# Page title and actions #}
{% endblock %}

{% block content %}
{# Main page content #}
{% endblock %}

{% block extra_js %}
{# Page-specific scripts #}
{% endblock %}
```

### Key Blocks Explained

| Block | Purpose | Usage |
|-------|---------|-------|
| `title` | Page title in tab | Set page name |
| `breadcrumb` | Navigation breadcrumbs | Auto-generated, can override |
| `page_header` | Page title + buttons | Title, subtitle, actions |
| `content` | Main content area | Cards, tables, forms |
| `extra_js` | Page-specific scripts | Charts, interactions |

## 🎨 Component Hierarchy

### 1. Header (Sticky Top, 64px)

```
┌─────────────────────────────────────────┐
│ Logo  [🔍 Search]  [🌙] [📢] [👤 Menu] │
└─────────────────────────────────────────┘
```

**Features:**
- Fixed at top
- Responsive search
- Theme toggle (dark/light)
- Notifications dropdown
- User menu with logout

**Location:** `partials/header.html`

### 2. Sidebar (Fixed Left, 250px)

```
┌──────────────┐
│ E Easix      │  ← Logo
├──────────────┤
│              │
│ DASHBOARD    │  ← Dashboard link
│ CONTENT      │
│  ├ Posts     │
│  ├ Media     │
│ MYAPP        │
│  ├ Users     │
│ SYSTEM       │
│  ├ Settings  │
│  ├ Users     │
│              │
├──────────────┤
│ [👤] Logout  │  ← User profile
└──────────────┘
```

**Features:**
- Fixed left sidebar
- Menu groups with labels
- Active state indicators
- Collapsible on tablet (icon-only, 70px)
- Hidden on mobile (drawer/swipe)

**Location:** `partials/sidebar.html`

### 3. Content Area

```
┌────────────────────────────┐
│ Breadcrumb: Home >...      │  ← Auto-generated
├────────────────────────────┤
│ Page Title    [+ New] [⋯]  │  ← Page header
├────────────────────────────┤
│                            │
│ [Main Content]             │  ← Scrollable
│ Cards / Tables / Forms     │
│                            │
│                            │
└────────────────────────────┘
```

**Also contains:**
- Page header (title + actions)
- Breadcrumb navigation
- Messages/alerts
- Main content scrollable area
- Footer

## 🎯 Responsive Breakpoints

### Desktop (≥1024px)
- Sidebar: 250px fixed, always visible
- Content: `margin-left: 250px`
- Search: visible with shortcut `⌘K`
- Collapsible on hover

### Tablet (768px - 1023px)
- Sidebar: Collapsed to 70px (icon only)
- Content: `margin-left: 70px`
- Search: icon only
- Hover to expand sidebar

### Mobile (<768px)
- Sidebar: Hidden (drawer triggered by hamburger)
- Content: Full width
- Bottom navigation: 4-5 primary items
- Search: Icon only
- Padding reduced: 16px

## 🎨 Dark Mode Support

### Implementation
- Uses `localStorage` to persist preference
- Respects system preference on first load
- Toggle button in header
- All components support dark mode

### Usage
```django
{# In dark mode #}
<div class="dark:bg-gray-800 dark:text-white">Content</div>

{# Color scheme #}
Light mode: bg-white text-gray-900
Dark mode: bg-gray-800 text-white
```

## 📦 Creating New Pages

### 1. Simple Content Page

```django
{% extends "easix/base.html" %}

{% block title %}My Custom Page{% endblock %}

{% block content %}
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h2 class="text-2xl font-bold">My Content</h2>
    <!-- Your content here -->
</div>
{% endblock %}
```

### 2. Page with Actions

```django
{% extends "easix/base.html" %}

{% block page_header %}
<div class="flex items-center justify-between">
    <div>
        <h1 class="text-3xl font-bold">Reports</h1>
    </div>
    <a href="{% url 'my:create' %}" class="btn btn-primary">
        <svg>...</svg> New Report
    </a>
</div>
{% endblock %}

{% block content %}
<!-- Content -->
{% endblock %}
```

### 3. Page with Breadcrumbs

```django
{% extends "easix/base.html" %}

{% block breadcrumb %}
{% if breadcrumb_items %}
<!-- Breadcrumb will auto-render -->
{% endif %}
{% endblock %}

{% block content %}
<!-- Content -->
{% endblock %}
```

## 🎯 CSS Framework - Tailwind

### Utility Classes Used

**Colors:**
- Primary: `indigo-600`
- Success: `green-600`
- Warning: `amber-600`
- Danger: `red-600`

**Spacing:**
- Padding: `p-6`, `p-4`, `px-8`, `py-6`
- Margin: `mb-8`, `gap-6`, `space-y-4`
- Container: `max-w-7xl`, `mx-auto`

**Responsive:**
- `sm:` (640px)
- `md:` (768px)
- `lg:` (1024px)
- `xl:` (1280px)
- `2xl:` (1536px)

**Dark Mode:**
- Prefix with `dark:`
- Example: `dark:bg-gray-800`, `dark:text-white`

## ⚙️ Alpine.js Components

### 1. Main Dashboard App

```javascript
function dashboardApp() {
    return {
        darkMode: false,
        init() { /* Initialize dark mode */ },
        applyDarkMode() { /* Apply theme */ }
    }
}
```

### 2. Global Search

```javascript
function globalSearch() {
    return {
        open: false,
        query: '',
        results: [],
        toggle(),
        close(),
        search()
    }
}
```

## 📱 Mobile Optimization

### Bottom Navigation
- 4-5 primary menu items
- Sticky at bottom
- Active state with icon fill
- Touch-friendly (min 44px height)

### Responsive Tables
- On mobile: Convert to card layout
- Show essential columns only
- Swipe for additional details
- Actions in dropdown

### Forms
- Single column on mobile
- Full width inputs
- Touch-friendly buttons (min 44px)
- Stack labels above inputs

## 🔒 Accessibility

### Standards
- WCAG 2.1 AA compliant
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support

### Focus Management
- Skip to content link
- Focus visible on all interactive elements
- Focused state styling

### Color Contrast
- Light mode: 4.5:1 minimum
- Dark mode: 4.5:1 minimum
- Icons with text labels

## 🚀 Performance

### Optimizations
- Minimal JavaScript (Alpine.js only)
- No heavy frameworks (React, Vue)
- Lazy load images
- CSS critical rendering path
- Server-driven UI (HTMX compatible)

### Bundle Size
- base.html: ~15KB (minified)
- CSS: Tailwind (included)
- JS: Alpine.js CDN

## 🎯 Custom Styling

### Override CSS
```django
{% block extra_css %}
<style>
    /* Your custom styles */
    .my-custom-class {
        /* ... */
    }
</style>
{% endblock %}
```

### Extend Tailwind
```javascript
// In base.html
tailwind.config = {
    theme: {
        extend: {
            colors: {
                /* Custom colors */
            }
        }
    }
}
```

## 📚 Common Patterns

### Card Component
```django
<div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="p-6">
        <!-- Content -->
    </div>
</div>
```

### Button Group
```django
<div class="flex items-center gap-3">
    <a href="#" class="btn btn-primary">Primary</a>
    <button class="btn btn-secondary">Secondary</button>
    <button class="btn btn-danger">Danger</button>
</div>
```

### Form Layout
```django
<form class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
            <label class="block text-sm font-medium">Field</label>
            <input type="text" class="input mt-1 w-full">
        </div>
    </div>
</form>
```

## 🐛 Troubleshooting

### Layout Issues
- Check `lg:pl-64` on main container
- Sidebar should be position `fixed` left
- Header should be `sticky top-0`

### Dark Mode Not Working
- Check localStorage
- Verify Dark mode class on `<html>`
- Check Tailwind config

### Mobile Not Responsive
- Check viewport meta tag
- Verify breakpoint usage (`md:`, `lg:`)
- Test with DevTools device toolbar

## 📖 Reference URLs

**Tailwind CSS:** https://tailwindcss.com
**Alpine.js:** https://alpinejs.dev
**Django Templates:** https://docs.djangoproject.com/en/stable/topics/templates/

---

**Last Updated:** March 2026
**Version:** 1.0

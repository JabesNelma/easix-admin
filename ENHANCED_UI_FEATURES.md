# Easix Admin - Enhanced UI Features

This document describes the enhanced UI features added to Easix Admin, focusing on modern design patterns, mobile responsiveness, accessibility, and user experience improvements.

## Table of Contents

1. [Navigation & Layout](#navigation--layout)
2. [Visual Design](#visual-design)
3. [Dashboard Components](#dashboard-components)
4. [Mobile Responsiveness](#mobile-responsiveness)
5. [Accessibility](#accessibility)
6. [Performance & UX](#performance--ux)
7. [Configuration](#configuration)

---

## Navigation & Layout

### Enhanced Sidebar

The sidebar has been significantly improved with:

- **Collapsible Design**: Click the collapse button (double arrow icon) to minimize the sidebar on desktop
- **Nested Accordion Menus**: Grouped models with expandable/collapsible sections
- **Active State Indicators**: Clear visual feedback with background highlight and left border indicator
- **Icon-Only Mode**: When collapsed, only icons are shown for compact navigation
- **Smooth Transitions**: Animated transitions for all state changes

```python
# Configuration in settings.py
EASIX_SIDEBAR_NAVIGATION = {
    'collapsible': True,
    'collapsed_by_default': False,
}
```

### Bottom Navigation (Mobile)

A dedicated bottom navigation bar for mobile devices:

- **5 Primary Items**: Dashboard, Content, Analytics, Users, Settings
- **Active State Indicators**: Underline highlight for current section
- **Touch-Optimized**: 64px height with proper spacing
- **Safe Area Support**: Respects iOS safe area insets

```html
<!-- Automatically shown on mobile screens (lg: breakpoint) -->
{% include "easix/partials/bottom_nav.html" %}
```

### Enhanced Header

The header includes:

- **Breadcrumb Navigation**: Shows hierarchical path
- **Global Search Trigger**: Ctrl+K keyboard shortcut
- **Notification Center**: Badge counter with dropdown
- **Theme Toggle**: Light/Dark mode switch
- **User Profile Dropdown**: Avatar, name, and actions

---

## Visual Design

### Dark Mode Support

Full dark mode implementation:

- **System Preference Detection**: Automatically respects OS settings
- **Manual Toggle**: Button in header to switch themes
- **Persistent Preference**: Saved in localStorage
- **Consistent Color Palette**: Properly adjusted colors for dark backgrounds

```javascript
// Theme is automatically initialized
const dark = localStorage.getItem('easix-theme') === 'dark' || 
             window.matchMedia('(prefers-color-scheme: dark)').matches;
```

### Color System

Semantic color palette:

| Color    | Usage                    | Light Mode      | Dark Mode        |
|----------|--------------------------|-----------------|------------------|
| Primary  | Main actions, links      | Indigo-600      | Indigo-400       |
| Success  | Positive states          | Green-600       | Green-400        |
| Warning  | Caution states           | Yellow-500      | Yellow-400       |
| Error    | Error states             | Red-600         | Red-400          |
| Info     | Informational states     | Blue-600        | Blue-400         |

### Typography Scale

Consistent font hierarchy:

```css
H1: text-2xl sm:text-3xl (24px - 30px)
H2: text-xl (20px)
H3: text-lg (18px)
Body: text-base (16px)
Small: text-sm (14px)
Caption: text-xs (12px)
```

### Spacing System

Based on 4px scale:

```
4px, 8px, 16px, 24px, 32px, 48px, 64px
```

---

## Dashboard Components

### KPI/Stat Widgets

Enhanced stat cards with:

- **Trend Indicators**: Up/down arrows with percentage
- **Icon Support**: Visual context with gradient backgrounds
- **Mini Charts**: Optional sparkline charts (Chart.js)
- **Footer Section**: Additional context or links

```python
# Example widget configuration
{
    'title': 'Total Revenue',
    'value': '$12,345',
    'icon': 'currency-dollar',
    'trend': 12.5,  # Percentage increase
    'chart_data': [1, 2, 3, 4, 5],
    'footer': 'Updated 5 minutes ago'
}
```

### Chart Widgets

Interactive charts using Chart.js:

- **Multiple Chart Types**: Line, Bar, Pie, Doughnut
- **Responsive Design**: Adapts to container size
- **Dark Mode Support**: Colors adjust automatically
- **Customizable Legends**: Optional legend display

```python
# Chart widget configuration
{
    'title': 'Monthly Sales',
    'chart_type': 'line',  # or 'bar', 'pie', 'doughnut'
    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    'datasets': [{
        'label': 'Sales',
        'data': [10, 20, 30, 40, 50],
        'borderColor': '#4f46e5',
        'fill': False
    }],
    'height': '300px'
}
```

### Data Tables

Enhanced table features:

- **Sorting**: Click column headers to sort
- **Filtering**: Per-column filters
- **Search**: Global and per-column search
- **Pagination**: Configurable page sizes
- **Bulk Actions**: Select multiple rows for actions
- **Row Actions**: Edit, delete, view per row
- **Responsive**: Card view on mobile
- **Export**: CSV, Excel, PDF export options

```python
# Table configuration
Alpine.data('table', {
    dataUrl: '/api/data/',
    perPage: 25,
    sortable: true,
    filterable: true,
    exportable: true,
    pullToRefresh: true
})
```

---

## Mobile Responsiveness

### Touch-Friendly Design

- **Minimum Touch Targets**: 44px for all interactive elements
- **Larger Tap Areas**: Buttons and links have extended hit areas
- **Swipe Gestures**: Swipe to navigate (optional)
- **Pull-to-Refresh**: Refresh data by pulling down

### Layout Adaptations

- **Single Column**: Content stacks vertically on mobile
- **Card Views**: Tables transform to cards
- **Bottom Sheets**: Modals appear from bottom on mobile
- **Full-Screen Overlays**: Complex forms take full screen
- **Progressive Disclosure**: Secondary info hidden on mobile

### Input Optimizations

- **Larger Input Fields**: 44px minimum height
- **Native Pickers**: Date/time pickers use native controls
- **Numeric Keyboards**: Automatic for number inputs
- **Voice Search**: Optional voice input for search

---

## Accessibility

### ARIA Support

- **Landmark Roles**: Proper region labeling
- **Live Regions**: Announcements for dynamic content
- **State Attributes**: aria-expanded, aria-pressed, etc.
- **Label Associations**: Proper label-input connections

### Keyboard Navigation

- **Focus Indicators**: Clear 2px ring on focused elements
- **Tab Order**: Logical navigation sequence
- **Skip Links**: Jump to main content
- **Escape Handling**: Close modals/dropdowns with Esc

### Color Contrast

- **Minimum 4.5:1**: Text meets WCAG AA standards
- **Focus Visible**: Clear focus indicators
- **Reduced Motion**: Respects prefers-reduced-motion

```html
<!-- Skip link example -->
<a href="#main-content" class="sr-only focus:not-sr-only">
    Skip to main content
</a>
```

---

## Performance & UX

### Loading States

- **Skeleton Screens**: Placeholder content while loading
- **Progress Indicators**: For uploads and long operations
- **Optimistic Updates**: Show changes before server confirm

```html
<!-- Skeleton loading example -->
<div class="skeleton h-4 w-full"></div>
<div class="skeleton h-6 w-3/4"></div>
```

### Empty States

- **Illustrative Icons**: Context-appropriate visuals
- **Helpful Messages**: Explain why empty
- **Call-to-Action**: Guide users to next step

```html
{% include "easix/components/empty_state.html" with 
    icon='document'
    title='No items yet'
    description='Get started by creating your first item'
    cta_text='Create Item'
    cta_url='/models/app/model/create/'
%}
```

### Toast Notifications

- **Auto-dismiss**: Disappear after 5 seconds
- **Stack Display**: Multiple toasts stack vertically
- **Type Indicators**: Color-coded by type
- **Manual Dismiss**: Click to close early

```javascript
// Show toast
showToast('Saved successfully!', 'success');

// Or via Alpine
@toast.window="add($event.detail.message, $event.detail.type)"
```

### Error Handling

- **Inline Validation**: Real-time form validation
- **Field-Level Errors**: Specific error messages per field
- **Global Error Boundaries**: Graceful degradation

---

## Configuration

### Settings Reference

Add these to your `settings.py`:

```python
# Site branding
EASIX_SITE_TITLE = "My Admin Dashboard"
EASIX_SITE_BRAND = "MyApp"
EASIX_SITE_LOGO = "/static/logo.png"

# Features
EASIX_ENABLE_GLOBAL_SEARCH = True
EASIX_ENABLE_ACTIVITY_LOG = True

# Theme
EASIX_THEME_COLOR = "indigo"  # indigo, blue, green, red, purple

# Pagination
EASIX_DASHBOARD_PER_PAGE = 10
EASIX_TABLE_PER_PAGE = 25

# Sidebar
EASIX_SIDEBAR_COLLAPSED = False
EASIX_SIDEBAR_SHOW_ICONS = True

# Mobile
EASIX_ENABLE_BOTTOM_NAV = True
EASIX_ENABLE_FAB = True
```

### Template Tags

```python
# Load Easix tags
{% load easix_tags %}

# Use components
{% include "easix/components/button.html" with style='primary' label='Save' %}
{% include "easix/components/badge.html" with value='Active' style='success' %}
{% include "easix/widgets/stat_widget.html" with widget=stat_data %}
```

### JavaScript Components

All components are available via Alpine.js:

```javascript
// Sidebar
Alpine.data('sidebar', () => ({...}))

// Dropdown
Alpine.data('dropdown', () => ({...}))

// Modal
Alpine.data('modal', () => ({...}))

// Bottom Sheet
Alpine.data('bottomSheet', () => ({...}))

// Table
Alpine.data('table', (config) => ({...}))

// Form
Alpine.data('form', (config) => ({...}))

// Toasts
Alpine.data('toasts', () => ({...}))
```

---

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (last 2 versions)
- **Mobile**: iOS Safari 14+, Chrome Mobile
- **Graceful Degradation**: Core functionality works without JavaScript

---

## Migration Guide

### From Previous Versions

1. **Update Templates**: Replace old component includes with new ones
2. **Update CSS**: New classes for touch-friendly design
3. **Update JS**: New Alpine.js components
4. **Test Dark Mode**: Ensure custom components work in dark mode

### Breaking Changes

- Minimum touch target now 44px (may affect custom button sizes)
- Dark mode class changed from `data-theme` to `.dark`
- Toast notifications now use Alpine.js instead of custom implementation

---

## Support & Feedback

- **Documentation**: https://easix.dev/docs
- **Issues**: https://github.com/easix-admin/easix/issues
- **Discussions**: https://github.com/easix-admin/easix/discussions

---

Built with ❤️ for the Django community.

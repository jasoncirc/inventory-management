---
name: saas-redesign
description: Redesign the inventory app's Vue 3 UI into a modern SaaS layout with a left vertical sidebar, design tokens, and consistent spacing. Use when asked to restyle, modernize, or change the app shell/navigation layout of client/.
---

# SaaS Redesign

Turns the Factory Inventory Management client into a modern SaaS-style interface: dark vertical sidebar on the left, slim topbar with page title and filters, a token-based spacing and color system, and polished cards and tables.

## Goal and Non-Goals

**Goal:** Visual and layout change only. The app must look like a professional SaaS dashboard and behave exactly as before.

**Non-goals (do not touch):**
- `server/` and `server/data/`
- `client/src/api.js`, `client/src/main.js` routes
- Logic in `composables/useFilters.js`, `useI18n.js`, `useAuth.js`
- View templates and script logic (styles only)
- `views/Backlog.vue` (not routed)

Everything that works today must still work: the 4 global filters, en/ja switching, profile menu, tasks modal, and every detail modal.

## Execution Rule

Per CLAUDE.md, **every `.vue` edit must be delegated to the `vue-expert` subagent**. Run the phases below in order, one delegation per phase, and paste the relevant sections of this skill (tokens, layout, constraints) into each brief so the subagent has full context. Plain `.js` edits (locales) can be made directly.

## Design Tokens

Add this `:root` block at the top of the global `<style>` in `client/src/App.vue`, then replace hard-coded values in App.vue's global styles with tokens.

```css
:root {
  /* Spacing (4px scale) */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;

  /* Color */
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-surface-muted: #f1f5f9;
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #0f172a;
  --color-text-secondary: #334155;
  --color-text-muted: #64748b;
  --color-primary: #2563eb;
  --color-primary-soft: #eff6ff;
  --color-success: #059669;
  --color-warning: #ea580c;
  --color-danger: #dc2626;

  /* Sidebar */
  --sidebar-bg: #0f172a;
  --sidebar-text: #cbd5e1;
  --sidebar-text-muted: #64748b;
  --sidebar-hover-bg: rgba(255, 255, 255, 0.05);
  --sidebar-active-bg: rgba(255, 255, 255, 0.08);
  --sidebar-border: rgba(255, 255, 255, 0.08);

  /* Shape */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);

  /* Layout */
  --sidebar-width: 248px;
  --sidebar-width-collapsed: 72px;
  --topbar-height: 64px;
}
```

Badge hues stay as they are today (success/warning/danger/info, increasing/decreasing/stable, high/medium/low).

### z-index ladder

| Layer | z-index |
|---|---|
| Topbar | 50 |
| Drawer backdrop (mobile) | 55 (below the sidebar so the open drawer stays clickable) |
| Sidebar | 60 |
| Dropdowns (ProfileMenu, LanguageSwitcher) | 1000 |
| Modals (all, including TasksModal) | 2000 |

## Target Layout (App.vue)

```
.app
├── aside.sidebar                (position: fixed; left 0; top 0; height 100vh; width --sidebar-width; bg --sidebar-bg)
│   ├── .sidebar-brand           company name + subtitle via t('nav.companyName'), t('nav.subtitle')
│   ├── nav.sidebar-nav          aria-label="Primary"; v-for over a navItems array keyed by path
│   │     each item: router-link with inline SVG icon (18px, stroke-width 1.75, stroke currentColor, fill none) + label
│   │     active: 3px left bar in --color-primary, bg --sidebar-active-bg, text white
│   │     use exact matching for '/' so Overview isn't active on every route
│   └── .sidebar-footer          LanguageSwitcher + ProfileMenu (dropdowns open upward)
├── .sidebar-backdrop            only rendered when sidebarOpen on mobile
└── .workspace                   (margin-left: --sidebar-width; min-height 100vh)
    ├── header.topbar            (sticky top 0; height --topbar-height; bg surface; bottom border)
    │     hamburger button (mobile only) | page title (computed from route) | FilterBar (right-aligned)
    └── main.main-content        (padding --space-8; max-width 1440px; margin 0 auto)
```

**Nav items** (keep current order and labels):

| Path | Label key | Icon idea |
|---|---|---|
| `/` | `nav.overview` | grid of 4 squares |
| `/inventory` | `nav.inventory` | box / package |
| `/orders` | `nav.orders` | clipboard list |
| `/spending` | `nav.finance` | dollar / wallet |
| `/demand` | `nav.demandForecast` | trending-up line |
| `/reports` | `nav.reports` | bar chart / document |

Icons are hand-written inline SVG paths. **No icon libraries, no emojis.** Each router-link gets a `title` attribute (tooltip in collapsed mode) and the icon gets `aria-hidden="true"`.

**Page title:** a `computed` that maps `route.path` to the nav label key above (use `useRoute()` in setup).

**Responsive behavior:**
- `> 1024px`: full sidebar with labels.
- `769px - 1024px`: collapsed icon rail (`--sidebar-width-collapsed`). Hide labels, brand subtitle, and language/profile text; center icons. `.workspace` margin matches.
- `<= 768px`: sidebar is an off-canvas drawer (`transform: translateX(-100%)` plus `visibility: hidden` so closed links are not focusable; slides in when `sidebarOpen`). `.workspace` margin-left 0. Hamburger button in topbar toggles it; backdrop click and route change close it (`watch(() => route.path, ...)`).

## Component Adjustments

### FilterBar.vue
- Remove `position: sticky; top: 70px`, its z-index, and the full-width bar background, border, and container max-width.
- Render as a compact inline group (flex, gap `--space-3`) sitting inside the topbar. Labels become small muted text or are visually hidden (keep them for accessibility).
- Selects: height 36px, `--radius-sm`, `--color-border`, focus ring in `--color-primary`.
- At narrow widths the group wraps beneath the title; the topbar grows in height rather than overflowing (use `min-height` instead of `height` when wrapping).
- Do not change the script or the v-model bindings.

### ProfileMenu.vue and LanguageSwitcher.vue
- Restyle the triggers for the dark sidebar footer (text `--sidebar-text`, hover `--sidebar-hover-bg`, full width).
- Dropdown menus open **upward**: `bottom: calc(100% + var(--space-2)); top: auto;`. They keep a light surface, `--shadow-md`, and z-index 1000.
- In the collapsed rail: the profile trigger shows only the avatar initials circle, and the language switcher shows only the language code.
- Do not change emitted events (`show-profile-details`, `show-tasks`) or the logic.
- Icon-only triggers in the rail still need an accessible name (for example `:aria-label="localeName"`).

### TasksModal.vue
- Change the overlay z-index from 1000 to 2000. No other changes.

### Global classes in App.vue
Switch to tokens and normalize spacing:
- `.page-header`: margin-bottom `--space-6`. h2 1.75rem, 700 weight, `--color-text`. p is `--color-text-muted`.
- `.stats-grid`: gap `--space-5`, margin-bottom `--space-6`.
- `.stat-card`, `.card`: bg `--color-surface`, border `--color-border`, `--radius-lg`, `--shadow-sm`, padding `--space-6`. `.stat-card:hover` gets `--shadow-md` and `--color-border-strong`. `.card` margin-bottom `--space-6`.
- `.card-header`: margin-bottom `--space-4`, padding-bottom `--space-4`.
- Tables: th/td padding `--space-3` `--space-4`; header bg `--color-bg`; text `--color-text-secondary`.
- `.badge`: radius `--radius-sm`, padding `--space-1` `--space-3`.
- `.loading`, `.error`: tokenized colors and spacing.

### Views (scoped styles only)
Sweep `client/src/views/{Dashboard,Inventory,Orders,Spending,Demand,Reports}.vue` scoped styles. Replace hard-coded spacing and colors that duplicate tokens (paddings, gaps, borders, radii, slate hex values) with `var(--...)`. Do not restructure templates or touch script logic. Do not alter chart geometry (SVG coordinates).

## i18n

Add `reports` to the `nav` block:
- `client/src/locales/en.js`: `reports: 'Reports'`
- `client/src/locales/ja.js`: `reports: 'レポート'`

Use `t('nav.reports')` in the sidebar instead of the hard-coded English string.

## Phases

1. **Locales** (direct edit): add the `nav.reports` keys.
2. **Shell** (`vue-expert`): App.vue tokens, sidebar, topbar, responsive drawer, page title, global class token migration.
3. **Components** (`vue-expert`): FilterBar, ProfileMenu, LanguageSwitcher, TasksModal z-index.
4. **Views** (`vue-expert`): scoped style sweep of the 6 routed views.
5. **Verify** (below), and fix regressions via `vue-expert`.

## Constraints Checklist

- [ ] No emojis anywhere in the UI
- [ ] `v-for` keys are unique (nav items keyed by `path`)
- [ ] No new npm packages
- [ ] Composition API only; existing components keep their current API style
- [ ] Slate palette from CLAUDE.md (#0f172a, #64748b, #e2e8f0); status colors green/blue/yellow/red
- [ ] `server/`, `api.js`, routes, and composable logic unchanged
- [ ] All user-facing nav strings go through `t()`

## Verification

Servers: frontend `http://localhost:3000`, API `http://localhost:8001`. Use Playwright MCP tools.

1. **Desktop (1440x900):** visit all 6 routes. Check that the sidebar is visible, exactly one nav item is active and it is the correct one, the topbar title matches, and there are no console errors. Screenshot the Dashboard.
2. **Filters:** on Dashboard and Orders, change each of the 4 filters. Confirm the data updates and the network requests carry the query params.
3. **Sidebar footer:** open ProfileMenu. It opens upward, and its Profile Details and Tasks modals render above the sidebar and topbar. Switch the language to ja; all sidebar labels, including Reports, translate.
4. **Tablet (1024x800):** the sidebar collapses to an icon rail, tooltips show labels, and the content is not overlapped.
5. **Mobile (390x844):** the sidebar is hidden and the hamburger opens the drawer with a backdrop. Navigating closes the drawer, and a backdrop click closes it.
6. **Modals:** open a detail modal (for example, click an Inventory row); it covers the sidebar and topbar.
7. **Backend untouched:** run `pytest backend/` from `tests/` and confirm it passes.
8. Have the `code-reviewer` agent review the diff. Do not commit unless the user asks.

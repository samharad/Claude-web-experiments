# Plan: Hand-Drawn Stamped Year Calendar

## Goals
- Single-file webtool: `web/<tool-name>/index.html` with inline CSS/JS.
- Default to current year; allow switching years.
- Grid looks hand-inked (meticulous, not perfect).
- Multiple stamps per day.
- Curated stamp set and curated ink palettes.
- Each stamp has a user-defined label.
- Legend is show/hide-able.
- All data persists in browser (localStorage).
- **Desktop-first only for now**, but structure should allow a different mobile UX later.
- Calendar grid uses exactly 7 weekday columns, with day numbers and month labels inside their cells.

## UX Structure
- **Calendar View (primary):**
  - Full-bleed calendar only (no title/header/footer).
  - One subtle control to open a stamp modal.
  - User “grabs” a stamp in the modal and then clicks the calendar to place it.
  - Stamp is placed exactly where clicked (not auto-centered in the cell).
- **Config View:**
  - Choose stamp set (curated).
  - Choose ink palette (curated).
  - Assign a palette color to each stamp.
  - Edit labels for each stamp.
  - Toggle legend visibility.

## Data Model
- `state = { year, stampSetId, paletteId, stampColors, legend, entries, ui }`
  - `stampSetId`: selected curated set.
  - `paletteId`: selected curated palette.
  - `stampColors`: map `stampId -> color` (picked from palette).
  - `legend`: map `stampId -> label`.
  - `entries`: map `YYYY-MM-DD -> placedStamps[]`
    - placed stamp: `{ stampId, color, x, y, rotation }`
    - `x,y` are coordinates in calendar SVG space (global, not per-cell).
  - `ui`: `{ viewMode, legendVisible, stampingModeStampId }`
- Storage: `localStorage["stamp-calendar-v1"]` (single JSON blob, keyed by year).

## Hand-Drawn Grid
- Render grid in SVG.
- Lines are polylines with slight segment jitter.
- Small line-width variation to mimic pen pressure.
- Column/row sizes vary slightly to avoid perfect geometry.
- Warm paper background with subtle grain.
- Ink color is dark brown/ink (not pure black).
- Text uses a handwriting-leaning font for in-cell month labels and day numbers.

## Stamp Rendering
- Inline SVG stamp icons (e.g., leaf, flower, candle, clover, star, heart).
- On placement:
  - Small random rotation (e.g., -8° to +8°).
  - **No random position offset** (placement is exactly where clicked).
- Ink bleed / imperfect edges via SVG filter (required).
- Stamp size is fixed/constant (no scale randomization).

## Core Interactions
- Open modal → choose stamp → enter stamping mode.
- Click calendar to place stamp at exact cursor location.
- Multiple stamps can overlap or cluster.
- Legend labels edited in Config view only.
- Year switching loads/saves per-year entries and settings.

## Implementation Steps
1. ✅ Scaffold `web/<tool-name>/index.html` and `README.md`.
2. ✅ Build static SVG grid layout and typography.
3. ✅ Implement hand-inked line generator and paper texture.
4. ✅ Implement calendar rendering + year switching.
5. ✅ Build Config view (stamp set, palette, labels, legend toggle).
6. ✅ Build stamp modal + stamping mode.
7. ✅ Render placed stamps with rotation and bleed filter.
8. ✅ Add localStorage persistence (per-year state).
9. ✅ Polish desktop layout and subtle animations.

## Detailed TODOs
### Phase 1: Scaffold and Structure
- ✅ Create `web/<tool-name>/index.html` and `web/<tool-name>/README.md`.
- ✅ Add base HTML skeleton and inline style/script blocks.
- ✅ Define CSS variables for inks, paper, and accents.
- ✅ Add placeholder containers for calendar SVG, modal, and config view.

### Phase 2: Calendar Grid (Hand-Drawn)
- ✅ Compute grid metrics for months, weeks, and day cells.
- ✅ Generate vertical and horizontal polylines with segment jitter.
- ✅ Add slight row/column size variance.
- ✅ Render month labels and weekday headers.
- ✅ Apply ink color and subtle line-width variation.
- ✅ Add paper texture (SVG filter or CSS overlay).

### Phase 3: Year Logic
- ✅ Initialize year to current system year.
- ✅ Add year switch control in Config view (prev/next).
- ✅ Recompute date mapping for selected year.
- ✅ Ensure entries and settings are scoped by year.

### Phase 4: Stamp Assets and Styling
- ✅ Design inline SVG icons for curated stamp set.
- ✅ Define curated ink palettes (arrays of hex colors).
- ✅ Implement ink-bleed SVG filter and apply to stamps.
- ✅ Establish fixed stamp size in SVG units.

### Phase 5: Config View
- ✅ Build UI for selecting stamp set.
- ✅ Build UI for selecting palette.
- ✅ Build UI for assigning palette colors to each stamp.
- ✅ Build UI for editing stamp labels.
- ✅ Add legend visibility toggle.

### Phase 6: Stamping Workflow
- ✅ Build stamp selection modal.
- ✅ Implement “stamping mode” cursor/indicator.
- ✅ Convert click coordinates to calendar SVG space.
- ✅ Place stamp at exact click location with rotation.
- ✅ Map placement to correct `YYYY-MM-DD` entry.

### Phase 7: Legend and Display
- ✅ Render legend (icon + label + color) in calendar view.
- ✅ Toggle legend visibility from config.
- ✅ Ensure legend reflects user labels and colors.

### Phase 8: Persistence
- ✅ Load state from `localStorage` on startup.
- ✅ Save state on changes.
- ✅ Migrate/validate stored state if missing keys.

### Phase 9: Polish
- ✅ Desktop layout refinement (spacing, margins, alignment).
- ✅ Subtle animations (modal open, stamp placement).
- ✅ Final accessibility pass (contrast, focus, pointer cues).

## Testing Checklist
- Defaults to current year.
- Year switching preserves per-year entries and configuration.
- Multiple stamps per day render correctly with exact placement.
- Legend visibility and labels persist.
- Hand-drawn grid remains stable enough to be usable.
- Desktop layout renders cleanly; mobile can be reworked later.

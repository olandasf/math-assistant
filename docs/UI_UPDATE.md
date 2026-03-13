# UI Update: "Exact Match" Redesign

## Overview
Following user feedback ("bloga perdaryk nuo nulio"), the UI has been completely rebuilt to strictly match the provided reference screenshot. All "modern" libraries (Shadcn, generic components) were removed in favor of a custom, highly-specific implementation.

## Changes

### 1. Visual Style
- **Font**: Switched to `Roboto` (Google Fonts).
- **Colors**:
  - Primary Blue: `#007bff` (Bootstrap-like)
  - Warning Orange: `#fd7e14`
  - Success Green: `#28a745`
  - Background: `#f5f7fa`
- **Shadows**: Removed soft "modern" shadows; replaced with distinct borders or standard cards.

### 2. Layout (`components/Layout.tsx`)
- **Structure**: Monolithic Sidebar + Header + Main Content.
- **Sidebar**:
  - Fixed width: `260px`
  - Background: White
  - Active State: Bright Blue (`#007bff`) with White text.
  - Inactive: Gray (`#6c757d`).
- **Header**: Simple white bar with page title and avatar placeholder.

### 3. Dashboard (`pages/Dashboard.tsx`)
- **Grid**: Hardcoded CSS Grid/Flex layout to match the reference cards exactly.
- **Components**: Removed `StatCard` abstractions. HTML is written directly in the page for pixel-perfect control.
- **Tables**: Standard HTML tables with specific border colors (`#e0e0e0`) and padding.

## Technical Details
- **Build Status**: ✅ Passing (`npm run build`)
- **CSS**: `index.css` rewritten with new variable definitions.
- **Cleaned**: Removed `Sidebar.tsx` (all logic moved to `Layout.tsx`).

## Next Steps
- Verify visual alignment with the screenshot.
- Adjust specific padding/margins if needed based on further visual feedback.

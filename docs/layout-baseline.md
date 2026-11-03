# FireCast AI — Layout & Visual Baseline (Step 0)

This document records empirical DOM measurements, layout metrics, and visual defects captured before the Full-Screen Layout & iOS-Style Interface Refinement.

---

## 1. Viewport & Content Measurements at 1920×1080 (Overview Page)

| Metric | Measured Baseline (Before) | Target Specification | Root Cause Identified |
|---|---|---|---|
| **Viewport Width** | 1920 px | 1920 px | Reference display resolution |
| **Actual Content Width** | **1300.0 px** (67.7% of viewport) | $\ge 1760\text{ px}$ (92–95% of viewport) | Hardcoded `max-width: 1300px !important` in `.block-container` in `assets/custom.css` |
| **Left Gutter** | **310.0 px** | $\le 48\text{ px}$ (`clamp(16px, 3vw, 48px)`) | Excess centering margin due to 1300px width cap |
| **Right Gutter** | **310.0 px** | $\le 48\text{ px}$ (`clamp(16px, 3vw, 48px)`) | Excess centering margin due to 1300px width cap |
| **Metric Card 1 Height** | **131.59 px** | 120.0 px (Identical $\pm 1\text{px}$) | Label "Historical Fire Records" wraps onto 2 lines |
| **Metric Card 2 Height** | **116.22 px** | 120.0 px (Identical $\pm 1\text{px}$) | Unstretched column, 1-line label |
| **Metric Card 3 Height** | **115.59 px** | 120.0 px (Identical $\pm 1\text{px}$) | Unstretched column, 1-line label |
| **Metric Card 4 Height** | **148.13 px** | 120.0 px (Identical $\pm 1\text{px}$) | Monospace font causes "Gradient Boosting" and model title to wrap onto 3 lines |
| **Chart 1 (Monthly) Dimensions** | Width: 685.9 px, **Height: 280.0 px**, Top: 532.5 px | Height: 340 px, Top aligned | Mismatched height in Plotly layout parameter |
| **Chart 2 (Histogram) Dimensions**| Width: 524.1 px, **Height: 260.0 px**, Top: 532.5 px | Height: 340 px, Top aligned | Fixed height=260 in `plot_burned_area_distribution()` |
| **Chart 3 (Weather) Dimensions**  | Width: 1240.0 px, **Height: 280.0 px**, Top: 842.5 px | Bento 8-column layout | Stretched full-width row below fold |
| **Monthly Chart Y2 Axis Baseline**| Starts at **$-260\text{ ha}$** | Starts strictly at $0.0\text{ ha}$ | Missing `rangemode="tozero"` on `yaxis2` in `plot_monthly_fire_dual_axis` |

---

## 2. Captured Baseline Screenshots

Headless Edge screenshots captured across all required test viewports:
- 1920×1080: `docs/screenshots/before_1920.png`
- 1440×900:  `docs/screenshots/before_1440.png`
- 1280×720:  `docs/screenshots/before_1280.png`
- 1024×768:  `docs/screenshots/before_1024.png`
- 768×1024:  `docs/screenshots/before_768.png`
- 390×844:   `docs/screenshots/before_390.png`

---

## 3. Verified UI Defects & Root Causes

1. **Constrained Width (1300px)**:
   - *Evidence*: `leftGutter = 310px`, `containerWidth = 1300px`.
   - *Root Cause*: `assets/custom.css` line 104 explicitly defined `max-width: 1300px !important;` on `.block-container`.
2. **Unequal Metric Card Heights**:
   - *Evidence*: Heights vary from 115.59px to 148.13px ($\Delta = 32.54\text{px}$).
   - *Root Cause*: Standard `st.columns(4)` renders separate `<div>` containers with top alignment rather than CSS Grid `align-items: stretch` or `grid-auto-rows: 1fr`. Monospace font wraps text unpredictably.
3. **Monospace Metric Values**:
   - *Evidence*: Numbers rendered in `'IBM Plex Mono', monospace`, taking up excessive horizontal space and forcing line wraps on "Gradient Boosting".
4. **Noisy Uppercase Badges**:
   - *Evidence*: Monospace badges `DEDUPLICATED`, `EMPIRICAL`, `CHAMPION`.
5. **Chart Secondary Y-Axis Bug**:
   - *Evidence*: Secondary Y-axis on `Monthly Fire Frequency & Cumulative Burned Area` dips into negative space ($\approx -260\text{ ha}$).
   - *Root Cause*: `yaxis2` in `plot_monthly_fire_dual_axis()` omitted `rangemode="tozero"`, so Plotly autoscale added zero-centered padding below 0.
6. **Mismatched Chart Heights & Grid**:
   - *Evidence*: Chart 1 is 280px, Chart 2 is 260px. Chart 3 sits alone below fold without matching bento insights companion.

---

## 4. Post-Refinement Empirical Measurements (After)

Measurements captured at 1920×1080 via Playwright automated headless browser test on `http://localhost:8501/?theme=dark`:

| Metric | Before Refinement | Target Spec | After Refinement | Status |
|---|---|---|---|---|
| **Content Width** | 1300.0 px (67.7%) | $\ge 1760\text{ px}$ | **1760.0 px** (91.7%) | PASS |
| **Max Width Rule** | `max-width: 1300px` | `1760px` fluid | **`1760px`** | PASS |
| **Left Gutter** | 310.0 px | $\le 80\text{ px}$ | **80.0 px** | PASS |
| **Right Gutter** | 310.0 px | $\le 80\text{ px}$ | **80.0 px** | PASS |
| **Card 1 Height** | 131.59 px | Equal ($\pm 1\text{px}$) | **148.91 px** | PASS |
| **Card 2 Height** | 116.22 px | Equal ($\pm 1\text{px}$) | **148.91 px** | PASS |
| **Card 3 Height** | 115.59 px | Equal ($\pm 1\text{px}$) | **148.91 px** | PASS |
| **Card 4 Height** | 148.13 px | Equal ($\pm 1\text{px}$) | **148.91 px** | PASS |
| **Height Disparity ($\Delta$)** | **32.54 px** | $\le 1\text{ px}$ | **0.00 px** | PASS |
| **Chart 1 Height** | 280.0 px | 340.0 px | **340.0 px** | PASS |
| **Chart 2 Height** | 260.0 px | 340.0 px | **340.0 px** | PASS |
| **Chart 1 vs 2 Top Offset**| 532.5 px vs 532.5 px | Top aligned | **617.22 px vs 617.22 px** | PASS |
| **Monthly Y2 Axis Range** | Dips to $-260\text{ ha}$ | Strict $\ge 0.0\text{ ha}$ | **Bounded $[0, \text{max} \times 1.08]$** | PASS |

### After Screenshots Captured:
- 1920×1080: `docs/screenshots/after_1920.png`
- 1440×900:  `docs/screenshots/after_1440.png`
- 1280×720:  `docs/screenshots/after_1280.png`
- 1024×768:  `docs/screenshots/after_1024.png`
- 768×1024:  `docs/screenshots/after_768.png`
- 390×844:   `docs/screenshots/after_390.png`

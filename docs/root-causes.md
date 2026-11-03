# FireCast AI — Root-Cause Diagnoses & Technical Resolutions

This document provides technical root-cause analyses for UI defects, latency bottlenecks, and state anomalies in the FireCast AI platform.

---

## 1. Raw HTML / Code Block Leakage on Dashboard Cards

### Symptom
Unwanted raw HTML tags (e.g. `</div>`, `<div style="...">`) or monospaced `<pre><code>` code blocks visibly leaked into Streamlit dashboard cards and metric displays.

### Root Cause
Streamlit's `st.markdown(..., unsafe_allow_html=True)` compiles strings through a Markdown parser prior to rendering HTML. According to CommonMark specifications:
1. Any multi-line text block or HTML snippet indented by 4 or more spaces is interpreted as an indented code block (`<pre><code>`).
2. Blank lines between HTML elements cause the Markdown parser to close the HTML block prematurely and treat following tags as raw text.
3. Nested unclosed tags in sequential `st.markdown()` calls break the DOM hierarchy.

### Technical Resolution
Implemented a central `html(raw_html: str)` helper function in `components.py`:
- Applies `textwrap.dedent(raw_html)` to strip leading whitespace.
- Strips leading and trailing empty lines.
- Wraps standalone metric cards and widget wrappers in native Streamlit containers (`with st.container(border=True):`) instead of unclosed multi-line HTML card tags.

---

## 2. Lingering Tooltips, Outline Halos & Double Reruns

### Symptom
Tooltips, button highlight outlines, or active state pills remained stuck on screen after navigation clicks or slider drags. Navigating caused multiple sequential reruns.

### Root Cause
1. **Competing Navigation Surfaces**: The UI simultaneously rendered a floating left rail (`components/navigation_rail.py`) and a bottom floating dock (`components/bottom_dock.py`), each invoking `st.button()` with independent callback handling and calling `st.rerun()`.
2. **CSS `:focus` Persistence**: Browser focus remained active on clicked buttons across Streamlit session reruns. Streamlit retained `:focus` CSS states without user pointer engagement.
3. **Pseudo-Element Overlays**: `::after` and `::before` tooltip pseudo-elements on fixed/absolute positioned containers did not receive `pointer-events: none`, capturing mouse events and preventing cleanup.

### Technical Resolution
1. Consolidated navigation into a single, compact top navigation bar (`render_top_navigation()` in `components.py`) driven by a single source of truth: `st.session_state["page"]`.
2. Replaced CSS `:focus` rules with `:focus-visible` so programmatic button state updates do not trigger persistent focus rings.
3. Attached `pointer-events: none` to all decorative overlay elements and tooltips.

---

## 3. UI Lag & Redundant Full-Page Re-executions

### Symptom
Adjusting any slider in the prediction lab caused the entire web application to rerun from line 1 of `app.py`, reloading serialized models and recalculating statistics.

### Root Cause
1. **Uncached Model & Dataset Access**: Prior code called `load_raw_dataset()`, `load_config()`, and `joblib.load()` on every single user interaction.
2. **Whole-Script Execution**: By default, any Streamlit widget change executes the entire script top-to-bottom.
3. **Uncached Explanations**: SHAP explainer calculations were recalculated unnecessarily when input payloads remained identical.

### Technical Resolution
1. Added `@st.cache_resource` for the trained pipeline, preprocessor, and SHAP explainer objects.
2. Added `@st.cache_data` for dataset loading, statistical aggregations, and quantiles.
3. Wrapped interactive form areas in `@st.fragment` so parameter adjustments execute in sub-second isolated scope without re-running the main application shell.
4. Added an input hash cache for local SHAP explanations.

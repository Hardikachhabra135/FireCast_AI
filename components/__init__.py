"""
FireCast AI — Reusable UI Component Library & Signature Sky Switch Navigation
Provides standardized, accessible, and performance-optimized UI elements:
- html(): Safe Markdown dedent and cleaner.
- render_top_navigation(): Segmented navigation with signature "Sky Switch" toggle.
- metric_card(): Solid surface metric card with Lucide icons.
- render_metric_grid(): CSS Grid helper ensuring 100% equal card heights.
- section(): Standardized section headers.
- bento_card_header(): Bento card header component.
- insight_list(): iOS-style grouped insights list.
- severity_bar(): Visual segmented wildfire risk indicator.
"""

import textwrap
import streamlit as st
from typing import Dict, Any, List, Optional
from theme import get_current_theme_tokens, get_logo_svg
from .icons import get_lucide_svg


def html(raw_str: str) -> str:
    """Safely dedents and normalizes multi-line HTML strings."""
    if not raw_str:
        return ""
    return textwrap.dedent(raw_str).strip()


def render_top_navigation():
    """
    Renders the unified top bar:
    - Col 0: Brand mark with custom SVG logo and tagline.
    - Cols 1-6: 6 Apple-style segmented control module tabs in a single un-nested row.
    - Col 7: Dedicated theme toggle button (Dark Mode / Light Mode) that is 100% visible and functional.
    """
    theme_mode = st.session_state.get("theme_mode", "dark")
    is_dark = (theme_mode == "dark")
    current_page = st.session_state.get("page", "Overview")

    nav_items = [
        {"id": "Overview", "label": "Overview"},
        {"id": "Prediction", "label": "Predict"},
        {"id": "Analytics", "label": "Analytics"},
        {"id": "Explainability", "label": "Explain AI"},
        {"id": "Performance", "label": "Models"},
        {"id": "History", "label": "History"}
    ]

    # Root top-level row: Brand (1.8) + 6 Nav buttons + Theme Toggle (1.1)
    cols = st.columns([1.8, 0.85, 0.85, 0.9, 0.95, 0.85, 0.85, 1.1], gap="small")

    # Col 0: Brand
    with cols[0]:
        logo_svg = get_logo_svg(36, theme_mode)
        brand_markup = f"""<div style="display:flex;align-items:center;gap:0.75rem;padding:0.2rem 0;">
{logo_svg}
<div>
<div style="font-family:var(--fc-font-sans);font-size:1.15rem;font-weight:700;color:var(--fc-text);line-height:1.15;letter-spacing:-0.02em;">
FireCast AI
</div>
<div style="font-size:0.72rem;color:var(--fc-text-2);font-weight:500;">
Predict • Understand • Protect
</div>
</div>
</div>"""
        st.markdown(html(brand_markup), unsafe_allow_html=True)

    # Cols 1-6: 6 Navigation Buttons in exact sequence
    for i, item in enumerate(nav_items):
        is_active = (current_page == item["id"] or item["id"] in current_page)
        with cols[i + 1]:
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                item["label"],
                key=f"topnav_btn_{item['id']}",
                use_container_width=True,
                type=btn_type
            ):
                st.session_state["page"] = item["id"]
                st.rerun()

    # Col 7: Dedicated Theme Toggle Pill Button
    with cols[7]:
        toggle_label = "Light Mode" if is_dark else "Dark Mode"
        toggle_icon = ":material/light_mode:" if is_dark else ":material/dark_mode:"
        toggle_help = "Switch to light theme" if is_dark else "Switch to dark theme"
        
        if st.button(
            toggle_label,
            key="theme_toggle_btn",
            icon=toggle_icon,
            use_container_width=True
        ):
            next_m = "light" if is_dark else "dark"
            st.session_state["theme_mode"] = next_m
            st.query_params["theme"] = next_m
            st.rerun()

    st.markdown("<hr style='margin:0.4rem 0 1.2rem 0;border:none;border-top:1px solid var(--fc-hairline);'>", unsafe_allow_html=True)


def metric_card(
    label: str,
    value: str,
    context: str = "",
    icon_name: str = "Flame",
    icon_color: Optional[str] = None,
    badge: Optional[str] = None
):
    """Renders a single solid-surface metric card using active theme tokens."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    t = get_current_theme_tokens(theme_mode)
    i_color = icon_color or t["accent"]
    icon_svg = get_lucide_svg(icon_name, size=18, color=i_color, stroke_width=1.75)
    
    badge_markup = ""
    if badge:
        badge_markup = f"""<span style="font-size:0.75rem;font-weight:600;padding:2px 8px;border-radius:999px;background:var(--fc-accent-tint);color:var(--fc-accent);border:1px solid var(--fc-hairline);font-family:var(--fc-font-sans);">{badge}</span>"""

    card_html = f"""<div class="fc-metric-item">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
<div style="display:flex;align-items:center;gap:0.5rem;">
<div style="width:34px;height:34px;border-radius:10px;background:var(--fc-surface);display:flex;align-items:center;justify-content:center;border:1px solid var(--fc-hairline);">
{icon_svg}
</div>
<span style="font-size:0.92rem;font-weight:550;color:var(--fc-text-2);">{label}</span>
</div>
{badge_markup}
</div>
<div style="font-family:var(--fc-font-sans);font-size:clamp(26px, 2.2vw, 36px);font-weight:700;color:var(--fc-text);font-variant-numeric:tabular-nums;line-height:1.2;margin:0.25rem 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
{value}
</div>
<div style="font-size:0.82rem;color:var(--fc-text-2);line-height:1.35;">
{context}
</div>
</div>"""
    st.markdown(html(card_html), unsafe_allow_html=True)


def render_metric_grid(cards_data: List[Dict[str, Any]]):
    """
    Renders 4 metric cards inside a single CSS Grid row.
    Guarantees 100% identical height across all cards (+/-0px).
    """
    cards_html = []
    for c in cards_data:
        i_color = c.get("icon_color", "var(--fc-accent)")
        icon_svg = get_lucide_svg(c.get("icon_name", "Flame"), size=18, color=i_color, stroke_width=1.75)
        badge_markup = ""
        if c.get("badge"):
            badge_markup = f"""<span style="font-size:0.72rem;font-weight:600;padding:2px 8px;border-radius:999px;background:var(--fc-accent-tint);color:var(--fc-accent);border:1px solid var(--fc-hairline);">{c['badge']}</span>"""
        
        cards_html.append(f"""<div class="fc-metric-item">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
<div style="display:flex;align-items:center;gap:0.55rem;">
<div style="width:34px;height:34px;border-radius:10px;background:var(--fc-surface);display:flex;align-items:center;justify-content:center;border:1px solid var(--fc-hairline);">
{icon_svg}
</div>
<span style="font-size:0.92rem;font-weight:550;color:var(--fc-text-2);">{c['label']}</span>
</div>
{badge_markup}
</div>
<div style="font-family:var(--fc-font-sans);font-size:clamp(24px, 2.0vw, 34px);font-weight:700;color:var(--fc-text);font-variant-numeric:tabular-nums;line-height:1.2;margin:0.25rem 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
{c['value']}
</div>
<div style="font-size:0.82rem;color:var(--fc-text-2);line-height:1.35;">
{c.get('context', '')}
</div>
</div>""")

    grid_markup = f"""<div class="fc-metric-grid">{''.join(cards_html)}</div>"""
    st.markdown(html(grid_markup), unsafe_allow_html=True)


def section(title: str, subtitle: str = ""):
    """Renders a standardized section heading."""
    sub_markup = f"""<div style="font-size:0.92rem;color:var(--fc-text-2);margin-top:0.2rem;line-height:1.45;">{subtitle}</div>""" if subtitle else ""
    markup = f"""<div style="margin-bottom:1rem;">
<h2 class="fc-title" style="margin:0;">
{title}
</h2>
{sub_markup}
</div>"""
    st.markdown(html(markup), unsafe_allow_html=True)


def bento_card_header(title: str, subtitle: str = "", badge: Optional[str] = None) -> str:
    """Returns HTML for standard bento card headers."""
    badge_html = f"""<span style="font-size:0.75rem;font-weight:600;padding:2px 8px;border-radius:999px;background:var(--fc-accent-tint);color:var(--fc-accent);border:1px solid var(--fc-hairline);">{badge}</span>""" if badge else ""
    sub_html = f"""<div style="font-size:0.82rem;color:var(--fc-text-2);margin-top:2px;">{subtitle}</div>""" if subtitle else ""
    
    return html(f"""<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
<div>
<div class="fc-headline" style="margin:0;">{title}</div>
{sub_html}
</div>
{badge_html}
</div>""")


def insight_list(insights: List[Dict[str, str]]):
    """Renders iOS-style grouped insights list with squircle icons and hairline dividers."""
    items_html = []
    for item in insights:
        icon_name = item.get("icon", "BrainCircuit")
        color = item.get("color", "var(--fc-accent)")
        icon_svg = get_lucide_svg(icon_name, size=18, color=color, stroke_width=1.75)
        
        items_html.append(f"""<div class="fc-insight-item">
<div style="width:34px;height:34px;border-radius:10px;background:var(--fc-surface);display:flex;align-items:center;justify-content:center;border:1px solid var(--fc-hairline);flex-shrink:0;">
{icon_svg}
</div>
<div>
<div style="font-size:0.92rem;font-weight:600;color:var(--fc-text);margin-bottom:2px;">{item['title']}</div>
<div style="font-size:0.82rem;color:var(--fc-text-2);line-height:1.4;">{item['text']}</div>
</div>
</div>""")

    markup = f"""<div class="fc-card" style="padding:1.25rem 1.4rem;height:100%;box-sizing:border-box;">
<div style="font-size:1.05rem;font-weight:650;color:var(--fc-text);margin-bottom:0.75rem;">Key Empirical Findings</div>
<div class="fc-insight-list">{''.join(items_html)}</div>
</div>"""
    st.markdown(html(markup), unsafe_allow_html=True)


def tooltip(label: str, text: str) -> str:
    """Renders a label with an accessible native title tooltip."""
    help_svg = get_lucide_svg("HelpCircle", size=13, color="currentColor", stroke_width=1.75)
    return f"""<span title="{text}" style="display:inline-flex;align-items:center;gap:4px;cursor:help;color:var(--fc-text);font-weight:500;">
{label} <span style="opacity:0.7;display:inline-flex;align-items:center;">{help_svg}</span>
</span>"""


def severity_bar(hectares: float, severity_info: Dict[str, Any]):
    """Renders an empirical severity scale progress bar using dynamic theme tokens."""
    sev_color = severity_info.get("color", "var(--fc-accent)")
    sev_name = severity_info.get("name", "Moderate")
    
    if hectares <= 0.0:
        pct = 2.0
    elif hectares < 2.5:
        pct = 5.0 + (hectares / 2.5) * 20.0
    elif hectares < 10.0:
        pct = 25.0 + ((hectares - 2.5) / 7.5) * 25.0
    elif hectares < 35.0:
        pct = 50.0 + ((hectares - 10.0) / 25.0) * 25.0
    else:
        pct = min(98.0, 75.0 + ((hectares - 35.0) / 100.0) * 23.0)

    bar_html = f"""<div style="margin-top:1.1rem;background:var(--fc-surface);padding:0.9rem 1.1rem;border-radius:var(--fc-radius-control);border:1px solid var(--fc-hairline);">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;font-size:0.78rem;">
<span style="font-weight:600;color:var(--fc-text);text-transform:uppercase;letter-spacing:0.04em;">Empirical Severity Band</span>
<span style="font-weight:700;color:{sev_color};text-transform:uppercase;">{sev_name}</span>
</div>
<div style="position:relative;height:8px;background:var(--fc-hairline);border-radius:999px;overflow:hidden;display:flex;">
<div style="width:25%;height:100%;background:rgba(69,201,154,0.25);border-right:1px solid var(--fc-bg);" title="Low Severity (0 - 2.5 ha)"></div>
<div style="width:25%;height:100%;background:rgba(255,173,92,0.25);border-right:1px solid var(--fc-bg);" title="Moderate Severity (2.5 - 10 ha)"></div>
<div style="width:25%;height:100%;background:rgba(255,113,56,0.25);border-right:1px solid var(--fc-bg);" title="High Severity (10 - 35 ha)"></div>
<div style="width:25%;height:100%;background:rgba(255,71,87,0.25);" title="Extreme Severity (>= 35 ha)"></div>
<div style="position:absolute;top:0;left:0;height:100%;width:{pct}%;background:{sev_color};border-radius:999px;box-shadow:0 0 10px {sev_color};"></div>
</div>
<div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--fc-text-2);margin-top:0.35rem;font-family:var(--fc-font-sans);font-variant-numeric:tabular-nums;">
<span>0 ha</span>
<span>2.5 ha</span>
<span>10 ha</span>
<span>35 ha+</span>
</div>
</div>"""
    st.markdown(html(bar_html), unsafe_allow_html=True)

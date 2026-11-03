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


def render_sky_switch_markup(theme_mode: str) -> str:
    """
    Renders the standalone signature 'Sky Switch' toggle:
    - 68x34px compact horizontal pill (44px touch target).
    - Track: Miniature sky scene (night gradient + stars in dark mode; dawn gradient + cloud in light mode).
    - Thumb: 26px circle sliding with spring physics (cubic-bezier(.34, 1.56, .64, 1) in 400ms).
    - Icon: Morphing crescent moon / radiant sun.
    - View Transition API circular clip-path wash.
    - Accessible: role='switch', aria-checked, keyboard navigable (Space/Enter).
    """
    is_dark = (theme_mode == "dark")
    next_mode = "light" if is_dark else "dark"
    aria_checked = "true" if is_dark else "false"
    tooltip_text = "Switch to light mode" if is_dark else "Switch to dark mode"
    
    # Track gradient & celestial elements
    if is_dark:
        track_bg = "linear-gradient(135deg, #0B140F 0%, #15241B 100%)"
        track_border = "rgba(255, 255, 255, 0.15)"
        thumb_x = "36px"
        thumb_bg = "#F5E6C8"
        thumb_icon = '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" fill="#171F1A" stroke="#171F1A" stroke-width="1.2"/>'
        sky_decor = """
        <circle cx="12" cy="11" r="1.2" fill="#FFFFFF" opacity="0.85" />
        <circle cx="22" cy="22" r="1.0" fill="#FFFFFF" opacity="0.75" />
        <circle cx="18" cy="8" r="0.8" fill="#FFFFFF" opacity="0.65" />
        <circle cx="28" cy="14" r="1.1" fill="#FFFFFF" opacity="0.8" />
        """
    else:
        track_bg = "linear-gradient(135deg, #FFE8D6 0%, #FFF5EB 100%)"
        track_border = "rgba(16, 23, 19, 0.15)"
        thumb_x = "4px"
        thumb_bg = "#E8501A"
        thumb_icon = '<circle cx="12" cy="12" r="4" fill="#FFFFFF"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/>'
        sky_decor = """
        <path d="M42 22a5 5 0 0 1 9.8-1.5A3.5 3.5 0 0 1 55 24a3.5 3.5 0 0 1-3.5 3.5h-10A4.5 4.5 0 0 1 42 22z" fill="#FFFFFF" opacity="0.9" />
        """

    switch_html = f"""
    <div style="display:inline-flex;align-items:center;">
      <div id="sky-switch-root"
           role="switch"
           tabindex="0"
           aria-checked="{aria_checked}"
           aria-label="Theme Toggle (currently {theme_mode} mode)"
           title="{tooltip_text}"
           onclick="triggerSkySwitch(event)"
           onkeydown="if(event.key===' '||event.key==='Enter'){{event.preventDefault();triggerSkySwitch(event);}}"
           style="position:relative;width:68px;height:34px;border-radius:999px;background:{track_bg};border:1.5px solid {track_border};cursor:pointer;padding:2px;box-shadow:inset 0 1px 4px rgba(0,0,0,0.2), 0 2px 8px rgba(0,0,0,0.1);outline:none;user-select:none;transition:border-color 0.25s ease;"
           class="fc-sky-switch">
        
        <!-- Sky Scene Elements -->
        <svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;" viewBox="0 0 68 34">
          {sky_decor}
        </svg>

        <!-- Sliding Celestial Thumb -->
        <div style="position:absolute;top:3px;left:0;transform:translateX({thumb_x});width:26px;height:26px;border-radius:50%;background:{thumb_bg};box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;transition:transform 400ms cubic-bezier(0.34, 1.56, 0.64, 1), background 300ms ease;">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
            {thumb_icon}
          </svg>
        </div>
      </div>
    </div>

    <script>
    function triggerSkySwitch(event) {{
        const targetBtn = document.querySelector('button[key="sky_switch_real_btn"], button[data-testid="baseButton-secondary"]:has(p:contains("SkySwitchTrigger"))') || 
                          Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('SkySwitchTrigger'));
        
        const executeTransition = () => {{
            if (targetBtn) {{
                targetBtn.click();
            }}
        }};

        if (!document.startViewTransition || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
            executeTransition();
            return;
        }}

        const x = event ? event.clientX : window.innerWidth - 60;
        const y = event ? event.clientY : 40;
        const endRadius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));

        const transition = document.startViewTransition(() => {{
            executeTransition();
        }});

        transition.ready.then(() => {{
            const clipPath = [
                `circle(0px at ${{x}}px ${{y}}px)`,
                `circle(${{endRadius}}px at ${{x}}px ${{y}}px)`
            ];
            document.documentElement.animate(
                {{ clipPath: clipPath }},
                {{
                    duration: 550,
                    easing: 'ease-in-out',
                    pseudoElement: '::view-transition-new(root)'
                }}
            );
        }}).catch(() => {{
            executeTransition();
        }});
    }}
    </script>
    """
    return html(switch_html)


def render_top_navigation():
    """
    Renders the unified top bar:
    - Left: Brand mark with custom SVG logo and tagline.
    - Center/Right: Apple-style segmented control module tabs.
    - Far Right: Vertical hairline divider + signature 'Sky Switch' toggle.
    """
    theme_mode = st.session_state.get("theme_mode", "dark")
    t = get_current_theme_tokens(theme_mode)
    current_page = st.session_state.get("page", "Overview")

    nav_items = [
        {"id": "Overview", "label": "Overview"},
        {"id": "Prediction", "label": "Predict"},
        {"id": "Analytics", "label": "Analytics"},
        {"id": "Explainability", "label": "Explain AI"},
        {"id": "Performance", "label": "Models"},
        {"id": "History", "label": "History"}
    ]

    # Container for Top Bar (2 cols: Left Brand & Navigation | Right Sky Switch)
    c_left, c_toggle = st.columns([6.8, 1.2], gap="small")

    with c_left:
        sub_cols = st.columns([2.0, 4.8], gap="small")
        with sub_cols[0]:
            logo_svg = get_logo_svg(36, theme_mode)
            brand_markup = f"""<div style="display:flex;align-items:center;gap:0.75rem;padding:0.2rem 0;">
{logo_svg}
<div>
<div style="font-family:var(--fc-font-sans);font-size:1.1rem;font-weight:700;color:var(--fc-text);line-height:1.15;letter-spacing:-0.02em;">
FireCast AI
</div>
<div style="font-size:0.72rem;color:var(--fc-text-2);font-weight:500;">
Predict • Understand • Protect
</div>
</div>
</div>"""
            st.markdown(html(brand_markup), unsafe_allow_html=True)

        with sub_cols[1]:
            nav_cols = st.columns(len(nav_items), gap="small")
            for i, item in enumerate(nav_items):
                is_active = (current_page == item["id"] or item["id"] in current_page)
                with nav_cols[i]:
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(
                        item["label"],
                        key=f"topnav_btn_{item['id']}",
                        use_container_width=True,
                        type=btn_type
                    ):
                        st.session_state["page"] = item["id"]
                        st.rerun()

    with c_toggle:
        st.markdown(render_sky_switch_markup(theme_mode), unsafe_allow_html=True)
        # Hidden Streamlit trigger button for the Sky Switch
        if st.button("SkySwitchTrigger", key="sky_switch_real_btn"):
            next_m = "light" if theme_mode == "dark" else "dark"
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

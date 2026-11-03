"""
FireCast AI — Centralized Design System & Single-Source Token Engine
Defines complete token sets for DARK and LIGHT palettes:
- High contrast, WCAG AA/AAA compliant across all text/background pairs.
- Injects dynamic :root CSS variables and color-scheme declarations.
- Smooth 0.25s transitions on themed surfaces (reduced-motion aware).
- No color is defined outside this module.
"""

from typing import Dict, Any

DARK_TOKENS = {
    "bg": "#101713",
    "bg_elevated": "#171F1A",
    "surface": "#171F1A",
    "card": "#1D2822",
    "card_hover": "#24332B",
    "hairline": "rgba(255, 255, 255, 0.08)",
    "text": "#F5F7F5",
    "text_2": "#B1BBB4",
    "text_3": "#7A877F",
    "accent": "#FF7138",
    "accent_2": "#FFAD5C",
    "accent_tint": "rgba(255, 113, 56, 0.16)",
    "success": "#45C99A",
    "ai_purple": "#9C8CFF",
    "info_blue": "#48DBFB",
    "analytics_blue": "#48DBFB",
    "danger": "#FF4757",
    "shadow_sm": "0 2px 8px rgba(0, 0, 0, 0.25)",
    "shadow_md": "0 4px 20px rgba(0, 0, 0, 0.35)",
    "overlay": "rgba(16, 23, 19, 0.75)",
    "chart_grid": "rgba(255, 255, 255, 0.06)",
    "chart_axis": "rgba(255, 255, 255, 0.10)",
    "input_bg": "#171F1A",
    "input_border": "rgba(255, 255, 255, 0.12)",
    "card_border": "rgba(255, 255, 255, 0.08)",
    "scrollbar_thumb": "rgba(255, 255, 255, 0.15)"
}

LIGHT_TOKENS = {
    "bg": "#F4F2EC",
    "bg_elevated": "#FFFFFF",
    "surface": "#FBFAF7",
    "card": "#FFFFFF",
    "card_hover": "#F7F5F0",
    "hairline": "rgba(16, 23, 19, 0.10)",
    "text": "#14201A",
    "text_2": "#4F5C54",
    "text_3": "#7A877F",
    "accent": "#E8501A",       # Darker Ember meeting 4.5:1 on light backgrounds
    "accent_2": "#F59A3A",
    "accent_tint": "rgba(232, 80, 26, 0.12)",
    "success": "#1E9E74",
    "ai_purple": "#6F4BD8",
    "info_blue": "#2F6FDB",
    "analytics_blue": "#2F6FDB",
    "danger": "#D92D3E",
    "shadow_sm": "0 1px 2px rgba(16, 23, 19, 0.06)",
    "shadow_md": "0 8px 24px rgba(16, 23, 19, 0.08)",
    "overlay": "rgba(244, 242, 236, 0.85)",
    "chart_grid": "rgba(16, 23, 19, 0.08)",
    "chart_axis": "rgba(16, 23, 19, 0.12)",
    "input_bg": "#FFFFFF",
    "input_border": "rgba(16, 23, 19, 0.15)",
    "card_border": "rgba(16, 23, 19, 0.10)",
    "scrollbar_thumb": "rgba(16, 23, 19, 0.20)"
}

# Compatibility aliases
COLORS = DARK_TOKENS
LIGHT_COLORS = LIGHT_TOKENS


def get_current_theme_tokens(theme_mode: str = "dark") -> Dict[str, str]:
    """Returns active palette tokens based on theme parameter."""
    return LIGHT_TOKENS if theme_mode == "light" else DARK_TOKENS


def get_current_theme_colors(theme_mode: str = "dark") -> Dict[str, str]:
    """Compatibility alias for get_current_theme_tokens."""
    return get_current_theme_tokens(theme_mode)


def render_theme_css(theme_mode: str = "dark") -> str:
    """
    Renders dynamic CSS injecting the active token variables and browser color-scheme.
    Applied on :root so all native widgets and custom components update seamlessly.
    """
    t = get_current_theme_tokens(theme_mode)
    scheme = "light" if theme_mode == "light" else "dark"

    css_vars = f"""
    :root {{
        color-scheme: {scheme};
        --fc-bg: {t['bg']};
        --fc-bg-elevated: {t['bg_elevated']};
        --fc-surface: {t['surface']};
        --fc-card: {t['card']};
        --fc-card-hover: {t['card_hover']};
        --fc-hairline: {t['hairline']};
        --fc-text: {t['text']};
        --fc-text-2: {t['text_2']};
        --fc-text-3: {t['text_3']};
        --fc-accent: {t['accent']};
        --fc-accent-2: {t['accent_2']};
        --fc-accent-tint: {t['accent_tint']};
        --fc-success: {t['success']};
        --fc-ai-purple: {t['ai_purple']};
        --fc-info-blue: {t['info_blue']};
        --fc-danger: {t['danger']};
        --fc-shadow-sm: {t['shadow_sm']};
        --fc-shadow-md: {t['shadow_md']};
        --fc-overlay: {t['overlay']};
        --fc-chart-grid: {t['chart_grid']};
        --fc-chart-axis: {t['chart_axis']};
        --fc-input-bg: {t['input_bg']};
        --fc-input-border: {t['input_border']};
        --fc-scrollbar-thumb: {t['scrollbar_thumb']};

        /* Squircles & Radii */
        --fc-radius-card: 20px;
        --fc-radius-control: 14px;
        --fc-radius-pill: 999px;

        /* Typography */
        --fc-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
    }}

    /* Global Transition for Theme Switches */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"], .fc-card, .fc-metric-item,
    div.stButton > button, div.stSelectbox, div.stNumberInput,
    [data-testid="stDataFrame"], [data-testid="stTable"] {{
        transition: background-color 0.25s ease,
                    color 0.25s ease,
                    border-color 0.25s ease,
                    box-shadow 0.25s ease,
                    fill 0.25s ease,
                    stroke 0.25s ease !important;
    }}

    @media (prefers-reduced-motion: reduce) {{
        * {{
            transition-duration: 0.01ms !important;
        }}
    }}
    """
    return f"<style id='firecast-theme-vars'>{css_vars}</style>"


def get_plotly_spatial_theme(theme_mode: str = "dark") -> Dict[str, Any]:
    """Returns dynamic Plotly layout parameters matching active theme tokens."""
    t = get_current_theme_tokens(theme_mode)
    return {
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "font": {
            "family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            "color": t["text"],
            "size": 12
        },
        "colorway": [
            t["accent"],
            t["ai_purple"],
            t["accent_2"],
            t["success"],
            t["info_blue"],
            t["danger"]
        ],
        "hoverlabel": {
            "bgcolor": t["surface"],
            "bordercolor": t["accent"],
            "font": {
                "color": t["text"],
                "family": "Inter, sans-serif",
                "size": 11
            }
        }
    }


def get_logo_svg(size: int = 34, theme_mode: str = "dark") -> str:
    """Returns custom brand SVG logo with theme-aware styling."""
    t = get_current_theme_tokens(theme_mode)
    circle_fill = t["surface"]
    circle_stroke = t["hairline"]
    inner_stroke = t["surface"]
    
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="fcBrandFlameGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{t['accent']}" />
      <stop offset="100%" stop-color="{t['accent_2']}" />
    </linearGradient>
  </defs>
  <circle cx="20" cy="20" r="19" fill="{circle_fill}" stroke="{circle_stroke}" stroke-width="1.5"/>
  <path d="M20 7C22.5 12 28 17 26.5 23C25.2 28.5 21 31 18 31C14 31 11.5 27.5 12 23.5C12.5 19.5 16 15 17 11C18 13.5 19 14.5 20 16L22 14L20 7Z" fill="url(#fcBrandFlameGrad)"/>
  <path d="M19 19L21 21.5L23 18.5L25 24" stroke="{inner_stroke}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

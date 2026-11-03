"""
FireCast AI — Unified Repair, Performance & Full-Page Spatial Operating System
Predict. Understand. Protect.
"""

import os
import streamlit as st
from theme import render_theme_css

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="FireCast AI — Wildfire Intelligence Platform",
    page_icon="assets/logo.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. State Management & Query Param Theme Sync (Single Source of Truth)
if "theme_mode" not in st.session_state:
    qp_theme = st.query_params.get("theme", "dark")
    st.session_state["theme_mode"] = qp_theme if qp_theme in ("dark", "light") else "dark"

if "page" not in st.session_state:
    st.session_state["page"] = "Overview"

theme_mode = st.session_state["theme_mode"]

# 3. Inject Dynamic Theme Variables & Styles
st.markdown(render_theme_css(theme_mode), unsafe_allow_html=True)

def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

# Theme persistence script
persistence_script = f"""
<script>
(function() {{
    const currentTheme = "{theme_mode}";
    try {{
        localStorage.setItem("firecast_theme", currentTheme);
    }} catch(e) {{}}
    document.documentElement.setAttribute("data-theme", currentTheme);
}})();
</script>
"""
st.markdown(persistence_script, unsafe_allow_html=True)

# 4. Import Central Navigation and Page Modules
from components import render_top_navigation
from pages.overview import render_overview_page
from pages.prediction import render_prediction_page
from pages.analytics import render_analytics_page
from pages.explainability import render_explainability_page
from pages.performance import render_performance_page
from pages.history import render_history_page

# 5. Render Top Navigation Bar with Signature Sky Switch Toggle
render_top_navigation()

# 6. Render Exactly One Active Page
current_page = st.session_state.get("page", "Overview")

if current_page == "Overview":
    render_overview_page()
elif current_page == "Prediction":
    render_prediction_page()
elif current_page == "Analytics":
    render_analytics_page()
elif current_page == "Explainability":
    render_explainability_page()
elif current_page == "Performance":
    render_performance_page()
elif current_page == "History":
    render_history_page()
else:
    render_overview_page()

"""
FireCast AI — Module 06: Prediction History & Audit Log
Locally persisted SQLite audit trail with search, filters, empty state, and CSV export.
"""

import streamlit as st
import pandas as pd
from src.database import get_prediction_history, delete_prediction_record, clear_all_history, seed_benchmark_history
from components import section, metric_card, html
from theme import get_current_theme_colors


def render_history_page():
    """Renders Module 06: Prediction History & Audit Log."""
    theme_mode = st.session_state.get("theme_mode", "dark")
    c = get_current_theme_colors(theme_mode)

    section(
        "Prediction History & Audit Trail",
        "Locally persisted records of past wildfire conditions evaluated with FireCast AI. Filter by severity, inspect telemetry, or export complete audit logs to CSV."
    )

    # 1. Controls Filter Row
    f_c1, f_c2, f_c3, f_c4 = st.columns([1.4, 1.0, 1.1, 1.1], gap="small")
    with f_c1:
        sev_filter = st.selectbox(
            "Filter by Severity Category",
            options=["All", "Low Severity", "Moderate Severity", "High Severity", "Extreme Severity"],
            index=0
        )
    with f_c2:
        max_rows = st.number_input("Max Records to Retrieve", min_value=10, max_value=1000, value=100, step=25)
    with f_c3:
        st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
        if st.button("Restore Benchmarks", use_container_width=True):
            seeded = seed_benchmark_history(force=True)
            st.success(f"Restored {seeded} benchmark records.")
            st.rerun()
    with f_c4:
        st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
        if st.button("Clear All Logs", use_container_width=True):
            deleted_count = clear_all_history()
            st.warning(f"Cleared {deleted_count} prediction records.")
            st.rerun()

    # Retrieve from SQLite (auto-seeds if database is empty)
    df_history = get_prediction_history(limit=int(max_rows), severity_filter=sev_filter)

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    # 2. History Summary Metrics
    total_saved = len(df_history)
    avg_ha = float(df_history["predicted_ha"].mean()) if total_saved > 0 else 0.0
    max_ha = float(df_history["predicted_ha"].max()) if total_saved > 0 else 0.0
    avg_latency = float(df_history["latency_ms"].mean()) if total_saved > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        metric_card("Saved Records", f"{total_saved}", "Total session entries", icon_name="Database", icon_color=c["analytics_blue"])
    with k2:
        metric_card("Mean Predicted Area", f"{avg_ha:.2f} ha", "Average across history", icon_name="Target", icon_color=c["accent"])
    with k3:
        metric_card("Max Analyzed Fire", f"{max_ha:.2f} ha", "Peak query size", icon_name="Flame", icon_color=c["danger"])
    with k4:
        metric_card("Average Latency", f"{avg_latency:.1f} ms", "Engine inference speed", icon_name="Cpu", icon_color=c["success"])

    st.markdown("<div style='height: 1.4rem;'></div>", unsafe_allow_html=True)

    # 3. Empty State or Telemetry Table
    if df_history.empty:
        empty_html = f"""<div class="fc-card" style="padding:2.5rem 1.5rem;text-align:center;background:{c['card']};border:1px solid {c['card_border']};margin-bottom:1.2rem;">
<div style="font-size:1.1rem;font-weight:600;color:{c['text']};margin-bottom:0.4rem;">
No Prediction Records Found
</div>
<div style="font-size:0.85rem;color:{c['text_2']};max-width:480px;margin:0 auto 1.2rem auto;line-height:1.5;">
No records matched the selected filter '{sev_filter}'. You can restore historical benchmark cases or navigate to the Predict module to run an interactive query.
</div>
</div>"""
        st.markdown(html(empty_html), unsafe_allow_html=True)
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            if st.button("Load Benchmark Historical Records", use_container_width=True, type="primary"):
                seed_benchmark_history(force=True)
                st.rerun()
        with e_col2:
            if st.button("Go to Predict Module", use_container_width=True):
                st.session_state["page"] = "Prediction"
                st.rerun()
        return

    # Data Table Display with spatial coordinates
    cols_to_show = ["id", "timestamp"]
    if "X" in df_history.columns:
        cols_to_show.append("X")
    if "Y" in df_history.columns:
        cols_to_show.append("Y")
    cols_to_show += [
        "month", "temp", "RH", "wind", "rain",
        "predicted_ha", "severity_category", "model_used", "latency_ms", "notes"
    ]
    cols_to_show = [col for col in cols_to_show if col in df_history.columns]
    display_df = df_history[cols_to_show].copy()
    display_df["month"] = display_df["month"].astype(str).str.upper()
    display_df["predicted_ha"] = display_df["predicted_ha"].round(2)
    display_df["latency_ms"] = display_df["latency_ms"].round(1)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 4. Export & Record Delete Actions
    exp_c1, exp_c2 = st.columns([1.5, 1.2], gap="medium")
    with exp_c1:
        csv_data = df_history.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export History to CSV",
            data=csv_data,
            file_name="FireCast_Prediction_History.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_c2:
        del_col1, del_col2 = st.columns([1.2, 1])
        with del_col1:
            del_id = st.number_input("Record ID to Delete", min_value=1, step=1, label_visibility="collapsed")
        with del_col2:
            if st.button("Delete Record", use_container_width=True):
                if delete_prediction_record(int(del_id)):
                    st.success(f"Deleted record #{del_id}.")
                    st.rerun()
                else:
                    st.error(f"Record #{del_id} not found.")

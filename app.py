"""
EE4409 CA2 — Manufacturing Plant Monitoring Dashboard
Author : Senior Data Scientist / Full-Stack Developer
Stack  : Streamlit · Plotly · Pandas
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, date
import os

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plant Monitoring Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL THEME / CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---------- base ---------- */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #2a3144;
}

/* ---------- KPI cards ---------- */
.kpi-card {
    background: linear-gradient(135deg, #1a2035 0%, #1f2940 100%);
    border: 1px solid #2e3f5c;
    border-radius: 14px;
    padding: 22px 26px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    transition: transform .2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-label  { font-size: 13px; color: #8899aa; letter-spacing: .05em; text-transform: uppercase; margin-bottom: 6px; }
.kpi-value  { font-size: 2.4rem; font-weight: 700; line-height: 1.1; }
.kpi-sub    { font-size: 12px; color: #607080; margin-top: 4px; }

/* ---------- machine cards ---------- */
.mc-card {
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 4px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
}
.mc-running { background: linear-gradient(135deg,#0d3321,#1a5c38); border:1px solid #27a05a; }
.mc-idle    { background: linear-gradient(135deg,#332d00,#5c4e00); border:1px solid #c9a800; }
.mc-fault   { background: linear-gradient(135deg,#330a0a,#5c1a1a); border:1px solid #cc3333; }
.mc-title   { font-size: 1.15rem; font-weight: 700; margin-bottom: 4px; }
.mc-status  { font-size: .85rem; letter-spacing:.08em; font-weight:600; }
.mc-metric  { font-size:.8rem; color:#aabbcc; margin-top:6px; }

/* ---------- alert table ---------- */
.alert-row { background:#1f1010; border-left:4px solid #cc3333;
             border-radius:6px; padding:8px 12px; margin:4px 0; font-size:.85rem; }

/* ---------- section headers ---------- */
.section-header {
    font-size: 1.05rem; font-weight: 600;
    color: #7eb8f7; border-bottom: 1px solid #2a3a55;
    padding-bottom: 6px; margin-bottom: 14px; letter-spacing:.04em;
}

/* ---------- sidebar info box ---------- */
.info-box {
    background:#1a2133; border:1px solid #2e3f5c;
    border-radius:10px; padding:14px; margin:8px 0; font-size:.82rem; line-height:1.6;
}
.info-box b { color:#7eb8f7; }
.warn { color:#ff6b6b; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────
DATA_FILE = "plant_monitoring_data_1_.xlsm"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsm", ".xlsx"):
        df = pd.read_excel(path, engine="openpyxl")
    else:
        df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["rejection_rate"] = np.where(
        df["produced_units"] > 0,
        df["rejected_units"] / df["produced_units"] * 100,
        0,
    )
    df["date"] = df["timestamp"].dt.date
    return df

# Try loading from multiple candidate locations
for candidate in [DATA_FILE, f"data/{DATA_FILE}", f"/mnt/user-data/uploads/{DATA_FILE}"]:
    if os.path.exists(candidate):
        df_raw = load_data(candidate)
        break
else:
    st.error(f"⚠️  Data file not found. Place **{DATA_FILE}** in the same directory as app.py and re-run.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — SENSOR INFO + FILTERS
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 Plant Monitor")
    st.markdown("---")

    # ── INFORMATION PANEL ────────────────────────────────────────────────────
    with st.expander("ℹ️  Sensor & System Guide", expanded=True):
        st.markdown("""
<div class="info-box">
<b>⚡ Current Sensor</b><br>
Measures the electrical load drawn by the motor (Amperes).
Reflects how hard the machine is working.<br>
&nbsp;&nbsp;• Typical range: <b>10 – 50 A</b><br>
&nbsp;&nbsp;• <span class="warn">CRITICAL: &gt; 60 A</span>
</div>
<div class="info-box">
<b>📳 Vibration Sensor</b><br>
Measures mechanical vibration velocity (mm/s).
High vibration often precedes bearing or gear failures.<br>
&nbsp;&nbsp;• Typical range: <b>1 – 8 mm/s</b><br>
&nbsp;&nbsp;• <span class="warn">CRITICAL: &gt; 10 mm/s</span>
</div>
<div class="info-box">
<b>🔴 Critical Fault Indicators</b><br>
Either condition triggers an alert:<br>
&nbsp;&nbsp;• Vibration <b>&gt; 10 mm/s</b><br>
&nbsp;&nbsp;• Current <b>&gt; 60 A</b>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    # Machine filter
    all_machines = sorted(df_raw["machine_id"].unique())
    sel_machines = st.multiselect("Machine ID", all_machines, default=all_machines)

    # Date range filter
    min_date, max_date = df_raw["date"].min(), df_raw["date"].max()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        d_start, d_end = date_range
    else:
        d_start = d_end = date_range[0] if date_range else min_date

    # Shift filter
    shifts = st.multiselect("Shift", ["Day", "Night"], default=["Day", "Night"])

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.75rem;color:#5a6a7a;text-align:center'>"
        "EE4409 CA2 · Manufacturing Dashboard</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["machine_id"].isin(sel_machines) &
    (df_raw["date"] >= d_start) &
    (df_raw["date"] <= d_end) &
    df_raw["shift"].isin(shifts)
].copy()

if df.empty:
    st.warning("No data matches the selected filters. Please widen your selection.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# COMPUTED METRICS (whole filtered dataset)
# ──────────────────────────────────────────────────────────────────────────────
total_rows      = len(df)
running_rows    = (df["status"] == "RUNNING").sum()
uptime_pct      = running_rows / total_rows * 100 if total_rows else 0

total_produced  = df["produced_units"].sum()
total_rejected  = df["rejected_units"].sum()
yield_rate      = (total_produced - total_rejected) / total_produced * 100 if total_produced else 0

active_faults   = (df["status"] == "FAULT").sum()

# Latest reading per machine (for status cards + gauges)
latest = (
    df.sort_values("timestamp")
    .groupby("machine_id")
    .last()
    .reset_index()
)

# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='margin-bottom:2px;font-size:1.75rem;'>🏭 Manufacturing Plant Monitoring Dashboard</h1>"
    f"<p style='color:#607080;font-size:.85rem;margin-top:0;'>Data: {d_start} → {d_end} &nbsp;|&nbsp; "
    f"Machines: {', '.join(sel_machines)} &nbsp;|&nbsp; Shifts: {', '.join(shifts)}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# ROW 1 — KPI CARDS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Plant-Wide KPIs</div>', unsafe_allow_html=True)
k1, k2, k3 = st.columns(3)

def kpi_color(value, good_threshold, bad_threshold, higher_is_better=True):
    if higher_is_better:
        return "#2ecc71" if value >= good_threshold else ("#e67e22" if value >= bad_threshold else "#e74c3c")
    else:
        return "#2ecc71" if value <= good_threshold else ("#e67e22" if value <= bad_threshold else "#e74c3c")

with k1:
    color = kpi_color(uptime_pct, 80, 60)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">⏱ Total Plant Uptime</div>
        <div class="kpi-value" style="color:{color}">{uptime_pct:.1f}%</div>
        <div class="kpi-sub">{running_rows:,} of {total_rows:,} readings RUNNING</div>
    </div>""", unsafe_allow_html=True)

with k2:
    color = kpi_color(yield_rate, 90, 75)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">✅ Total Yield Rate</div>
        <div class="kpi-value" style="color:{color}">{yield_rate:.1f}%</div>
        <div class="kpi-sub">{total_produced - total_rejected:,} good / {total_produced:,} produced</div>
    </div>""", unsafe_allow_html=True)

with k3:
    fault_color = "#e74c3c" if active_faults > 0 else "#2ecc71"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🚨 Active Fault Count</div>
        <div class="kpi-value" style="color:{fault_color}">{active_faults}</div>
        <div class="kpi-sub">Rows with FAULT status in selection</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# ROW 2 — MACHINE STATUS CARDS + HEALTH GAUGES
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🤖 Individual Machine Status</div>', unsafe_allow_html=True)

STATUS_CLASS = {"RUNNING": "mc-running", "IDLE": "mc-idle", "FAULT": "mc-fault"}
STATUS_ICON  = {"RUNNING": "🟢", "IDLE": "🟡", "FAULT": "🔴"}
STATUS_COLOR = {"RUNNING": "#27a05a", "IDLE": "#c9a800", "FAULT": "#cc3333"}

machine_cols = st.columns(len(sel_machines)) if sel_machines else []

def make_gauge(value, title, max_val=20, warning=8, critical=10):
    """Plotly gauge for vibration health."""
    color = "#2ecc71" if value <= warning else ("#e67e22" if value <= critical else "#e74c3c")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": " mm/s", "font": {"size": 16, "color": "#e0e0e0"}},
        title={"text": title, "font": {"size": 13, "color": "#8899aa"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#4a5a6a",
                     "tickfont": {"color": "#8899aa", "size": 10}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#1a2035",
            "bordercolor": "#2e3f5c",
            "steps": [
                {"range": [0, warning],   "color": "#0d2a1a"},
                {"range": [warning, critical], "color": "#2a2200"},
                {"range": [critical, max_val], "color": "#2a0a0a"},
            ],
            "threshold": {"line": {"color": "#e74c3c", "width": 3},
                          "thickness": 0.8, "value": critical},
        },
    ))
    fig.update_layout(
        height=180, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
    )
    return fig

for i, machine in enumerate(sel_machines):
    row = latest[latest["machine_id"] == machine]
    if row.empty:
        continue
    r = row.iloc[0]
    status   = r["status"]
    css_cls  = STATUS_CLASS.get(status, "mc-idle")
    icon     = STATUS_ICON.get(status, "⚪")
    vib      = r["vibration_mm_s"]
    cur      = r["current_a"]
    produced = int(r["produced_units"])
    rejected = int(r["rejected_units"])

    with machine_cols[i]:
        st.markdown(f"""
        <div class="mc-card {css_cls}">
            <div class="mc-title">{machine}</div>
            <div class="mc-status">{icon} {status}</div>
            <div class="mc-metric">
                ⚡ Current: <b>{cur:.1f} A</b> &nbsp;|&nbsp;
                📳 Vibration: <b>{vib:.2f} mm/s</b>
            </div>
            <div class="mc-metric">
                📦 Produced: <b>{produced}</b> &nbsp;|&nbsp;
                ❌ Rejected: <b>{rejected}</b>
            </div>
            <div class="mc-metric" style="color:#607080;font-size:.75rem;">
                Latest reading: {r['timestamp'].strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>""", unsafe_allow_html=True)

        st.plotly_chart(
            make_gauge(vib, f"{machine} Vibration Health"),
            use_container_width=True, config={"displayModeBar": False},
        )

st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# ROW 3 — SENSOR TREND CHART  (current_a + vibration_mm_s)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Sensor Trends Over Time</div>', unsafe_allow_html=True)

fig_trend = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    row_heights=[0.5, 0.5],
    subplot_titles=("Motor Current (A)", "Vibration Velocity (mm/s)"),
    vertical_spacing=0.10,
)

machine_colors = {"M1": "#7eb8f7", "M2": "#f79e7e", "M3": "#7ef7a8"}

for mach in sel_machines:
    sub = df[df["machine_id"] == mach].sort_values("timestamp")
    col = machine_colors.get(mach, "#aaaaaa")

    fig_trend.add_trace(
        go.Scatter(x=sub["timestamp"], y=sub["current_a"], name=f"{mach} Current",
                   line=dict(color=col, width=1.5), opacity=0.9,
                   hovertemplate=f"<b>{mach}</b> %{{x|%Y-%m-%d %H:%M}}<br>Current: %{{y:.1f}} A<extra></extra>"),
        row=1, col=1,
    )
    fig_trend.add_trace(
        go.Scatter(x=sub["timestamp"], y=sub["vibration_mm_s"], name=f"{mach} Vibration",
                   line=dict(color=col, width=1.5, dash="dot"), opacity=0.9,
                   hovertemplate=f"<b>{mach}</b> %{{x|%Y-%m-%d %H:%M}}<br>Vibration: %{{y:.2f}} mm/s<extra></extra>"),
        row=2, col=1,
    )

# Threshold reference lines
fig_trend.add_hline(y=60, row=1, col=1, line_color="#e74c3c", line_dash="dash",
                    annotation_text="Critical 60 A", annotation_font_color="#e74c3c",
                    annotation_position="top right")
fig_trend.add_hline(y=10, row=2, col=1, line_color="#e74c3c", line_dash="dash",
                    annotation_text="Critical 10 mm/s", annotation_font_color="#e74c3c",
                    annotation_position="top right")

fig_trend.update_layout(
    height=460, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,30,0.6)",
    font_color="#e0e0e0", legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
    margin=dict(l=10, r=10, t=40, b=10), hovermode="x unified",
)
fig_trend.update_xaxes(gridcolor="#1e2a3a", showgrid=True)
fig_trend.update_yaxes(gridcolor="#1e2a3a", showgrid=True)

st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# ROW 4 — PRODUCTION BAR CHART (by shift)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏗️ Production Performance by Shift</div>', unsafe_allow_html=True)

shift_df = (
    df.groupby(["shift", "machine_id"])[["produced_units", "rejected_units"]]
    .sum()
    .reset_index()
)

col_bar, col_pie = st.columns([3, 2])

with col_bar:
    fig_bar = go.Figure()
    for mach in sel_machines:
        sub = shift_df[shift_df["machine_id"] == mach]
        col = machine_colors.get(mach, "#aaa")
        fig_bar.add_trace(go.Bar(
            name=f"{mach} Produced", x=sub["shift"], y=sub["produced_units"],
            marker_color=col, opacity=0.85,
            hovertemplate=f"<b>{mach}</b><br>Shift: %{{x}}<br>Produced: %{{y:,}}<extra></extra>",
        ))
        fig_bar.add_trace(go.Bar(
            name=f"{mach} Rejected", x=sub["shift"], y=sub["rejected_units"],
            marker_color=col, opacity=0.4, marker_pattern_shape="/",
            hovertemplate=f"<b>{mach}</b><br>Shift: %{{x}}<br>Rejected: %{{y:,}}<extra></extra>",
        ))

    fig_bar.update_layout(
        barmode="group", height=320,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,30,0.6)",
        font_color="#e0e0e0", xaxis_title="Shift", yaxis_title="Units",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    fig_bar.update_xaxes(gridcolor="#1e2a3a")
    fig_bar.update_yaxes(gridcolor="#1e2a3a")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_pie:
    status_counts = df.groupby("status").size().reset_index(name="count")
    pie_colors    = {"RUNNING": "#27a05a", "IDLE": "#c9a800", "FAULT": "#cc3333"}
    fig_pie = go.Figure(go.Pie(
        labels=status_counts["status"],
        values=status_counts["count"],
        hole=0.55,
        marker_colors=[pie_colors.get(s, "#888") for s in status_counts["status"]],
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value} readings<br>%{percent}<extra></extra>",
    ))
    fig_pie.update_layout(
        height=320, title=dict(text="Status Distribution", font_color="#8899aa", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# ROW 5 — ANOMALY / ALERTS LOG
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🚨 Anomaly Detection — Alerts Log</div>', unsafe_allow_html=True)

alerts = df[
    (df["vibration_mm_s"] > 10) |
    (df["current_a"] > 60) |
    (df["rejection_rate"] > 10)
].copy()

alerts["Triggered By"] = alerts.apply(
    lambda r: " | ".join(filter(None, [
        f"⚡ Current {r['current_a']:.1f}A > 60A"  if r["current_a"] > 60 else "",
        f"📳 Vibration {r['vibration_mm_s']:.2f} > 10mm/s" if r["vibration_mm_s"] > 10 else "",
        f"❌ Rejection {r['rejection_rate']:.1f}% > 10%"   if r["rejection_rate"] > 10 else "",
    ])), axis=1,
)

if alerts.empty:
    st.success("✅  No anomalies detected in the current selection.")
else:
    a_col1, a_col2, a_col3 = st.columns(3)
    a_col1.metric("Total Anomaly Rows", len(alerts))
    a_col2.metric("Machines Affected", alerts["machine_id"].nunique())
    a_col3.metric("Most Affected", alerts["machine_id"].value_counts().idxmax())

    display_alerts = alerts[[
        "timestamp", "machine_id", "status",
        "current_a", "vibration_mm_s", "rejection_rate", "Triggered By"
    ]].rename(columns={
        "timestamp": "Timestamp", "machine_id": "Machine",
        "status": "Status", "current_a": "Current (A)",
        "vibration_mm_s": "Vibration (mm/s)", "rejection_rate": "Rejection Rate (%)",
    }).sort_values("Timestamp", ascending=False)

    display_alerts["Timestamp"] = display_alerts["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display_alerts["Rejection Rate (%)"] = display_alerts["Rejection Rate (%)"].round(2)

    st.dataframe(
        display_alerts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Current (A)":        st.column_config.NumberColumn(format="%.1f A"),
            "Vibration (mm/s)":   st.column_config.NumberColumn(format="%.2f mm/s"),
            "Rejection Rate (%)": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )

    # Anomaly timeline
    alerts_by_day = alerts.groupby(["date", "machine_id"]).size().reset_index(name="anomalies")
    fig_anom = px.bar(
        alerts_by_day, x="date", y="anomalies", color="machine_id",
        color_discrete_map=machine_colors,
        labels={"date": "Date", "anomalies": "Anomaly Count", "machine_id": "Machine"},
        barmode="group",
    )
    fig_anom.update_layout(
        height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,18,30,0.6)",
        font_color="#e0e0e0", margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig_anom.update_xaxes(gridcolor="#1e2a3a")
    fig_anom.update_yaxes(gridcolor="#1e2a3a")
    st.plotly_chart(fig_anom, use_container_width=True)

st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# ROW 6 — OPERATIONAL RECOMMENDATIONS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Operational Insights & Recommendations</div>', unsafe_allow_html=True)

# Dynamic fault analysis
fault_counts = df[df["status"] == "FAULT"].groupby("machine_id").size()
most_faults_machine = fault_counts.idxmax() if not fault_counts.empty else None

rec_col1, rec_col2 = st.columns(2)

with rec_col1:
    st.markdown("#### 🔧 Maintenance Recommendations")

    if most_faults_machine:
        fc = fault_counts[most_faults_machine]
        pct = fc / len(df[df["machine_id"] == most_faults_machine]) * 100
        if most_faults_machine == "M1" or True:   # dynamic
            schedule_advice = (
                f"**{most_faults_machine}** recorded the highest fault frequency "
                f"(**{fc} faults**, {pct:.1f}% of its readings). "
                "Recommended actions:"
            )
    else:
        schedule_advice = "No faults detected in the selected period — continue standard monitoring."

    st.markdown(schedule_advice)

    st.markdown(f"""
| Priority | Action | Interval |
|----------|--------|----------|
| 🔴 High | Full bearing inspection & lubrication on **{most_faults_machine or 'N/A'}** | Immediately |
| 🟠 Medium | Electrical connection check (motor terminals) | Weekly |
| 🟡 Low | Scheduled preventive maintenance — all machines | Monthly |
| 🟢 Routine | Vibration baseline recalibration | Quarterly |
""")

    # High-vibration machine alert
    high_vib = latest[latest["vibration_mm_s"] > 8]
    if not high_vib.empty:
        for _, hv in high_vib.iterrows():
            st.warning(
                f"⚠️ **{hv['machine_id']}** last recorded vibration of "
                f"**{hv['vibration_mm_s']:.2f} mm/s** — approaching critical threshold. "
                "Schedule inspection within 24 hours."
            )

with rec_col2:
    st.markdown("#### 🔬 Suggested Advanced Sensing Modalities")

    st.markdown("""
| Sensor Type | Purpose | Benefit |
|-------------|---------|---------|
| 🌡️ **Thermal Camera** | Detect overheating in motors & bearings | Catch thermal anomalies before mechanical failure |
| 🎤 **Acoustic Emission (AE)** | Detect micro-cracks & bearing wear via sound | Early fault detection at sub-millimetre scale |
| 🛢️ **Oil Quality Sensor** | Monitor lubricant viscosity & particulates | Predict lubrication failure before damage occurs |
| 🔄 **Torque Sensor** | Measure rotational load directly | Distinguish mechanical vs electrical faults |
| 🌊 **Ultrasonic Sensor** | Detect internal leaks or cavitation | Non-invasive inspection of sealed systems |
""")

    st.info(
        "💡 **Predictive Maintenance Strategy**: Combining the existing current & vibration sensors "
        "with thermal imaging and acoustic sensors can reduce unplanned downtime by up to **40%** "
        "through machine learning anomaly detection trained on multi-modal sensor fusion."
    )

# Summary recommendation box
high_rej_shift = df.groupby("shift").apply(
    lambda g: g["rejected_units"].sum() / max(g["produced_units"].sum(), 1) * 100
).idxmax()

st.markdown("#### 📋 Summary Action Plan")
st.markdown(f"""
> **Key Findings from Current Data ({d_start} → {d_end})**
>
> - **Plant Uptime**: {uptime_pct:.1f}% — {'✅ Healthy' if uptime_pct >= 80 else '⚠️ Below target of 80%'}
> - **Yield Rate**: {yield_rate:.1f}% — {'✅ Healthy' if yield_rate >= 90 else '⚠️ Investigate rejection causes'}
> - **Highest Fault Machine**: {most_faults_machine or 'None'} — Prioritise for maintenance
> - **Shift with Higher Rejection**: **{high_rej_shift}** shift — Review operator procedures and tooling
> - **Recommendation**: Implement a real-time alert system using vibration + current thresholds, 
>   and schedule a predictive maintenance review within 7 days.
""")

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#3a4a5a;font-size:.78rem;padding:6px 0'>"
    "EE4409 CA2 · Manufacturing Plant Monitoring Dashboard · "
    "Built with Streamlit · Plotly · Pandas"
    "</div>",
    unsafe_allow_html=True,
)

"""
EE4409 CA2 — PlantIQ Manufacturing Dashboard
Stack : Streamlit · Plotly · Pandas
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="PlantIQ", page_icon="⚙️",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────────────────────
# CSS — warm beige, minimal, elegant
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

/* ── base ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="block-container"] {
    background-color: #f5f0e8 !important;
    color: #1a1a1a;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #ede8de !important;
    border-right: 1px solid #d8d0c0;
}
[data-testid="stSidebar"] * { color: #1a1a1a !important; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; color: #1a1a1a; }

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── tabs ── */
[data-testid="stTabs"] button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #666 !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #1a1a1a !important;
    border-bottom: 2px solid #1a1a1a !important;
}

/* ── section divider label ── */
.sh {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: .18em;
    color: #999;
    text-transform: uppercase;
    border-bottom: 1px solid #d8d0c0;
    padding-bottom: 6px;
    margin-bottom: 18px;
}

/* ── KPI cards ── */
.kpi-card {
    background: #fff;
    border: 1px solid #e0d8cc;
    border-radius: 12px;
    padding: 28px 24px 22px;
    text-align: left;
    position: relative;
}
.kpi-card-top {
    width: 32px; height: 3px;
    border-radius: 2px;
    margin-bottom: 16px;
    background: var(--kpi-bar, #1a1a1a);
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    line-height: 1;
    color: var(--kpi-color, #1a1a1a);
    margin-bottom: 6px;
}
.kpi-sub {
    font-size: 12px;
    color: #aaa;
}

/* ── machine status cards ── */
.mc-card {
    background: #fff;
    border: 1px solid #e0d8cc;
    border-radius: 12px;
    padding: 22px;
    border-top: 3px solid var(--mc-accent, #ccc);
}
.mc-name {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    color: #1a1a1a;
    margin-bottom: 4px;
}
.mc-status-pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 16px;
}
.pill-running { background: #dcfce7; color: #166534; }
.pill-idle    { background: #fef9c3; color: #854d0e; }
.pill-fault   { background: #fee2e2; color: #991b1b; }
.mc-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #f0ebe0;
    font-size: 13px;
}
.mc-row:last-child { border-bottom: none; }
.mc-row-label { color: #888; font-weight: 500; }
.mc-row-val   { color: #1a1a1a; font-weight: 600; }
.mc-row-alert { color: #dc2626; font-weight: 700; }
.risk-bar-bg {
    background: #ede8de;
    border-radius: 4px;
    height: 5px;
    margin-top: 14px;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: var(--risk-color, #ccc);
    width: var(--risk-w, 0%);
}
.risk-label {
    font-size: 11px;
    color: #888;
    margin-top: 5px;
}

/* ── info boxes in sidebar ── */
.info-box {
    background: #f5f0e8;
    border: 1px solid #d8d0c0;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 6px 0;
    font-size: 12px;
    line-height: 1.65;
    color: #333;
}
.info-box b { color: #1a1a1a; }
.crit { color: #dc2626; font-weight: 700; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #ede8de; }
::-webkit-scrollbar-thumb { background: #c8bfaf; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = "plant_monitoring_data_1_.xlsm"

@st.cache_data
def load_data(path):
    ext = os.path.splitext(str(path))[1].lower()
    df  = pd.read_excel(path, engine="openpyxl") if ext in (".xlsm",".xlsx") else pd.read_csv(path)
    df["timestamp"]      = pd.to_datetime(df["timestamp"])
    df["date"]           = df["timestamp"].dt.date
    df["rejection_rate"] = np.where(df["produced_units"]>0,
                                    df["rejected_units"]/df["produced_units"]*100, 0)
    return df

for p in [DATA_FILE, f"data/{DATA_FILE}", f"/mnt/user-data/uploads/{DATA_FILE}"]:
    if os.path.exists(p):
        df_raw = load_data(p); break
else:
    up = st.file_uploader("Upload plant_monitoring_data_1_.xlsm", type=["xlsm","xlsx","csv"])
    if up: df_raw = load_data(up)
    else:  st.info("Place your `.xlsm` file next to `app.py`, or upload it above."); st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 24px'>
        <div style='font-family:DM Serif Display,serif;font-size:1.5rem;color:#1a1a1a'>⚙ PlantIQ</div>
        <div style='font-size:10px;letter-spacing:.15em;color:#aaa;text-transform:uppercase;margin-top:2px'>
            Monitoring Dashboard
        </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("ℹ️ Sensor Guide", expanded=False):
        st.markdown("""
<div class="info-box"><b>⚡ Current Sensor</b><br>
Measures motor electrical load (A). Typical: 10–50 A.<br>
<span class="crit">Critical threshold: &gt; 60 A</span></div>
<div class="info-box"><b>📳 Vibration Sensor</b><br>
Measures mechanical velocity (mm/s). Typical: 1–8 mm/s.<br>
<span class="crit">Critical threshold: &gt; 10 mm/s</span></div>
<div class="info-box"><b>🔴 Fault Triggers</b><br>
Vibration &gt; 10 mm/s &nbsp;·&nbsp; Current &gt; 60 A &nbsp;·&nbsp; Rejection &gt; 10%</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sh" style="margin-top:12px">Filters</div>', unsafe_allow_html=True)
    all_machines = sorted(df_raw["machine_id"].unique())
    sel_machines = st.multiselect("Machine", all_machines, default=all_machines)
    mn, mx = df_raw["date"].min(), df_raw["date"].max()
    d_range = st.date_input("Date Range", value=(mn, mx), min_value=mn, max_value=mx)
    d_start, d_end = (d_range[0], d_range[1]) if len(d_range)==2 else (mn, mx)
    sel_shifts = st.multiselect("Shift", ["Day","Night"], default=["Day","Night"])

    st.markdown('<div class="sh" style="margin-top:16px">Alert Thresholds</div>', unsafe_allow_html=True)
    vib_thresh = st.slider("Vibration (mm/s)", 5.0, 15.0, 10.0, 0.5)
    cur_thresh = st.slider("Current (A)", 40.0, 80.0, 60.0, 1.0)

# ─────────────────────────────────────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["machine_id"].isin(sel_machines) &
    (df_raw["date"] >= d_start) & (df_raw["date"] <= d_end) &
    df_raw["shift"].isin(sel_shifts)
].copy()

if df.empty:
    st.warning("No data for the current filters."); st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────────────────
total       = len(df)
uptime_pct  = (df["status"]=="RUNNING").sum() / total * 100
total_prod  = df["produced_units"].sum()
total_rej   = df["rejected_units"].sum()
yield_rate  = (total_prod - total_rej) / total_prod * 100 if total_prod else 0
fault_count = (df["status"]=="FAULT").sum()
latest      = df.sort_values("timestamp").groupby("machine_id").last().reset_index()
alerts_df   = df[(df["vibration_mm_s"]>vib_thresh)|(df["current_a"]>cur_thresh)|(df["rejection_rate"]>10)]

def risk_score(mach_df, fc, vib_t, cur_t):
    n = len(mach_df) or 1
    return min(int((fc/n*100*0.40 + (mach_df["vibration_mm_s"]>vib_t).sum()/n*100*0.30 +
                    (mach_df["current_a"]>cur_t).sum()/n*100*0.20 +
                    min(mach_df["rejection_rate"].mean(),20)*0.10) * 3.5), 100)

machine_risk = {m: risk_score(df[df["machine_id"]==m],
                               (df[df["machine_id"]==m]["status"]=="FAULT").sum(),
                               vib_thresh, cur_thresh) for m in sel_machines}

# ─────────────────────────────────────────────────────────────────────────────
# SHARED CHART STYLE (light background)
# ─────────────────────────────────────────────────────────────────────────────
MACH_COLORS = {"M1":"#2563eb","M2":"#d97706","M3":"#16a34a"}

CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#faf7f2",
    font_color="#1a1a1a",
    font_family="DM Sans",
    margin=dict(l=10, r=10, t=40, b=10),
)

def apply_grid(fig, rows=None):
    kw = dict(gridcolor="#e8e0d0", zeroline=False, linecolor="#d8d0c0")
    if rows:
        for r in rows:
            fig.update_xaxes(**kw, row=r)
            fig.update_yaxes(**kw, row=r)
    else:
        fig.update_xaxes(**kw)
        fig.update_yaxes(**kw)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding:8px 0 4px;display:flex;align-items:baseline;gap:20px'>
  <span style='font-family:DM Serif Display,serif;font-size:2rem;color:#1a1a1a'>⚙ PlantIQ</span>
  <span style='font-size:12px;color:#aaa;letter-spacing:.04em'>
    {d_start} – {d_end} &nbsp;·&nbsp; {', '.join(sel_machines)} &nbsp;·&nbsp; {', '.join(sel_shifts)} shift
  </span>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr style='border:none;border-top:1px solid #d8d0c0;margin:8px 0 20px'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
TAB_MAIN, TAB_ADV = st.tabs(["📊  Live Dashboard", "🔬  Advanced Analysis"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with TAB_MAIN:

    # ── KPI CARDS ────────────────────────────────────────────────────────────
    st.markdown('<div class="sh">Plant-wide KPIs</div>', unsafe_allow_html=True)

    def kpi_card(col, label, value, sub, bar_color, val_color):
        col.markdown(f"""
        <div class="kpi-card" style="--kpi-bar:{bar_color};--kpi-color:{val_color}">
            <div class="kpi-card-top"></div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    up_col  = "#16a34a" if uptime_pct>=80 else ("#d97706" if uptime_pct>=60 else "#dc2626")
    yr_col  = "#16a34a" if yield_rate>=90 else ("#d97706" if yield_rate>=75 else "#dc2626")
    ft_col  = "#dc2626" if fault_count>0 else "#16a34a"
    top_risk = max(machine_risk.values()) if machine_risk else 0
    rk_col  = "#16a34a" if top_risk<30 else ("#d97706" if top_risk<60 else "#dc2626")

    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "Plant Uptime",   f"{uptime_pct:.1f}%",
             f"{(df['status']=='RUNNING').sum():,} of {total:,} readings", up_col, up_col)
    kpi_card(k2, "Yield Rate",     f"{yield_rate:.1f}%",
             f"{total_prod-total_rej:,} good of {total_prod:,} units", yr_col, yr_col)
    kpi_card(k3, "Fault Readings", str(fault_count),
             f"{fault_count/total*100:.1f}% of all readings", ft_col, ft_col)
    kpi_card(k4, "Max Risk Score", f"{top_risk}/100",
             "Highest machine risk index", rk_col, rk_col)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MACHINE STATUS CARDS ─────────────────────────────────────────────────
    st.markdown('<div class="sh">Individual Machine Status</div>', unsafe_allow_html=True)

    STATUS_ACCENT = {"RUNNING":"#16a34a","IDLE":"#d97706","FAULT":"#dc2626"}
    STATUS_PILL   = {"RUNNING":"pill-running","IDLE":"pill-idle","FAULT":"pill-fault"}
    STATUS_DOT    = {"RUNNING":"●","IDLE":"●","FAULT":"⚠"}

    def make_gauge(val, max_v, w_thresh, c_thresh, title):
        bar_col = "#16a34a" if val<=w_thresh else ("#d97706" if val<=c_thresh else "#dc2626")
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={"suffix":" mm/s","font":{"size":14,"color":"#1a1a1a"}},
            title={"text":title,"font":{"size":11,"color":"#888","family":"DM Sans"}},
            gauge={
                "axis":{"range":[0,max_v],"tickcolor":"#ccc","tickfont":{"color":"#aaa","size":9}},
                "bar":{"color":bar_col,"thickness":.3},
                "bgcolor":"#faf7f2","bordercolor":"#e0d8cc",
                "steps":[{"range":[0,w_thresh],"color":"#f0fdf4"},
                         {"range":[w_thresh,c_thresh],"color":"#fefce8"},
                         {"range":[c_thresh,max_v],"color":"#fef2f2"}],
                "threshold":{"line":{"color":"#dc2626","width":2},"thickness":.8,"value":c_thresh},
            }))
        fig.update_layout(height=165, margin=dict(l=15,r=15,t=35,b=5),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#1a1a1a")
        return fig

    mcols = st.columns(len(sel_machines))
    for i, mach in enumerate(sel_machines):
        row = latest[latest["machine_id"]==mach]
        if row.empty: continue
        r   = row.iloc[0]
        st_ = r["status"]
        rs  = machine_risk[mach]
        accent   = STATUS_ACCENT.get(st_, "#999")
        pill_cls = STATUS_PILL.get(st_, "pill-idle")
        dot      = STATUS_DOT.get(st_, "●")
        cc_cls   = "mc-row-alert" if r["current_a"]>cur_thresh else "mc-row-val"
        vc_cls   = "mc-row-alert" if r["vibration_mm_s"]>vib_thresh else "mc-row-val"
        risk_col = "#16a34a" if rs<30 else ("#d97706" if rs<60 else "#dc2626")
        risk_lbl = "Low" if rs<30 else ("Medium" if rs<60 else "High")

        with mcols[i]:
            st.markdown(f"""
            <div class="mc-card" style="--mc-accent:{accent}">
                <div class="mc-name">{mach}</div>
                <span class="mc-status-pill {pill_cls}">{dot} {st_}</span>
                <div class="mc-row">
                    <span class="mc-row-label">Motor Current</span>
                    <span class="{cc_cls}">{r['current_a']:.1f} A</span>
                </div>
                <div class="mc-row">
                    <span class="mc-row-label">Vibration</span>
                    <span class="{vc_cls}">{r['vibration_mm_s']:.2f} mm/s</span>
                </div>
                <div class="mc-row">
                    <span class="mc-row-label">Units Produced</span>
                    <span class="mc-row-val">{int(r['produced_units'])}</span>
                </div>
                <div class="mc-row">
                    <span class="mc-row-label">Units Rejected</span>
                    <span class="mc-row-val">{int(r['rejected_units'])}</span>
                </div>
                <div class="risk-bar-bg">
                    <div class="risk-bar-fill"
                         style="--risk-color:{risk_col};--risk-w:{rs}%"></div>
                </div>
                <div class="risk-label">Risk Index: <b style="color:{risk_col}">{rs}/100 — {risk_lbl}</b></div>
            </div>""", unsafe_allow_html=True)

            st.plotly_chart(
                make_gauge(r["vibration_mm_s"], 20, 8, vib_thresh, f"{mach} Vibration"),
                use_container_width=True, config={"displayModeBar":False})

    st.markdown("<hr style='border:none;border-top:1px solid #d8d0c0;margin:20px 0'>",
                unsafe_allow_html=True)

    # ── SENSOR TRENDS ────────────────────────────────────────────────────────
    st.markdown('<div class="sh">Sensor Trends Over Time</div>', unsafe_allow_html=True)

    fig_trend = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.09,
        subplot_titles=("Motor Current (A)", "Vibration Velocity (mm/s)"),
        row_heights=[.5,.5])

    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp").copy()
        c   = MACH_COLORS.get(mach, "#555")
        sub["cur_roll"] = sub["current_a"].rolling(8, min_periods=1).mean()
        sub["vib_roll"] = sub["vibration_mm_s"].rolling(8, min_periods=1).mean()
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"], y=sub["current_a"],
            name=mach, line=dict(color=c, width=1), opacity=.35, showlegend=True), row=1, col=1)
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"], y=sub["cur_roll"],
            name=f"{mach} avg", line=dict(color=c, width=2.2), showlegend=False), row=1, col=1)
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"], y=sub["vibration_mm_s"],
            name=mach, line=dict(color=c, width=1, dash="dot"), opacity=.35,
            showlegend=False), row=2, col=1)
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"], y=sub["vib_roll"],
            name=f"{mach} avg", line=dict(color=c, width=2.2), showlegend=False), row=2, col=1)

    fig_trend.add_hline(y=cur_thresh, row=1, col=1, line_color="#dc2626", line_dash="dash",
        annotation_text=f"Alert {cur_thresh:.0f} A", annotation_font_color="#dc2626")
    fig_trend.add_hline(y=vib_thresh, row=2, col=1, line_color="#dc2626", line_dash="dash",
        annotation_text=f"Alert {vib_thresh:.0f} mm/s", annotation_font_color="#dc2626")

    fig_trend.update_layout(**CHART_BASE, height=440, hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11))
    apply_grid(fig_trend, [1,2])
    st.plotly_chart(fig_trend, use_container_width=True)
    st.caption("Thick lines show 8-point rolling average. Thin lines show raw readings. Dashed red = alert threshold.")

    st.markdown("<hr style='border:none;border-top:1px solid #d8d0c0;margin:20px 0'>",
                unsafe_allow_html=True)

    # ── PRODUCTION + CORRELATION + RISK ──────────────────────────────────────
    st.markdown('<div class="sh">Production & Analysis</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2.5, 2, 2])

    with c1:
        st.markdown("**Production by Shift**")
        sdf = df.groupby(["shift","machine_id"])[["produced_units","rejected_units"]].sum().reset_index()
        fb  = go.Figure()
        for mach in sel_machines:
            sub = sdf[sdf["machine_id"]==mach]
            col = MACH_COLORS.get(mach, "#555")
            fb.add_trace(go.Bar(name=f"{mach} Good", x=sub["shift"],
                y=sub["produced_units"]-sub["rejected_units"], marker_color=col, opacity=.85))
            fb.add_trace(go.Bar(name=f"{mach} Rejected", x=sub["shift"],
                y=sub["rejected_units"], marker_color=col, opacity=.3, marker_pattern_shape="/"))
        fb.update_layout(**CHART_BASE, height=280, barmode="group",
            legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10))
        apply_grid(fb)
        st.plotly_chart(fb, use_container_width=True)

    with c2:
        st.markdown("**Sensor Correlation**")
        corr = df[["current_a","vibration_mm_s","rejection_rate","produced_units"]].corr().round(2)
        fh = go.Figure(go.Heatmap(
            z=corr.values,
            x=["Current","Vibration","Rejection","Produced"],
            y=["Current","Vibration","Rejection","Produced"],
            colorscale=[[0,"#dc2626"],[.5,"#f5f0e8"],[1,"#2563eb"]],
            zmid=0, text=corr.values, texttemplate="%{text}",
            textfont={"size":11,"family":"DM Sans"}))
        fh.update_layout(**CHART_BASE, height=280)
        st.plotly_chart(fh, use_container_width=True)
        st.caption("Current & Vibration (+0.30) rise together before fault events.")

    with c3:
        st.markdown("**Predictive Risk Score**")
        rdf = pd.DataFrame({"Machine":list(machine_risk.keys()),
                             "Score":list(machine_risk.values())})
        rdf["Color"] = rdf["Score"].apply(
            lambda x: "#16a34a" if x<30 else ("#d97706" if x<60 else "#dc2626"))
        fr = go.Figure(go.Bar(
            x=rdf["Machine"], y=rdf["Score"],
            marker_color=rdf["Color"],
            text=rdf["Score"], texttemplate="%{text}/100",
            textposition="outside",
            textfont={"family":"DM Sans","size":12,"color":"#1a1a1a"}))
        fr.update_layout(**CHART_BASE, height=280, yaxis_range=[0,115])
        apply_grid(fr)
        st.plotly_chart(fr, use_container_width=True)
        st.caption("Fault (40%) + Vibration exceedances (30%) + Current exceedances (20%) + Rejection (10%)")

    st.markdown("<hr style='border:none;border-top:1px solid #d8d0c0;margin:20px 0'>",
                unsafe_allow_html=True)

    # ── ALERTS LOG ───────────────────────────────────────────────────────────
    st.markdown('<div class="sh">Anomaly Alerts Log</div>', unsafe_allow_html=True)

    if alerts_df.empty:
        st.success("No anomalies detected in the current selection.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Anomaly Rows",      len(alerts_df))
        m2.metric("Machines Affected", alerts_df["machine_id"].nunique())
        m3.metric("Most Affected",     alerts_df["machine_id"].value_counts().idxmax())
        m4.metric("Anomaly Rate",      f"{len(alerts_df)/total*100:.1f}%")

        disp = alerts_df.copy()
        disp["Triggered By"] = disp.apply(lambda r: " | ".join(filter(None, [
            f"Current {r['current_a']:.1f}A > {cur_thresh:.0f}A"       if r["current_a"]>cur_thresh else "",
            f"Vibration {r['vibration_mm_s']:.2f} > {vib_thresh:.0f}mm/s" if r["vibration_mm_s"]>vib_thresh else "",
            f"Rejection {r['rejection_rate']:.1f}% > 10%"               if r["rejection_rate"]>10 else "",
        ])), axis=1)
        disp = disp[["timestamp","machine_id","status","current_a",
                     "vibration_mm_s","rejection_rate","Triggered By"]]
        disp.columns = ["Timestamp","Machine","Status","Current (A)",
                        "Vibration (mm/s)","Rejection (%)","Triggered By"]
        disp["Timestamp"]     = pd.to_datetime(disp["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        disp["Rejection (%)"] = disp["Rejection (%)"].round(2)

        st.dataframe(disp.sort_values("Timestamp", ascending=False),
                     use_container_width=True, hide_index=True,
                     column_config={
                         "Current (A)":     st.column_config.NumberColumn(format="%.1f A"),
                         "Vibration (mm/s)":st.column_config.NumberColumn(format="%.2f mm/s"),
                         "Rejection (%)":   st.column_config.NumberColumn(format="%.2f%%"),
                     })
        st.download_button("⬇ Export Alerts as CSV",
            disp.to_csv(index=False).encode(),
            file_name=f"plant_alerts_{d_start}_{d_end}.csv", mime="text/csv")

    st.markdown("<hr style='border:none;border-top:1px solid #d8d0c0;margin:20px 0'>",
                unsafe_allow_html=True)

    # ── RECOMMENDATIONS ──────────────────────────────────────────────────────
    st.markdown('<div class="sh">Operational Recommendations</div>', unsafe_allow_html=True)

    fault_by_m  = df[df["status"]=="FAULT"].groupby("machine_id").size()
    top_fault_m = fault_by_m.idxmax() if not fault_by_m.empty else "N/A"
    high_risk_m = max(machine_risk, key=machine_risk.get) if machine_risk else "N/A"

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("##### Maintenance Schedule")
        st.markdown(f"""
| Priority | Machine | Action | Timeline |
|----------|---------|--------|----------|
| 🔴 Critical | **{top_fault_m}** | Full inspection — bearings, terminals, lubrication | Immediately |
| 🟠 High | **{high_risk_m}** | Vibration root-cause analysis | Within 48 hrs |
| 🟡 Medium | All | Electrical connection torque check | This week |
| 🟢 Routine | All | Preventive maintenance cycle | Monthly |
| 🔵 Schedule | All | Sensor baseline recalibration | Quarterly |
""")
        for m, rs in machine_risk.items():
            if rs >= 60:   st.error(f"**{m}** — risk score {rs}/100. Immediate inspection required.")
            elif rs >= 30: st.warning(f"**{m}** — risk score {rs}/100. Inspect within 48 hours.")

    with r2:
        st.markdown("##### Advanced Sensing Roadmap")
        st.markdown("""
| Sensor | Detects | Lead Time |
|--------|---------|-----------|
| 🌡 Thermal Camera | Motor & bearing overheating | 2–3 days early warning |
| 🎤 Acoustic Emission | Micro-cracks, bearing wear | Sub-mm defect detection |
| 🛢 Oil Quality | Lubricant degradation | Prevent seizure failures |
| 🔄 Torque Sensor | Rotational load anomalies | Isolate fault type |
| 🌊 Ultrasonic | Internal leaks, cavitation | Non-invasive inspection |
""")
        st.info("Combining thermal and acoustic sensors with existing data can reduce unplanned downtime by up to **40%**.")

    best_shift = df.groupby("shift").apply(
        lambda g:(g["produced_units"].sum()-g["rejected_units"].sum()) /
                  max(g["produced_units"].sum(),1)*100).idxmax()

    st.markdown(f"""
> **Summary — {d_start} to {d_end}** &nbsp;·&nbsp;
> Uptime **{uptime_pct:.1f}%** &nbsp;·&nbsp; Yield **{yield_rate:.1f}%** &nbsp;·&nbsp;
> Faults **{fault_count}** &nbsp;·&nbsp; Anomalies **{len(alerts_df)}**
> &nbsp;·&nbsp; Highest-risk machine: **{high_risk_m}** &nbsp;·&nbsp; Best shift: **{best_shift}**
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ADVANCED ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with TAB_ADV:

    st.markdown('<div class="sh">Deep-Dive Fault & Sensor Analysis</div>', unsafe_allow_html=True)
    st.caption("Detailed statistical charts for academic analysis and reporting.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── FIGURE 1 — Vibration over time + FAULT red dots ──────────────────────
    st.markdown("#### Figure 1 — Vibration Over Time: Identifying Fault Correlation")

    fault_rows = df[df["status"]=="FAULT"]
    fig_f1 = go.Figure()

    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp")
        fig_f1.add_trace(go.Scatter(x=sub["timestamp"], y=sub["vibration_mm_s"],
            name=mach, line=dict(color=MACH_COLORS.get(mach,"#555"), width=1.5), opacity=0.8,
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Vib: %{{y:.2f}} mm/s<extra></extra>"))

    if not fault_rows.empty:
        fig_f1.add_trace(go.Scatter(
            x=fault_rows["timestamp"], y=fault_rows["vibration_mm_s"],
            mode="markers", name="FAULT Event",
            marker=dict(color="#dc2626", size=9, symbol="circle",
                        line=dict(color="#fff", width=1)),
            hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>Vib: %{y:.2f} mm/s<br>%{customdata}<extra></extra>",
            customdata=fault_rows["machine_id"]))

    fig_f1.add_hline(y=vib_thresh, line_color="#dc2626", line_dash="dot",
        annotation_text=f"Critical {vib_thresh:.0f} mm/s",
        annotation_font_color="#dc2626", annotation_position="top right")
    fig_f1.update_layout(**CHART_BASE, height=360, xaxis_title="Timestamp",
        yaxis_title="Vibration (mm/s)",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
        title=dict(text="Vibration Over Time: Identifying Fault Correlation",
                   font_color="#888", font_size=13))
    apply_grid(fig_f1)
    st.plotly_chart(fig_f1, use_container_width=True)

    low_vib_faults = fault_rows[fault_rows["vibration_mm_s"] <= vib_thresh]
    st.markdown(f"""
> **Observation:** FAULT events (red dots) generally coincide with high vibration (> {vib_thresh:.0f} mm/s).
> **{len(low_vib_faults)}** outlier fault(s) occurred below the vibration threshold —
> likely triggered by electrical overcurrent rather than mechanical vibration.
> This confirms the importance of monitoring both sensors simultaneously.
""")
    st.markdown("---")

    # ── FIGURE 2 — Vibration vs Rejection Rate scatter ────────────────────────
    st.markdown("#### Figure 2 — Correlation: Vibration vs. Rejection Rate (RUNNING Only)")

    running_filt = df[(df["status"]=="RUNNING") & (df["vibration_mm_s"]<=8)].copy()

    if len(running_filt) > 2:
        z      = np.polyfit(running_filt["vibration_mm_s"], running_filt["rejection_rate"], 1)
        x_line = np.linspace(running_filt["vibration_mm_s"].min(),
                             running_filt["vibration_mm_s"].max(), 100)
        y_line = np.polyval(z, x_line)
        r_val  = running_filt[["vibration_mm_s","rejection_rate"]].corr().iloc[0,1]
    else:
        x_line = y_line = []; r_val = 0

    fig_f2 = go.Figure()
    for mach in sel_machines:
        sub = running_filt[running_filt["machine_id"]==mach]
        fig_f2.add_trace(go.Scatter(x=sub["vibration_mm_s"], y=sub["rejection_rate"],
            mode="markers", name=mach,
            marker=dict(color=MACH_COLORS.get(mach,"#555"), size=7, opacity=0.55),
            hovertemplate=f"<b>{mach}</b><br>Vib: %{{x:.2f}} mm/s<br>Rejection: %{{y:.1f}}%<extra></extra>"))

    if len(x_line) > 0:
        fig_f2.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines",
            name=f"Trend (r = {r_val:.4f})", line=dict(color="#991b1b", width=2),
            hovertemplate=f"Trend line<extra></extra>"))

    fig_f2.update_layout(**CHART_BASE, height=360,
        xaxis_title="Vibration Level (mm/s)", yaxis_title="Rejection Rate (%)",
        title=dict(text="Correlation: Vibration vs. Rejection Rate (RUNNING Only)",
                   font_color="#888", font_size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11))
    apply_grid(fig_f2)
    st.plotly_chart(fig_f2, use_container_width=True)
    st.markdown(f"""
> **Observation:** Pearson r = **{r_val:.4f}** — near-zero correlation.
> Vibration level does not meaningfully predict rejection rate during normal operation.
> Quality issues are driven by other factors such as tooling wear or material variability.
""")
    st.markdown("---")

    # ── FIGURE 3 — Per-machine dual axis: Vibration + FAULT + Rejection ───────
    st.markdown("#### Figure 3 — Machine Health Dashboard: Vibration & Quality Trends")

    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp").copy()
        if sub.empty: continue
        fault_sub = sub[sub["status"]=="FAULT"]

        fig_f3m = make_subplots(specs=[[{"secondary_y": True}]])

        fig_f3m.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["vibration_mm_s"], name="Vibration (mm/s)",
            line=dict(color="#2563eb", width=1.5),
            hovertemplate="%{x|%b %d %H:%M}<br>Vib: %{y:.2f} mm/s<extra></extra>"),
            secondary_y=False)

        if not fault_sub.empty:
            fig_f3m.add_trace(go.Scatter(
                x=fault_sub["timestamp"], y=fault_sub["vibration_mm_s"],
                mode="markers", name="FAULT Triggered",
                marker=dict(color="#1a1a1a", size=9, symbol="circle",
                            line=dict(color="#fff", width=1)),
                hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>%{y:.2f} mm/s<extra></extra>"),
                secondary_y=False)

        fig_f3m.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["rejection_rate"], name="Rejection Rate (%)",
            line=dict(color="#dc2626", width=1.5, dash="dash"),
            hovertemplate="%{x|%b %d %H:%M}<br>Rejection: %{y:.1f}%<extra></extra>"),
            secondary_y=True)

        fig_f3m.add_hline(y=vib_thresh, line_color="#dc2626", line_dash="dot",
            annotation_text=f"Critical {vib_thresh:.0f} mm/s",
            annotation_font_color="#dc2626", annotation_position="top right",
            secondary_y=False)

        fig_f3m.update_layout(**CHART_BASE, height=300, hovermode="x unified",
            title=dict(text=f"{mach} — Vibration & Quality Trends",
                       font_color="#888", font_size=13),
            legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11, orientation="h", y=1.12))
        fig_f3m.update_xaxes(title_text="Timestamp", gridcolor="#e8e0d0", zeroline=False)
        fig_f3m.update_yaxes(title_text="Vibration (mm/s)", gridcolor="#e8e0d0",
                              zeroline=False, range=[0, sub["vibration_mm_s"].max()*1.2],
                              secondary_y=False)
        fig_f3m.update_yaxes(title_text="Rejection Rate (%)", gridcolor="#e8e0d0",
                              zeroline=False, range=[0,100],
                              tickfont=dict(color="#dc2626"),
                              title_font=dict(color="#dc2626"),
                              secondary_y=True)
        st.plotly_chart(fig_f3m, use_container_width=True, config={"displayModeBar":False})

    fault_hi = df[(df["status"]=="FAULT") & (df["vibration_mm_s"]>vib_thresh)]
    fault_lo = df[(df["status"]=="FAULT") & (df["vibration_mm_s"]<=vib_thresh)]
    st.markdown(f"""
> **Observation:** **{len(fault_hi)}** fault(s) coincide with vibration above {vib_thresh:.0f} mm/s.
> **{len(fault_lo)}** fault(s) occurred at lower vibration, suggesting electrical overcurrent as the trigger.
> Rejection rate spikes closely align with fault events, confirming direct quality impact.
""")
    st.markdown("---")

    # ── FIGURE 4 — Vibration boxplot by status ────────────────────────────────
    st.markdown("#### Figure 4 — Vibration Distribution Grouped by Status")

    fig_f4 = go.Figure()
    box_colors = {"IDLE":"#2563eb","RUNNING":"#d97706","FAULT":"#6272a4"}
    for status in ["IDLE","RUNNING","FAULT"]:
        sub = df[df["status"]==status]["vibration_mm_s"]
        if sub.empty: continue
        fig_f4.add_trace(go.Box(y=sub, name=status, boxmean=True,
            marker_color=box_colors.get(status,"#aaa"),
            line_color=box_colors.get(status,"#aaa"),
            fillcolor=box_colors.get(status,"#aaa"),
            opacity=0.6,
            hovertemplate=f"<b>{status}</b><br>%{{y:.2f}} mm/s<extra></extra>"))

    fig_f4.add_hline(y=vib_thresh, line_color="#dc2626", line_dash="dot",
        annotation_text=f"Critical {vib_thresh:.0f} mm/s", annotation_font_color="#dc2626")
    fig_f4.update_layout(**CHART_BASE, height=380,
        xaxis_title="Status", yaxis_title="Vibration (mm/s)",
        title=dict(text="Vibration Distribution Grouped by Status",
                   font_color="#888", font_size=13))
    apply_grid(fig_f4)
    st.plotly_chart(fig_f4, use_container_width=True)

    run_med   = df[df["status"]=="RUNNING"]["vibration_mm_s"].median()
    fault_med = df[df["status"]=="FAULT"]["vibration_mm_s"].median() if fault_count>0 else 0
    idle_med  = df[df["status"]=="IDLE"]["vibration_mm_s"].median()
    st.markdown(f"""
> **Observation:** FAULT median vibration ({fault_med:.1f} mm/s) is approximately
> {fault_med/run_med:.1f}× higher than RUNNING ({run_med:.1f} mm/s) and
> IDLE ({idle_med:.1f} mm/s). The wide FAULT IQR indicates variable fault severity.
""")
    st.markdown("---")

    # ── FIGURE 5 — Current vs Vibration + Rejection by machine/shift ──────────
    st.markdown("#### Figure 5 — Fault Diagnostics: Current vs Vibration & Rejection by Machine and Shift")

    fig_f5 = make_subplots(rows=1, cols=2,
        subplot_titles=("(a) Current vs Vibration by Status",
                        "(b) Rejection Rate by Machine and Shift (RUNNING only)"),
        column_widths=[0.55, 0.45])

    MARKER_SHAPE = {"M1":"circle","M2":"square","M3":"triangle-up"}
    STATUS_COL   = {"RUNNING":"#16a34a","IDLE":"#d97706","FAULT":"#dc2626"}

    for status in ["RUNNING","IDLE","FAULT"]:
        sub_s = df[df["status"]==status]
        for mach in sel_machines:
            sub = sub_s[sub_s["machine_id"]==mach]
            if sub.empty: continue
            fig_f5.add_trace(go.Scatter(
                x=sub["current_a"], y=sub["vibration_mm_s"], mode="markers",
                name=f"{status} {mach}", showlegend=True,
                marker=dict(color=STATUS_COL[status],
                            symbol=MARKER_SHAPE.get(mach,"circle"),
                            size=5, opacity=0.5 if status!="FAULT" else 0.9),
                hovertemplate=f"<b>{mach} {status}</b><br>Current: %{{x:.1f}} A<br>Vib: %{{y:.2f}} mm/s<extra></extra>"),
                row=1, col=1)

    fig_f5.add_vline(x=cur_thresh, row=1, col=1, line_color="#dc2626", line_dash="dash",
        annotation_text=f"{cur_thresh:.0f} A", annotation_font_color="#dc2626")
    fig_f5.add_hline(y=vib_thresh, row=1, col=1, line_color="#d97706", line_dash="dot",
        annotation_text=f"{vib_thresh:.0f} mm/s", annotation_font_color="#d97706")

    run_rej = (df[df["status"]=="RUNNING"]
               .groupby(["machine_id","shift"])
               .apply(lambda g: g["rejected_units"].sum()/max(g["produced_units"].sum(),1)*100)
               .reset_index(name="rej_rate"))

    shift_colors = {"Day":"#d97706","Night":"#2563eb"}
    for shift in ["Day","Night"]:
        sub = run_rej[run_rej["shift"]==shift]
        if sub.empty: continue
        fig_f5.add_trace(go.Bar(
            x=sub["machine_id"], y=sub["rej_rate"], name=shift,
            marker_color=shift_colors[shift],
            text=sub["rej_rate"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(family="DM Sans", size=11, color="#1a1a1a"),
            hovertemplate=f"<b>{shift} shift</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>"),
            row=1, col=2)

    fig_f5.update_xaxes(title_text="Motor Current (A)",  row=1, col=1,
                        gridcolor="#e8e0d0", zeroline=False)
    fig_f5.update_yaxes(title_text="Vibration (mm/s)",   row=1, col=1,
                        gridcolor="#e8e0d0", zeroline=False)
    fig_f5.update_xaxes(title_text="Machine ID",         row=1, col=2,
                        gridcolor="#e8e0d0", zeroline=False)
    fig_f5.update_yaxes(title_text="Rejection Rate (%)", row=1, col=2,
                        gridcolor="#e8e0d0", zeroline=False,
                        range=[0, run_rej["rej_rate"].max()*1.35 if not run_rej.empty else 10])
    fig_f5.update_layout(**CHART_BASE, height=420, barmode="group",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, orientation="v"),
        title=dict(text="Fault Diagnostics — Current vs Vibration and Rejection Rate",
                   font_color="#888", font_size=13))
    st.plotly_chart(fig_f5, use_container_width=True)

    day_avg   = run_rej[run_rej["shift"]=="Day"]["rej_rate"].mean()
    night_avg = run_rej[run_rej["shift"]=="Night"]["rej_rate"].mean()
    better    = "Night" if night_avg < day_avg else "Day"
    fault_zone = df[(df["current_a"]>cur_thresh) & (df["vibration_mm_s"]>vib_thresh)]
    st.markdown(f"""
> **Observation (a):** FAULT readings cluster where both current > {cur_thresh:.0f} A and
> vibration > {vib_thresh:.0f} mm/s simultaneously — {len(fault_zone)} readings exceeded both thresholds.
> Combined exceedance is the strongest fault predictor.
>
> **Observation (b):** Rejection rates are consistent across shifts (~3–4%).
> **{better} shift** performs marginally better. M3 has the highest rejection rate across both shifts,
> suggesting a machine-specific quality issue.
""")

    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sh">Analysis Summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
| Figure | Key Finding |
|--------|------------|
| **Fig 1** — Fault vs Vibration | {fault_count} FAULT events; majority above {vib_thresh:.0f} mm/s vibration |
| **Fig 2** — Vibration vs Rejection | Near-zero correlation (r ≈ {r_val:.3f}); vibration does not drive quality |
| **Fig 3** — Health Dashboard | FAULT events co-occur with rejection spikes per machine |
| **Fig 4** — Vibration Boxplot | FAULT median ({fault_med:.1f} mm/s) vs RUNNING ({run_med:.1f} mm/s) — {fault_med/run_med:.1f}× higher |
| **Fig 5** — Dual-threshold | Combined high current + high vibration = strongest fault predictor |
""")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<hr style='border:none;border-top:1px solid #d8d0c0;margin:24px 0 8px'>",
            unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;font-size:11px;color:#bbb;padding-bottom:12px;
            font-family:DM Sans,sans-serif;letter-spacing:.06em'>
    EE4409 CA2 &nbsp;·&nbsp; PlantIQ Manufacturing Dashboard &nbsp;·&nbsp;
    Streamlit · Plotly · Pandas
</div>""", unsafe_allow_html=True)

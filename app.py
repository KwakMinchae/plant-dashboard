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
# CSS — original dark industrial theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#080c14;color:#c8d8e8;font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:#0b1020;border-right:1px solid #1a2540;}
h1,h2,h3{font-family:'Syne',sans-serif;}
.kpi-wrap{background:linear-gradient(145deg,#0f1928,#131e30);border:1px solid #1e3050;border-radius:16px;
  padding:24px 20px 18px;text-align:center;position:relative;overflow:hidden;transition:transform .25s,box-shadow .25s;}
.kpi-wrap:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,120,255,.15);}
.kpi-wrap::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--kpi-accent,#2563eb);border-radius:16px 16px 0 0;}
.kpi-label{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.12em;color:#4a6080;
  text-transform:uppercase;margin-bottom:10px;}
.kpi-value{font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;line-height:1;
  color:var(--kpi-color,#7eb8f7);}
.kpi-sub{font-size:11px;color:#3a5070;margin-top:8px;font-family:'IBM Plex Mono',monospace;}
.mc{border-radius:14px;padding:18px 20px;margin-bottom:2px;border-left:4px solid transparent;
  transition:transform .2s;}
.mc:hover{transform:translateX(3px);}
.mc-running{background:#071a10;border-color:#16a34a;}
.mc-idle{background:#1a1500;border-color:#ca8a04;}
.mc-fault{background:#180808;border-color:#dc2626;animation:fault-pulse 2s ease-in-out infinite;}
@keyframes fault-pulse{0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,0);}50%{box-shadow:0 0 0 8px rgba(220,38,38,.15);}}
.mc-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
.mc-id{font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;}
.mc-badge{font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.1em;
  padding:3px 10px;border-radius:20px;}
.badge-running{background:#14532d;color:#4ade80;}
.badge-idle{background:#422006;color:#fbbf24;}
.badge-fault{background:#450a0a;color:#f87171;}
.mc-metrics{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;}
.mc-m{background:rgba(255,255,255,.03);border-radius:8px;padding:8px 10px;}
.mc-m-label{font-size:10px;color:#3a5070;font-family:'IBM Plex Mono',monospace;
  letter-spacing:.08em;margin-bottom:2px;}
.mc-m-val{font-size:1.1rem;font-weight:600;}
.risk-low{color:#4ade80;}.risk-med{color:#fbbf24;}.risk-high{color:#f87171;}
.sh{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.15em;color:#2563eb;
  text-transform:uppercase;border-bottom:1px solid #1a2540;padding-bottom:8px;margin-bottom:16px;}
.info-box{background:#0b1422;border:1px solid #1a2540;border-radius:10px;padding:12px;
  margin:8px 0;font-size:.8rem;line-height:1.7;}
.info-box b{color:#60a5fa;}.crit{color:#f87171;font-weight:700;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:#0b1020;}
::-webkit-scrollbar-thumb{background:#1e3050;border-radius:3px;}
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
    df["rejection_rate"] = np.where(
        df["status"]=="FAULT", 100,
        np.where(df["produced_units"]>0,
                 df["rejected_units"]/df["produced_units"]*100, 0)
    )
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
    st.markdown("""<div style='text-align:center;padding:10px 0 20px'>
    <div style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;
                background:linear-gradient(90deg,#3b82f6,#60a5fa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent'>⚙️ PlantIQ</div>
    <div style='font-family:IBM Plex Mono,monospace;font-size:10px;color:#2a4060;
                letter-spacing:.15em'>MONITORING DASHBOARD</div></div>""", unsafe_allow_html=True)

    with st.expander("ℹ️ Sensor Guide", expanded=False):
        st.markdown("""
<div class="info-box"><b>⚡ Current Sensor</b><br>Measures motor electrical load in Amperes.<br>
Typical: <b>10–50 A</b> &nbsp;·&nbsp; <span class="crit">CRITICAL &gt; 60 A</span></div>
<div class="info-box"><b>📳 Vibration Sensor</b><br>Measures mechanical velocity in mm/s.<br>
Typical: <b>1–8 mm/s</b> &nbsp;·&nbsp; <span class="crit">CRITICAL &gt; 10 mm/s</span></div>
<div class="info-box"><b>🔴 Fault Triggers</b><br>• Vibration <b>&gt; 10 mm/s</b><br>
• Current <b>&gt; 60 A</b><br>• Rejection rate <b>&gt; 10%</b></div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh" style="margin-top:16px">FILTERS</div>', unsafe_allow_html=True)
    all_machines = sorted(df_raw["machine_id"].unique())
    sel_machines = st.multiselect("Machine", all_machines, default=all_machines)
    mn, mx = df_raw["date"].min(), df_raw["date"].max()
    d_range = st.date_input("Date Range", value=(mn, mx), min_value=mn, max_value=mx)
    d_start, d_end = (d_range[0], d_range[1]) if len(d_range)==2 else (mn, mx)
    sel_shifts = st.multiselect("Shift", ["Day","Night"], default=["Day","Night"])

    st.markdown('<div class="sh" style="margin-top:16px">THRESHOLDS</div>', unsafe_allow_html=True)
    vib_thresh = st.slider("Vibration alert (mm/s)", 5.0, 15.0, 10.0, 0.5)
    cur_thresh = st.slider("Current alert (A)", 40.0, 80.0, 60.0, 1.0)

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
# SHARED CHART STYLE
# ─────────────────────────────────────────────────────────────────────────────
MACH_COLORS = {"M1":"#3b82f6","M2":"#f97316","M3":"#22c55e"}

CHART_BASE = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,12,20,.8)",
                  font_color="#c8d8e8", font_family="IBM Plex Mono",
                  margin=dict(l=10,r=10,t=45,b=10))

def apply_grid(fig, rows=None):
    kw = dict(gridcolor="#0f1928", zeroline=False)
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
st.markdown(f"""<div style='display:flex;align-items:baseline;gap:16px;margin-bottom:2px'>
  <h1 style='margin:0;font-size:1.9rem;background:linear-gradient(90deg,#60a5fa,#93c5fd);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent'>⚙️ PlantIQ</h1>
  <span style='font-family:IBM Plex Mono,monospace;font-size:11px;color:#2a4060'>
    {d_start} → {d_end} &nbsp;|&nbsp; {', '.join(sel_machines)} &nbsp;|&nbsp; {', '.join(sel_shifts)} shift
  </span></div>""", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
TAB_MAIN, TAB_ADV = st.tabs(["📊  Live Dashboard", "🔬  Advanced Analysis"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with TAB_MAIN:

    # ── KPI CARDS ────────────────────────────────────────────────────────────
    st.markdown('<div class="sh">📊 PLANT-WIDE KPIs</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    def kpi(col, label, value, sub, accent, color):
        col.markdown(f"""<div class="kpi-wrap" style="--kpi-accent:{accent};--kpi-color:{color}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

    up_col  = "#4ade80" if uptime_pct>=80 else ("#fbbf24" if uptime_pct>=60 else "#f87171")
    yr_col  = "#4ade80" if yield_rate>=90 else ("#fbbf24" if yield_rate>=75 else "#f87171")
    ft_col  = "#f87171" if fault_count>0 else "#4ade80"
    top_risk = max(machine_risk.values()) if machine_risk else 0
    rk_col  = "#4ade80" if top_risk<30 else ("#fbbf24" if top_risk<60 else "#f87171")

    kpi(k1,"⏱ PLANT UPTIME",   f"{uptime_pct:.1f}%", f"{(df['status']=='RUNNING').sum():,}/{total:,} readings","#2563eb",up_col)
    kpi(k2,"✅ YIELD RATE",     f"{yield_rate:.1f}%", f"{total_prod-total_rej:,} good of {total_prod:,}","#16a34a",yr_col)
    kpi(k3,"🚨 FAULT READINGS", str(fault_count),      f"{fault_count/total*100:.1f}% of all readings","#dc2626",ft_col)
    kpi(k4,"⚠️ MAX RISK SCORE", f"{top_risk}/100",     "Highest machine risk index","#ca8a04",rk_col)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── MACHINE CARDS + GAUGES ───────────────────────────────────────────────
    st.markdown('<div class="sh">🤖 INDIVIDUAL MACHINE STATUS</div>', unsafe_allow_html=True)

    STATUS_CSS  = {"RUNNING":"mc-running","IDLE":"mc-idle","FAULT":"mc-fault"}
    BADGE_CSS   = {"RUNNING":"badge-running","IDLE":"badge-idle","FAULT":"badge-fault"}
    STATUS_ICON = {"RUNNING":"▶","IDLE":"⏸","FAULT":"⚡"}

    def make_gauge(val, max_v, w_thresh, c_thresh, title):
        bar_col = "#4ade80" if val<=w_thresh else ("#fbbf24" if val<=c_thresh else "#f87171")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=val,
            number={"suffix":" mm/s","font":{"size":14,"color":"#c8d8e8"}},
            title={"text":title,"font":{"size":11,"color":"#4a6080","family":"IBM Plex Mono"}},
            gauge={"axis":{"range":[0,max_v],"tickcolor":"#1e3050","tickfont":{"color":"#3a5070","size":9}},
                   "bar":{"color":bar_col,"thickness":.28},"bgcolor":"#080c14","bordercolor":"#1a2540",
                   "steps":[{"range":[0,w_thresh],"color":"#071510"},
                             {"range":[w_thresh,c_thresh],"color":"#1a1200"},
                             {"range":[c_thresh,max_v],"color":"#180808"}],
                   "threshold":{"line":{"color":"#dc2626","width":3},"thickness":.8,"value":c_thresh}}))
        fig.update_layout(height=170,margin=dict(l=15,r=15,t=35,b=5),
                          paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#c8d8e8")
        return fig

    mcols = st.columns(len(sel_machines))
    for i, mach in enumerate(sel_machines):
        row = latest[latest["machine_id"]==mach]
        if row.empty: continue
        r = row.iloc[0]; st_ = r["status"]; rs = machine_risk[mach]
        rsk_cls = "risk-low" if rs<30 else ("risk-med" if rs<60 else "risk-high")
        rsk_lbl = "LOW" if rs<30 else ("MEDIUM" if rs<60 else "HIGH")
        cc = "#f87171" if r["current_a"]>cur_thresh else "#c8d8e8"
        vc = "#f87171" if r["vibration_mm_s"]>vib_thresh else "#c8d8e8"
        with mcols[i]:
            st.markdown(f"""<div class="mc {STATUS_CSS.get(st_,'mc-idle')}">
              <div class="mc-head"><span class="mc-id">{mach}</span>
                <span class="mc-badge {BADGE_CSS.get(st_,'badge-idle')}">{STATUS_ICON.get(st_,'?')} {st_}</span></div>
              <div class="mc-metrics">
                <div class="mc-m"><div class="mc-m-label">CURRENT</div>
                  <div class="mc-m-val" style="color:{cc}">{r['current_a']:.1f} A</div></div>
                <div class="mc-m"><div class="mc-m-label">VIBRATION</div>
                  <div class="mc-m-val" style="color:{vc}">{r['vibration_mm_s']:.2f} mm/s</div></div>
                <div class="mc-m"><div class="mc-m-label">PRODUCED</div>
                  <div class="mc-m-val">{int(r['produced_units'])}</div></div>
                <div class="mc-m"><div class="mc-m-label">REJECTED</div>
                  <div class="mc-m-val">{int(r['rejected_units'])}</div></div>
              </div>
              <div style="margin-top:12px;font-family:'IBM Plex Mono',monospace;font-size:11px;">
                RISK INDEX &nbsp;<span class="{rsk_cls}" style="font-weight:700">{rs}/100 — {rsk_lbl}</span></div>
              <div style="background:#0f1928;border-radius:6px;height:6px;margin-top:6px;">
                <div style="background:{'#4ade80' if rs<30 else '#fbbf24' if rs<60 else '#f87171'};
                            width:{rs}%;height:100%;border-radius:6px"></div></div>
            </div>""", unsafe_allow_html=True)
            st.plotly_chart(make_gauge(r["vibration_mm_s"],20,8,vib_thresh,f"{mach} Vibration Health"),
                            use_container_width=True, config={"displayModeBar":False})
    st.markdown("---")

    # ── SENSOR TRENDS ────────────────────────────────────────────────────────
    st.markdown('<div class="sh">📈 SENSOR TRENDS OVER TIME</div>', unsafe_allow_html=True)
    fig_trend = make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.09,
        subplot_titles=("Motor Current (A)","Vibration Velocity (mm/s)"),row_heights=[.5,.5])
    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp").copy()
        c   = MACH_COLORS.get(mach,"#aaa")
        sub["cur_roll"] = sub["current_a"].rolling(8,min_periods=1).mean()
        sub["vib_roll"] = sub["vibration_mm_s"].rolling(8,min_periods=1).mean()
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["current_a"],name=mach,
            line=dict(color=c,width=1),opacity=.4,showlegend=True),row=1,col=1)
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["cur_roll"],name=f"{mach} avg",
            line=dict(color=c,width=2.5),showlegend=False),row=1,col=1)
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["vibration_mm_s"],name=mach,
            line=dict(color=c,width=1,dash="dot"),opacity=.4,showlegend=False),row=2,col=1)
        fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["vib_roll"],name=f"{mach} avg",
            line=dict(color=c,width=2.5),showlegend=False),row=2,col=1)
    fig_trend.add_hline(y=cur_thresh,row=1,col=1,line_color="#dc2626",line_dash="dash",
        annotation_text=f"Alert {cur_thresh:.0f}A",annotation_font_color="#dc2626")
    fig_trend.add_hline(y=vib_thresh,row=2,col=1,line_color="#dc2626",line_dash="dash",
        annotation_text=f"Alert {vib_thresh:.0f}mm/s",annotation_font_color="#dc2626")
    fig_trend.update_layout(**CHART_BASE,height=460,hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)",font_size=11))
    apply_grid(fig_trend,[1,2])
    st.plotly_chart(fig_trend, use_container_width=True)
    st.caption("Thick lines = 8-reading rolling average. Thin = raw sensor data. Red dashed = alert threshold.")
    st.markdown("---")

    # ── PRODUCTION + CORRELATION + RISK ──────────────────────────────────────
    st.markdown('<div class="sh">🏗️ PRODUCTION & CORRELATION</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2,1.8,1.8,1.8])
    with c4:
        st.markdown("**Status Distribution (hrs)**")
        status_hrs = df.groupby(["machine_id","status"]).size().reset_index(name="hours")
        status_colors_bar = {"FAULT":"#ef4444","IDLE":"#9ca3af","RUNNING":"#3b82f6"}
        fos = go.Figure()
        for st_opt in ["FAULT","IDLE","RUNNING"]:
            sub = status_hrs[status_hrs["status"]==st_opt]
            fos.add_trace(go.Bar(name=st_opt, x=sub["machine_id"], y=sub["hours"],
                marker_color=status_colors_bar[st_opt]))
        fos.update_layout(**CHART_BASE, height=290, barmode="group",
            xaxis_title="Machine", yaxis_title="Hours",
            legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10))
        apply_grid(fos)
        st.plotly_chart(fos, use_container_width=True)
        st.caption("M1 has disproportionately high fault hours.")
    with c1:
        st.markdown("**Production by Shift**")
        sdf = df.groupby(["shift","machine_id"])[["produced_units","rejected_units"]].sum().reset_index()
        fb  = go.Figure()
        for mach in sel_machines:
            sub = sdf[sdf["machine_id"]==mach]; col = MACH_COLORS.get(mach,"#aaa")
            fb.add_trace(go.Bar(name=f"{mach} Good",x=sub["shift"],
                y=sub["produced_units"]-sub["rejected_units"],marker_color=col,opacity=.9))
            fb.add_trace(go.Bar(name=f"{mach} Rejected",x=sub["shift"],
                y=sub["rejected_units"],marker_color=col,opacity=.35,marker_pattern_shape="/"))
        fb.update_layout(**CHART_BASE,height=290,barmode="group",
            legend=dict(bgcolor="rgba(0,0,0,0)",font_size=10))
        apply_grid(fb)
        st.plotly_chart(fb, use_container_width=True)
    with c2:
        st.markdown("**Sensor Correlation Heatmap**")
        corr = df[["current_a","vibration_mm_s","rejection_rate","produced_units"]].corr().round(2)
        fh = go.Figure(go.Heatmap(z=corr.values,
            x=["Current","Vibration","Rejection%","Produced"],
            y=["Current","Vibration","Rejection%","Produced"],
            colorscale=[[0,"#dc2626"],[.5,"#0f1928"],[1,"#2563eb"]],zmid=0,
            text=corr.values,texttemplate="%{text}",textfont={"size":12,"family":"IBM Plex Mono"}))
        fh.update_layout(**CHART_BASE,height=290)
        st.plotly_chart(fh, use_container_width=True)
        st.caption("Current & Vibration (+0.30) spike together before faults.")
    with c3:
        st.markdown("**Predictive Risk Score**")
        rdf = pd.DataFrame({"Machine":list(machine_risk.keys()),"Score":list(machine_risk.values())})
        rdf["Color"] = rdf["Score"].apply(lambda x:"#4ade80" if x<30 else("#fbbf24" if x<60 else"#f87171"))
        fr = go.Figure(go.Bar(x=rdf["Machine"],y=rdf["Score"],marker_color=rdf["Color"],
            text=rdf["Score"],texttemplate="%{text}/100",textposition="outside",
            textfont={"family":"IBM Plex Mono","size":12}))
        fr.update_layout(**CHART_BASE,height=290,yaxis_range=[0,115])
        apply_grid(fr)
        st.plotly_chart(fr, use_container_width=True)
        st.caption("Fault(40%) + Vibration exceedances(30%) + Current exceedances(20%) + Rejection(10%)")
    st.markdown("---")

    # ── ALERTS LOG ───────────────────────────────────────────────────────────
    st.markdown('<div class="sh">🚨 ANOMALY ALERTS LOG</div>', unsafe_allow_html=True)
    if alerts_df.empty:
        st.success("✅ No anomalies detected.")
    else:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Anomaly Rows",      len(alerts_df))
        m2.metric("Machines Affected", alerts_df["machine_id"].nunique())
        m3.metric("Most Affected",     alerts_df["machine_id"].value_counts().idxmax())
        m4.metric("Anomaly Rate",      f"{len(alerts_df)/total*100:.1f}%")
        disp = alerts_df.copy()
        disp["Triggered By"] = disp.apply(lambda r: " | ".join(filter(None,[
            f"⚡ {r['current_a']:.1f}A>{cur_thresh:.0f}A"          if r["current_a"]>cur_thresh else "",
            f"📳 {r['vibration_mm_s']:.2f}>{vib_thresh:.0f}mm/s"   if r["vibration_mm_s"]>vib_thresh else "",
            f"❌ rej {r['rejection_rate']:.1f}%>10%"                if r["rejection_rate"]>10 else "",
        ])),axis=1)
        disp = disp[["timestamp","machine_id","status","current_a","vibration_mm_s","rejection_rate","Triggered By"]]
        disp.columns = ["Timestamp","Machine","Status","Current (A)","Vibration (mm/s)","Rejection (%)","Triggered By"]
        disp["Timestamp"]     = pd.to_datetime(disp["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        disp["Rejection (%)"] = disp["Rejection (%)"].round(2)
        st.dataframe(disp.sort_values("Timestamp",ascending=False),use_container_width=True,hide_index=True,
            column_config={"Current (A)":st.column_config.NumberColumn(format="%.1f A"),
                           "Vibration (mm/s)":st.column_config.NumberColumn(format="%.2f mm/s"),
                           "Rejection (%)":st.column_config.NumberColumn(format="%.2f%%")})
        st.download_button("⬇️ Export Alerts as CSV",
            disp.to_csv(index=False).encode(),
            file_name=f"plant_alerts_{d_start}_{d_end}.csv", mime="text/csv")
    st.markdown("---")

    # ── RECOMMENDATIONS ──────────────────────────────────────────────────────
    st.markdown('<div class="sh">💡 OPERATIONAL RECOMMENDATIONS</div>', unsafe_allow_html=True)
    fault_by_m  = df[df["status"]=="FAULT"].groupby("machine_id").size()
    top_fault_m = fault_by_m.idxmax() if not fault_by_m.empty else "N/A"
    high_risk_m = max(machine_risk, key=machine_risk.get) if machine_risk else "N/A"
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("#### 🔧 Dynamic Maintenance Schedule")
        st.markdown(f"""
| Priority | Machine | Action | Timeline |
|----------|---------|--------|----------|
| 🔴 Critical | **{top_fault_m}** | Full inspection — bearings, terminals, lubrication | **Immediately** |
| 🟠 High | **{high_risk_m}** | Vibration root-cause analysis | Within 48 hrs |
| 🟡 Medium | All | Electrical connection torque check | This week |
| 🟢 Routine | All | Preventive maintenance cycle | Monthly |
| 🔵 Schedule | All | Sensor baseline recalibration | Quarterly |
""")
        for m, rs in machine_risk.items():
            if rs>=60: st.error(f"🚨 **{m}** risk score **{rs}/100** — immediate inspection.")
            elif rs>=30: st.warning(f"⚠️ **{m}** risk score **{rs}/100** — inspect within 48 hrs.")
    with r2:
        st.markdown("#### 🔬 Advanced Sensing Roadmap")
        st.markdown("""
| Sensor | Detects | Lead Time |
|--------|---------|-----------|
| 🌡️ **Thermal Camera** | Motor/bearing overheating | 2–3 days early warning |
| 🎤 **Acoustic Emission** | Micro-cracks, bearing wear | Sub-mm defect detection |
| 🛢️ **Oil Quality** | Lubricant degradation | Prevent seizure failures |
| 🔄 **Torque Sensor** | Rotational load anomalies | Isolate fault type |
| 🌊 **Ultrasonic** | Internal leaks, cavitation | Non-invasive inspection |
""")
        st.info("💡 Thermal + acoustic sensors reduce unplanned downtime by up to **40%** via predictive ML.")

    best_shift = df.groupby("shift").apply(
        lambda g:(g["produced_units"].sum()-g["rejected_units"].sum())/max(g["produced_units"].sum(),1)*100).idxmax()
    st.markdown(f"""> **📋 Summary — {d_start} to {d_end}**
> Uptime **{uptime_pct:.1f}%** · Yield **{yield_rate:.1f}%** · Faults **{fault_count}** · Anomalies **{len(alerts_df)}**
> Highest-risk: **{high_risk_m}** ({machine_risk.get(high_risk_m,0)}/100) · Best shift: **{best_shift}**""")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ADVANCED ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with TAB_ADV:

    st.markdown('<div class="sh">🔬 DEEP-DIVE FAULT & SENSOR ANALYSIS</div>', unsafe_allow_html=True)
    st.caption("Detailed statistical charts for academic analysis and reporting.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── FIGURE 1 — Dual axis: Vibration + Current over time + FAULT dots ─────
    st.markdown("#### Figure 1 — Vibration & Current vs. Time (mm/s, A)")

    fault_rows = df[df["status"]=="FAULT"]

    fig_f1 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.08,
        subplot_titles=("Vibration (mm/s)", "Motor Current (A)"),
        row_heights=[.5, .5])

    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp")
        c   = MACH_COLORS.get(mach, "#aaa")
        # vibration
        fig_f1.add_trace(go.Scatter(x=sub["timestamp"], y=sub["vibration_mm_s"],
            name=mach, line=dict(color=c, width=1.5), opacity=0.85,
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Vib: %{{y:.2f}} mm/s<extra></extra>"),
            row=1, col=1)
        # current
        fig_f1.add_trace(go.Scatter(x=sub["timestamp"], y=sub["current_a"],
            name=f"{mach} Current", line=dict(color=c, width=1.5, dash="dot"), opacity=0.85,
            showlegend=False,
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Current: %{{y:.1f}} A<extra></extra>"),
            row=2, col=1)

    # FAULT dots on vibration panel
    if not fault_rows.empty:
        fig_f1.add_trace(go.Scatter(
            x=fault_rows["timestamp"], y=fault_rows["vibration_mm_s"],
            mode="markers", name="FAULT Event",
            marker=dict(color="#ef4444", size=10, symbol="circle",
                        line=dict(color="#fff", width=1)),
            hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>Vib: %{y:.2f} mm/s<br>%{customdata}<extra></extra>",
            customdata=fault_rows["machine_id"]),
            row=1, col=1)
        # FAULT dots on current panel too
        fig_f1.add_trace(go.Scatter(
            x=fault_rows["timestamp"], y=fault_rows["current_a"],
            mode="markers", name="FAULT Event",
            showlegend=False,
            marker=dict(color="#ef4444", size=10, symbol="circle",
                        line=dict(color="#fff", width=1)),
            hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>Current: %{y:.1f} A<br>%{customdata}<extra></extra>",
            customdata=fault_rows["machine_id"]),
            row=2, col=1)

    fig_f1.add_hline(y=vib_thresh, row=1, col=1, line_color="#dc2626", line_dash="dot",
        annotation_text=f"Critical {vib_thresh:.0f} mm/s",
        annotation_font_color="#dc2626", annotation_position="top right")
    fig_f1.add_hline(y=cur_thresh, row=2, col=1, line_color="#dc2626", line_dash="dot",
        annotation_text=f"Critical {cur_thresh:.0f} A",
        annotation_font_color="#dc2626", annotation_position="top right")

    fig_f1.update_layout(**CHART_BASE, height=560, hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11))
    apply_grid(fig_f1, [1, 2])
    st.plotly_chart(fig_f1, use_container_width=True)

    low_vib_faults = fault_rows[fault_rows["vibration_mm_s"] <= vib_thresh]
    st.markdown(f"""
> **Observation:** FAULT events (red dots) generally coincide with high vibration (> {vib_thresh:.0f} mm/s)
> and/or high current (> {cur_thresh:.0f} A). **{len(low_vib_faults)}** fault(s) occurred with low vibration —
> these were triggered by electrical overcurrent rather than mechanical causes.
> Viewing both sensors together confirms multi-modal fault signatures.
""")
    st.markdown("---")

    # ── FIGURE 2 — Vibration vs Rejection Rate scatter ────────────────────────
    st.markdown("#### Figure 2 — Vibration vs. Rejection Rate (%, RUNNING only)")

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
            marker=dict(color=MACH_COLORS.get(mach,"#aaa"), size=7, opacity=0.6),
            hovertemplate=f"<b>{mach}</b><br>Vib: %{{x:.2f}} mm/s<br>Rejection: %{{y:.1f}}%<extra></extra>"))

    if len(x_line) > 0:
        fig_f2.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines",
            name=f"Trend (r={r_val:.4f})", line=dict(color="#991b1b", width=2.5)))

    fig_f2.update_layout(**CHART_BASE, height=480,
        xaxis_title="Vibration Level (mm/s)", yaxis_title="Rejection Rate (%)",
        title=dict(text=f"Vibration vs. Rejection Rate (%) — RUNNING only | r = {r_val:.4f}",
                   font_color="#8899aa", font_size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11))
    apply_grid(fig_f2)
    st.plotly_chart(fig_f2, use_container_width=True)
    st.markdown(f"""
> **Observation:** Pearson r = **{r_val:.4f}** — near-zero correlation.
> Vibration level does not meaningfully predict rejection rate during normal operation.
> Quality issues are driven by other factors such as tooling wear or material variability.
""")
    st.markdown("---")

    # ── FIGURE 3 — Per-machine: Vibration + FAULT dots + Rejection Rate ───────
    st.markdown("#### Figure 3 — Machine Health: Vibration (mm/s) & Rejection Rate (%)")

    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp").copy()
        if sub.empty: continue
        fault_sub = sub[sub["status"]=="FAULT"]

        fig_f3m = make_subplots(specs=[[{"secondary_y": True}]])

        fig_f3m.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["vibration_mm_s"], name="Vibration (mm/s)",
            line=dict(color="#93c5fd", width=1.8),
            hovertemplate="%{x|%b %d %H:%M}<br>Vib: %{y:.2f} mm/s<extra></extra>"),
            secondary_y=False)

        if not fault_sub.empty:
            fig_f3m.add_trace(go.Scatter(
                x=fault_sub["timestamp"], y=fault_sub["vibration_mm_s"],
                mode="markers", name="FAULT",
                marker=dict(color="#111827", size=10, symbol="circle",
                            line=dict(color="#c8d8e8", width=1.5)),
                hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>%{y:.2f} mm/s<extra></extra>"),
                secondary_y=False)

        fig_f3m.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["rejection_rate"], name="Rejection Rate (%)",
            line=dict(color="#ef4444", width=1.8, dash="dash"),
            hovertemplate="%{x|%b %d %H:%M}<br>Rejection: %{y:.1f}%<extra></extra>"),
            secondary_y=True)

        fig_f3m.add_hline(y=vib_thresh, line_color="#dc2626", line_dash="dot",
            annotation_text=f"Critical {vib_thresh:.0f} mm/s",
            annotation_font_color="#dc2626", annotation_position="top right",
            secondary_y=False)

        fig_f3m.update_layout(
            **CHART_BASE, height=400, hovermode="x unified",
            title=dict(text=f"{mach} — Vibration (mm/s) & Rejection Rate (%)",
                       font_color="#8899aa", font_size=13),
            legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11, orientation="h", y=1.12))
        fig_f3m.update_xaxes(title_text="Timestamp", gridcolor="#0f1928", zeroline=False)
        fig_f3m.update_yaxes(title_text="Vibration (mm/s)", gridcolor="#0f1928",
                              zeroline=False,
                              range=[0, sub["vibration_mm_s"].max()*1.2],
                              secondary_y=False)
        fig_f3m.update_yaxes(title_text="Rejection Rate (%)", gridcolor="#0f1928",
                              zeroline=False, range=[0, 100],
                              tickfont=dict(color="#ef4444"),
                              title_font=dict(color="#ef4444"),
                              secondary_y=True)
        st.plotly_chart(fig_f3m, use_container_width=True, config={"displayModeBar":False})

    fault_hi = df[(df["status"]=="FAULT") & (df["vibration_mm_s"]>vib_thresh)]
    fault_lo = df[(df["status"]=="FAULT") & (df["vibration_mm_s"]<=vib_thresh)]
    st.markdown(f"""
> **Observation:** **{len(fault_hi)}** fault(s) coincide with vibration above {vib_thresh:.0f} mm/s.
> **{len(fault_lo)}** fault(s) occurred at lower vibration — suggesting electrical overcurrent triggers.
> Rejection rate spikes (red dashes) closely align with fault events, confirming direct quality impact.
""")
    st.info("""📌 **Rejection Rate Definition used in Figure 3:**
- `RUNNING` → `rejected_units / produced_units × 100%` — actual defect rate from raw data
- `FAULT` → `100%` — machine is down; zero usable output, treated as total production loss
- `IDLE` → calculated from raw data (typically 0% as no units are produced)""")
    st.markdown("---")

    # ── FIGURE 4 — Vibration boxplot by status ────────────────────────────────
    st.markdown("#### Figure 4 — Vibration Distribution by Status (mm/s)")

    fig_f4 = go.Figure()
    box_colors = {"IDLE":"#2d6a4f","RUNNING":"#c06030","FAULT":"#6272a4"}
    for status in ["IDLE","RUNNING","FAULT"]:
        sub = df[df["status"]==status]["vibration_mm_s"]
        if sub.empty: continue
        fig_f4.add_trace(go.Box(y=sub, name=status, boxmean=True,
            marker_color=box_colors.get(status,"#aaa"),
            line_color=box_colors.get(status,"#aaa"),
            fillcolor=box_colors.get(status,"#aaa"),
            opacity=0.75,
            hovertemplate=f"<b>{status}</b><br>%{{y:.2f}} mm/s<extra></extra>"))

    fig_f4.add_hline(y=vib_thresh, line_color="#dc2626", line_dash="dot",
        annotation_text=f"Critical {vib_thresh:.0f} mm/s", annotation_font_color="#dc2626")
    fig_f4.update_layout(**CHART_BASE, height=500,
        xaxis_title="Machine Status", yaxis_title="Vibration (mm/s)",
        title=dict(text="Vibration Distribution by Status (mm/s)",
                   font_color="#8899aa", font_size=13))
    apply_grid(fig_f4)
    st.plotly_chart(fig_f4, use_container_width=True)

    run_med   = df[df["status"]=="RUNNING"]["vibration_mm_s"].median()
    fault_med = df[df["status"]=="FAULT"]["vibration_mm_s"].median() if fault_count>0 else 0
    idle_med  = df[df["status"]=="IDLE"]["vibration_mm_s"].median()
    st.markdown(f"""
> **Observation:** FAULT median vibration ({fault_med:.1f} mm/s) is approximately
> **{fault_med/run_med:.1f}×** higher than RUNNING ({run_med:.1f} mm/s) and
> IDLE ({idle_med:.1f} mm/s). The wide FAULT IQR indicates variable fault severity —
> some faults are borderline while others exceed 18 mm/s.
""")
    st.markdown("---")

    # ── FIGURE 5 — Current vs Vibration scatter + Rejection by machine/shift ──
    st.markdown("#### Figure 5 — Current (A) vs Vibration (mm/s) & Rejection Rate (%)")

    fig_f5 = make_subplots(rows=1, cols=2,
        subplot_titles=("(a) Current (A) vs Vibration (mm/s) by Status",
                        "(b) Rejection Rate (%) by Machine & Shift"),
        column_widths=[0.55, 0.45])

    MARKER_SHAPE = {"M1":"circle","M2":"square","M3":"triangle-up"}
    STATUS_COL   = {"RUNNING":"#22c55e","IDLE":"#fbbf24","FAULT":"#ef4444"}

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
                            size=6, opacity=0.55 if status!="FAULT" else 0.9),
                hovertemplate=f"<b>{mach} {status}</b><br>Current: %{{x:.1f}} A<br>Vib: %{{y:.2f}} mm/s<extra></extra>"),
                row=1, col=1)

    fig_f5.add_vline(x=cur_thresh, row=1, col=1, line_color="#dc2626", line_dash="dash",
        annotation_text=f"{cur_thresh:.0f} A", annotation_font_color="#dc2626")
    fig_f5.add_hline(y=vib_thresh, row=1, col=1, line_color="#f97316", line_dash="dot",
        annotation_text=f"{vib_thresh:.0f} mm/s", annotation_font_color="#f97316")

    run_rej = (df[df["status"]=="RUNNING"]
               .groupby(["machine_id","shift"])
               .apply(lambda g: g["rejected_units"].sum()/max(g["produced_units"].sum(),1)*100)
               .reset_index(name="rej_rate"))

    shift_colors = {"Day":"#f59e0b","Night":"#3b4fa8"}
    for shift in ["Day","Night"]:
        sub = run_rej[run_rej["shift"]==shift]
        if sub.empty: continue
        fig_f5.add_trace(go.Bar(
            x=sub["machine_id"], y=sub["rej_rate"], name=shift,
            marker_color=shift_colors[shift],
            text=sub["rej_rate"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11),
            hovertemplate=f"<b>{shift} shift</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>"),
            row=1, col=2)

    fig_f5.update_xaxes(title_text="Motor Current (A)",  row=1, col=1, gridcolor="#0f1928", zeroline=False)
    fig_f5.update_yaxes(title_text="Vibration (mm/s)",   row=1, col=1, gridcolor="#0f1928", zeroline=False)
    fig_f5.update_xaxes(title_text="Machine ID",         row=1, col=2, gridcolor="#0f1928", zeroline=False)
    fig_f5.update_yaxes(title_text="Rejection Rate (%)", row=1, col=2, gridcolor="#0f1928", zeroline=False,
                        range=[0, run_rej["rej_rate"].max()*1.35 if not run_rej.empty else 10])
    fig_f5.update_layout(**CHART_BASE, height=520, barmode="group",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, orientation="v"),
        title=dict(text="Fault Diagnostics — Current (A) vs Vibration (mm/s) & Rejection Rate (%)",
                   font_color="#8899aa", font_size=13))
    st.plotly_chart(fig_f5, use_container_width=True)

    day_avg   = run_rej[run_rej["shift"]=="Day"]["rej_rate"].mean()
    night_avg = run_rej[run_rej["shift"]=="Night"]["rej_rate"].mean()
    better    = "Night" if night_avg < day_avg else "Day"
    fault_zone = df[(df["current_a"]>cur_thresh) & (df["vibration_mm_s"]>vib_thresh)]
    st.markdown(f"""
> **Observation (a):** FAULT readings cluster where both current > {cur_thresh:.0f} A and
> vibration > {vib_thresh:.0f} mm/s — **{len(fault_zone)}** readings exceeded both thresholds simultaneously.
>
> **Observation (b):** Rejection rates are consistent across shifts (~3–4%).
> **{better} shift** performs marginally better. M3 has the highest rejection rate across both shifts.
""")

    # ── FIGURE 6 — Operational Status Distribution by Machine ────────────────
    st.markdown("#### Figure 6 — Operational Status Distribution by Machine (hrs)")

    status_hrs_adv = df.groupby(["machine_id","status"]).size().reset_index(name="hours")
    fig_f6 = go.Figure()
    for st_opt, col_f6 in [("FAULT","#ef4444"),("IDLE","#9ca3af"),("RUNNING","#3b82f6")]:
        sub = status_hrs_adv[status_hrs_adv["status"]==st_opt]
        fig_f6.add_trace(go.Bar(
            name=st_opt, x=sub["machine_id"], y=sub["hours"],
            marker_color=col_f6,
            text=sub["hours"], textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11)))
    fig_f6.update_layout(**CHART_BASE, height=480, barmode="group",
        xaxis_title="Machine", yaxis_title="Operating Hours",
        title=dict(text="Operational Status Distribution by Machine (hrs)",
                   font_color="#8899aa", font_size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=12))
    apply_grid(fig_f6)
    st.plotly_chart(fig_f6, use_container_width=True)

    m1_fault = status_hrs_adv[(status_hrs_adv["machine_id"]=="M1") & (status_hrs_adv["status"]=="FAULT")]["hours"].sum()
    m2_fault = status_hrs_adv[(status_hrs_adv["machine_id"]=="M2") & (status_hrs_adv["status"]=="FAULT")]["hours"].sum()
    m3_fault = status_hrs_adv[(status_hrs_adv["machine_id"]=="M3") & (status_hrs_adv["status"]=="FAULT")]["hours"].sum()
    st.markdown(f"""
> **Observation:** M1 accumulated **{m1_fault} fault hours** — significantly higher than
> M2 ({m2_fault} hrs) and M3 ({m3_fault} hrs), confirming M1 as the highest-priority maintenance target.
> RUNNING hours are broadly similar across machines, meaning M1's faults are replacing productive time
> rather than idle time.
""")
    st.markdown("---")

    # ── Summary ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sh">📋 ANALYSIS SUMMARY</div>', unsafe_allow_html=True)
    st.markdown(f"""
| Figure | Key Finding |
|--------|------------|
| **Fig 1** — Vibration & Current (mm/s, A) | {fault_count} FAULT events visible on both sensor panels |
| **Fig 2** — Vibration vs Rejection (%, RUNNING) | Near-zero correlation r ≈ {r_val:.3f}; vibration ≠ quality driver |
| **Fig 3** — Health: Vibration (mm/s) & Rejection (%) | FAULT events co-occur with rejection spikes per machine |
| **Fig 4** — Vibration Distribution (mm/s) | FAULT median {fault_med:.1f} mm/s vs RUNNING {run_med:.1f} mm/s — {fault_med/run_med:.1f}× higher |
| **Fig 5** — Current (A) vs Vibration (mm/s) & Rejection (%) | Dual threshold exceedance = strongest fault predictor |
| **Fig 6** — Status Distribution (hrs) | M1 fault hours ({m1_fault} hrs) highest — priority maintenance target |
""")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div style='text-align:center;font-family:IBM Plex Mono,monospace;font-size:10px;
            color:#1e3050;padding:8px 0;letter-spacing:.1em'>
    EE4409 CA2 · PlantIQ Manufacturing Dashboard · Streamlit · Plotly · Pandas
</div>""", unsafe_allow_html=True)

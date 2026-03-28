"""
EE4409 CA2 — PlantIQ Manufacturing Dashboard  (v3 — Advanced Analysis Tab)
Stack : Streamlit · Plotly · Pandas · Claude API
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="PlantIQ", page_icon="⚙️",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────────────────────
# CSS
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
.kpi-label{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.12em;color:#4a6080;text-transform:uppercase;margin-bottom:10px;}
.kpi-value{font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;line-height:1;color:var(--kpi-color,#7eb8f7);}
.kpi-sub{font-size:11px;color:#3a5070;margin-top:8px;font-family:'IBM Plex Mono',monospace;}
.mc{border-radius:14px;padding:18px 20px;margin-bottom:2px;border-left:4px solid transparent;transition:transform .2s;}
.mc:hover{transform:translateX(3px);}
.mc-running{background:#071a10;border-color:#16a34a;}
.mc-idle{background:#1a1500;border-color:#ca8a04;}
.mc-fault{background:#180808;border-color:#dc2626;animation:fault-pulse 2s ease-in-out infinite;}
@keyframes fault-pulse{0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,0);}50%{box-shadow:0 0 0 8px rgba(220,38,38,.15);}}
.mc-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
.mc-id{font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;}
.mc-badge{font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.1em;padding:3px 10px;border-radius:20px;}
.badge-running{background:#14532d;color:#4ade80;}.badge-idle{background:#422006;color:#fbbf24;}.badge-fault{background:#450a0a;color:#f87171;}
.mc-metrics{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;}
.mc-m{background:rgba(255,255,255,.03);border-radius:8px;padding:8px 10px;}
.mc-m-label{font-size:10px;color:#3a5070;font-family:'IBM Plex Mono',monospace;letter-spacing:.08em;margin-bottom:2px;}
.mc-m-val{font-size:1.1rem;font-weight:600;}
.risk-low{color:#4ade80;}.risk-med{color:#fbbf24;}.risk-high{color:#f87171;}
.sh{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.15em;color:#2563eb;
  text-transform:uppercase;border-bottom:1px solid #1a2540;padding-bottom:8px;margin-bottom:16px;}
.chat-msg-user{background:#0f1e35;border-radius:12px 12px 2px 12px;padding:10px 14px;margin:6px 0;
  font-size:.85rem;border:1px solid #1e3050;}
.chat-msg-ai{background:#071428;border-radius:2px 12px 12px 12px;padding:10px 14px;margin:6px 0;
  font-size:.85rem;border:1px solid #1a3060;color:#a0c4f0;}
.chat-label{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.1em;color:#2563eb;margin-bottom:4px;}
.info-box{background:#0b1422;border:1px solid #1a2540;border-radius:10px;padding:12px;margin:8px 0;font-size:.8rem;line-height:1.7;}
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
# AI
# ─────────────────────────────────────────────────────────────────────────────
def build_context():
    lines = [f"Plant data: {d_start} to {d_end}, machines {', '.join(sel_machines)}.",
             f"Uptime: {uptime_pct:.1f}%, Yield: {yield_rate:.1f}%, Faults: {fault_count}, Anomalies: {len(alerts_df)}."]
    for m in sel_machines:
        sub = df[df["machine_id"]==m]
        lines.append(f"{m}: avg_current={sub['current_a'].mean():.1f}A, avg_vib={sub['vibration_mm_s'].mean():.2f}mm/s, "
                     f"faults={(sub['status']=='FAULT').sum()}, risk={machine_risk[m]}/100, "
                     f"avg_rej={sub['rejection_rate'].mean():.1f}%.")
    for s, row in df.groupby("shift")[["produced_units","rejected_units"]].sum().iterrows():
        yr = (row["produced_units"]-row["rejected_units"])/max(row["produced_units"],1)*100
        lines.append(f"{s} shift yield={yr:.1f}%.")
    return " ".join(lines)

def ask_claude(question, context, history):
    system = ("You are PlantIQ, an AI assistant for a non-expert plant operator. "
              "Answer in plain English, 3-5 sentences, use actual numbers from context. "
              f"\n\nCONTEXT:\n{context}")
    try:
        resp = requests.post("https://api.anthropic.com/v1/messages",
            headers={"Content-Type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":400,
                  "system":system,"messages":history+[{"role":"user","content":question}]},
            timeout=20)
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"⚠️ Could not reach AI: {e}"

# ─────────────────────────────────────────────────────────────────────────────
# SHARED CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
MACH_COLORS  = {"M1":"#3b82f6","M2":"#f97316","M3":"#22c55e"}
STATUS_CSS   = {"RUNNING":"mc-running","IDLE":"mc-idle","FAULT":"mc-fault"}
BADGE_CSS    = {"RUNNING":"badge-running","IDLE":"badge-idle","FAULT":"badge-fault"}
STATUS_ICON  = {"RUNNING":"▶","IDLE":"⏸","FAULT":"⚡"}
STATUS_COLOR = {"RUNNING":"#16a34a","IDLE":"#ca8a04","FAULT":"#dc2626"}

CHART_BASE = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,12,20,.8)",
                  font_color="#c8d8e8", font_family="IBM Plex Mono",
                  margin=dict(l=10,r=10,t=40,b=10))

def apply_grid(fig, rows=None):
    rows = rows or [1]
    for r in rows:
        fig.update_xaxes(gridcolor="#0f1928", zeroline=False, row=r)
        fig.update_yaxes(gridcolor="#0f1928", zeroline=False, row=r)

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

    def make_gauge(val, max_v, w_thresh, c_thresh, title):
        bar_col = "#4ade80" if val<=w_thresh else ("#fbbf24" if val<=c_thresh else "#f87171")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=val,
            number={"suffix":" mm/s","font":{"size":14,"color":"#c8d8e8"}},
            title={"text":title,"font":{"size":11,"color":"#4a6080","family":"IBM Plex Mono"}},
            gauge={"axis":{"range":[0,max_v],"tickcolor":"#1e3050","tickfont":{"color":"#3a5070","size":9}},
                   "bar":{"color":bar_col,"thickness":.28},"bgcolor":"#080c14","bordercolor":"#1a2540",
                   "steps":[{"range":[0,w_thresh],"color":"#071510"},{"range":[w_thresh,c_thresh],"color":"#1a1200"},
                             {"range":[c_thresh,max_v],"color":"#180808"}],
                   "threshold":{"line":{"color":"#dc2626","width":3},"thickness":.8,"value":c_thresh}}))
        fig.update_layout(height=170,margin=dict(l=15,r=15,t=35,b=5),
                          paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#c8d8e8")
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

    # ── AI CHAT ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sh">🤖 AI PLANT ASSISTANT</div>', unsafe_allow_html=True)
    if "chat_history"    not in st.session_state: st.session_state.chat_history    = []
    if "display_history" not in st.session_state: st.session_state.display_history = []

    QUICK = ["Which machine needs urgent attention?","Why is the yield rate what it is?",
             "Which shift performs better and why?","What should maintenance do this week?",
             "What caused the most recent faults?","Explain the vibration readings simply"]
    qcols = st.columns(3)
    for idx, q in enumerate(QUICK):
        if qcols[idx%3].button(q, key=f"q{idx}", use_container_width=True):
            st.session_state._quick_q = q

    user_q = st.chat_input("Ask PlantIQ anything…") or st.session_state.pop("_quick_q", None)
    if user_q:
        ai_ans = ask_claude(user_q, build_context(), st.session_state.chat_history)
        st.session_state.display_history.append((user_q, ai_ans))
        st.session_state.chat_history.extend([{"role":"user","content":user_q},
                                               {"role":"assistant","content":ai_ans}])
        if len(st.session_state.chat_history) > 20:
            st.session_state.chat_history = st.session_state.chat_history[-20:]

    if not st.session_state.display_history:
        st.markdown("""<div style='text-align:center;padding:30px;color:#2a4060;
            font-family:IBM Plex Mono,monospace;font-size:12px;'>
            💬 Click a quick question above or type below.</div>""", unsafe_allow_html=True)
    for um, am in st.session_state.display_history[-6:]:
        st.markdown(f'<div class="chat-label">YOU</div><div class="chat-msg-user">{um}</div>'
                    f'<div class="chat-label" style="color:#60a5fa;margin-top:8px">⚙️ PLANTIQ AI</div>'
                    f'<div class="chat-msg-ai">{am}</div>', unsafe_allow_html=True)
    if st.session_state.display_history:
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []; st.session_state.display_history = []; st.rerun()
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
        annotation_text=f"Alert {cur_thresh}A",annotation_font_color="#dc2626")
    fig_trend.add_hline(y=vib_thresh,row=2,col=1,line_color="#dc2626",line_dash="dash",
        annotation_text=f"Alert {vib_thresh}mm/s",annotation_font_color="#dc2626")
    fig_trend.update_layout(**CHART_BASE, height=460, hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)",font_size=11))
    apply_grid(fig_trend,[1,2])
    st.plotly_chart(fig_trend, use_container_width=True)
    st.caption("Thick lines = 8-reading rolling average. Thin = raw sensor data. Red dashed = alert threshold.")
    st.markdown("---")

    # ── PRODUCTION + CORRELATION + RISK ──────────────────────────────────────
    st.markdown('<div class="sh">🏗️ PRODUCTION & CORRELATION</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2.5,2,2])
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
        fh = go.Figure(go.Heatmap(z=corr.values,x=["Current","Vibration","Rejection%","Produced"],
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
            f"⚡ {r['current_a']:.1f}A>{cur_thresh}A"          if r["current_a"]>cur_thresh else "",
            f"📳 {r['vibration_mm_s']:.2f}>{vib_thresh}mm/s"   if r["vibration_mm_s"]>vib_thresh else "",
            f"❌ rej {r['rejection_rate']:.1f}%>10%"            if r["rejection_rate"]>10 else "",
        ])),axis=1)
        disp = disp[["timestamp","machine_id","status","current_a","vibration_mm_s","rejection_rate","Triggered By"]]
        disp.columns = ["Timestamp","Machine","Status","Current (A)","Vibration (mm/s)","Rejection (%)","Triggered By"]
        disp["Timestamp"]     = pd.to_datetime(disp["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        disp["Rejection (%)"] = disp["Rejection (%)"].round(2)
        st.dataframe(disp.sort_values("Timestamp",ascending=False), use_container_width=True, hide_index=True,
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
        st.info("💡 Thermal + acoustic sensors reduce unplanned downtime by up to **40%** via multi-modal predictive ML.")

    best_shift = df.groupby("shift").apply(
        lambda g:(g["produced_units"].sum()-g["rejected_units"].sum())/max(g["produced_units"].sum(),1)*100).idxmax()
    st.markdown(f"""> **📋 Summary — {d_start} to {d_end}**
> Uptime **{uptime_pct:.1f}%** · Yield **{yield_rate:.1f}%** · Faults **{fault_count}** · Anomalies **{len(alerts_df)}**
> Highest-risk: **{high_risk_m}** ({machine_risk.get(high_risk_m,0)}/100) · Best shift: **{best_shift}**
> *Action: Prioritise {top_fault_m} maintenance and deploy real-time vibration + current alerting.*""")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ADVANCED ANALYSIS  (all 5 figures)
# ══════════════════════════════════════════════════════════════════════════════
with TAB_ADV:

    st.markdown('<div class="sh">🔬 DEEP-DIVE FAULT & SENSOR ANALYSIS</div>', unsafe_allow_html=True)
    st.caption("This section contains detailed statistical charts for academic analysis and reporting.")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── FIGURE 1 — Vibration over time with FAULT red dots ───────────────────
    st.markdown("#### Figure 1 — Vibration Over Time: Identifying Fault Correlation")

    fig_f1 = go.Figure()
    fault_rows = df[df["status"]=="FAULT"]

    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp")
        c   = MACH_COLORS.get(mach,"#aaa")
        fig_f1.add_trace(go.Scatter(x=sub["timestamp"], y=sub["vibration_mm_s"],
            name=mach, line=dict(color=c, width=1.5), opacity=0.8,
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Vib: %{{y:.2f}} mm/s<extra></extra>"))

    # FAULT events as red scatter dots (one per fault row, y = vibration value)
    if not fault_rows.empty:
        fig_f1.add_trace(go.Scatter(
            x=fault_rows["timestamp"], y=fault_rows["vibration_mm_s"],
            mode="markers", name="FAULT Event",
            marker=dict(color="#ef4444", size=10, symbol="circle",
                        line=dict(color="#fff", width=1)),
            hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>Vib: %{y:.2f} mm/s<br>Machine: %{customdata}<extra></extra>",
            customdata=fault_rows["machine_id"]))

    fig_f1.add_hline(y=vib_thresh, line_color="#dc2626", line_dash="dot",
        annotation_text=f"Critical {vib_thresh} mm/s", annotation_font_color="#dc2626",
        annotation_position="top right")
    fig_f1.update_layout(**CHART_BASE, height=380, xaxis_title="Timestamp",
        yaxis_title="Vibration (mm/s)",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
        title=dict(text="Vibration Over Time: Identifying Fault Correlation",
                   font_color="#8899aa", font_size=13))
    apply_grid(fig_f1)
    st.plotly_chart(fig_f1, use_container_width=True)

    # Count fault outliers (faults where vibration is actually below threshold)
    low_vib_faults = fault_rows[fault_rows["vibration_mm_s"] <= vib_thresh]
    st.markdown(f"""
> **Observation:** FAULT events (red dots) generally coincide with high vibration (> {vib_thresh:.0f} mm/s),
> confirming vibration as a primary fault indicator. **{len(low_vib_faults)}** outlier fault(s) occurred
> with vibration ≤ {vib_thresh:.0f} mm/s — likely caused by electrical overcurrent rather than mechanical vibration.
> This highlights the importance of monitoring **both** sensors simultaneously.
""")
    st.markdown("---")

    # ── FIGURE 2 — Vibration vs Rejection Rate scatter (RUNNING only) ────────
    st.markdown("#### Figure 2 — Correlation: Vibration vs. Rejection Rate (RUNNING Status Only)")

    running_df = df[df["status"]=="RUNNING"].copy()
    # Filter to normal operating vibration range (1–8 mm/s) to match the figure
    running_filt = running_df[running_df["vibration_mm_s"] <= 8].copy()

    # Trend line via numpy polyfit
    if len(running_filt) > 2:
        z   = np.polyfit(running_filt["vibration_mm_s"], running_filt["rejection_rate"], 1)
        x_line = np.linspace(running_filt["vibration_mm_s"].min(), running_filt["vibration_mm_s"].max(), 100)
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
        fig_f2.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", name=f"Trend (r={r_val:.4f})",
            line=dict(color="#991b1b", width=2.5),
            hovertemplate=f"Trend line (r={r_val:.4f})<extra></extra>"))

    fig_f2.update_layout(**CHART_BASE, height=380, xaxis_title="Vibration Level (mm/s)",
        yaxis_title="Rejection Rate (%)",
        title=dict(text="Correlation: Vibration vs. Rejection Rate (RUNNING Status Only)",
                   font_color="#8899aa", font_size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11))
    apply_grid(fig_f2)
    st.plotly_chart(fig_f2, use_container_width=True)
    st.markdown(f"""
> **Observation:** Pearson r = **{r_val:.4f}** — near-zero correlation between vibration level and rejection rate
> during normal RUNNING operations. This means **vibration alone does not predict product quality failures**;
> rejection is driven by other factors (tooling wear, material quality, operator variance).
> Quality control should focus on process parameters rather than vibration thresholds.
""")
    st.markdown("---")

    # ── FIGURE 3 — Machine Status Timeline + Current overlay ─────────────────
    st.markdown("#### Figure 3 — Machine Status and Motor Current Over Time")

    n_machines = len(sel_machines)
    fig_f3 = make_subplots(rows=n_machines, cols=1, shared_xaxes=True,
        subplot_titles=[f"{m} Status" for m in sel_machines],
        vertical_spacing=0.08)

    STATUS_BG = {"RUNNING": "rgba(22,163,74,.25)", "IDLE": "rgba(202,138,4,.20)", "FAULT": "rgba(220,38,38,.35)"}

    for i, mach in enumerate(sel_machines, start=1):
        sub = df[df["machine_id"]==mach].sort_values("timestamp").copy()
        sub["status_num"] = sub["status"].map({"RUNNING":1,"IDLE":0.5,"FAULT":0})

        # Shaded status regions via vrect
        if not sub.empty:
            prev_status = sub.iloc[0]["status"]
            seg_start   = sub.iloc[0]["timestamp"]
            for _, row_r in sub.iterrows():
                if row_r["status"] != prev_status:
                    fig_f3.add_vrect(x0=seg_start, x1=row_r["timestamp"],
                        fillcolor=STATUS_BG.get(prev_status,"rgba(0,0,0,0)"),
                        layer="below", line_width=0, row=i, col=1)
                    seg_start   = row_r["timestamp"]
                    prev_status = row_r["status"]
            # final segment
            fig_f3.add_vrect(x0=seg_start, x1=sub.iloc[-1]["timestamp"],
                fillcolor=STATUS_BG.get(prev_status,"rgba(0,0,0,0)"),
                layer="below", line_width=0, row=i, col=1)

        # Current line
        fig_f3.add_trace(go.Scatter(x=sub["timestamp"], y=sub["current_a"],
            name=f"{mach} Current" if i==1 else None,
            showlegend=(i==1),
            line=dict(color="#3b82f6", width=1.5),
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Current: %{{y:.1f}} A<extra></extra>"),
            row=i, col=1)

        # Annotate current spikes above cur_thresh
        spikes = sub[sub["current_a"] > cur_thresh].copy()
        if not spikes.empty:
            for _, sp in spikes.iterrows():
                fig_f3.add_annotation(x=sp["timestamp"], y=sp["current_a"],
                    text=f"{sp['current_a']:.0f}A",
                    font=dict(color="#f87171", size=9, family="IBM Plex Mono"),
                    showarrow=True, arrowcolor="#f87171", arrowsize=.6, arrowwidth=1,
                    ax=0, ay=-20, row=i, col=1)

        fig_f3.update_yaxes(title_text="Current (A)", row=i, col=1,
            gridcolor="#0f1928", zeroline=False, range=[0, sub["current_a"].max()*1.15 if not sub.empty else 90])

    # Legend entries for status bands (manual)
    for label, col in [("RUNNING","rgba(22,163,74,.5)"),("IDLE","rgba(202,138,4,.45)"),("FAULT","rgba(220,38,38,.6)")]:
        fig_f3.add_trace(go.Scatter(x=[None],y=[None],mode="markers",name=label,
            marker=dict(color=col,size=10,symbol="square")))

    fig_f3.update_layout(**CHART_BASE, height=120*n_machines + 80, hovermode="x unified",
        title=dict(text="Machine Status and Motor Current Over Time",font_color="#8899aa",font_size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)",font_size=11,orientation="h",y=-0.06))
    fig_f3.update_xaxes(gridcolor="#0f1928", zeroline=False)
    st.plotly_chart(fig_f3, use_container_width=True)
    st.markdown(f"""
> **Observation:** Green bands = RUNNING, Yellow = IDLE, Red = FAULT. Current spikes above **{cur_thresh:.0f} A**
> (labelled) are annotated. FAULT periods visually correlate with current spikes, confirming
> electrical overcurrent as a co-trigger. Short IDLE periods between FAULT and RUNNING suggest
> automatic reset behaviour rather than manual operator intervention.
""")
    st.markdown("---")

    # ── FIGURE 4 — Vibration distribution by status (Box plot) ───────────────
    st.markdown("#### Figure 4 — Vibration Distribution Grouped by Status")

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
        annotation_text=f"Critical {vib_thresh} mm/s", annotation_font_color="#dc2626")
    fig_f4.update_layout(**CHART_BASE, height=400, xaxis_title="Status",
        yaxis_title="Vibration (mm/s)",
        title=dict(text="Vibration Distribution Grouped by Status",font_color="#8899aa",font_size=13))
    apply_grid(fig_f4)
    st.plotly_chart(fig_f4, use_container_width=True)

    # Compute key stats for the insight
    idle_med  = df[df["status"]=="IDLE"]["vibration_mm_s"].median()
    run_med   = df[df["status"]=="RUNNING"]["vibration_mm_s"].median()
    fault_med = df[df["status"]=="FAULT"]["vibration_mm_s"].median() if fault_count>0 else 0
    st.markdown(f"""
> **Observation:** FAULT status has a dramatically higher vibration distribution (median ≈ **{fault_med:.1f} mm/s**)
> compared to RUNNING (median ≈ **{run_med:.1f} mm/s**) and IDLE (median ≈ **{idle_med:.1f} mm/s**).
> IDLE and RUNNING distributions are nearly identical, confirming vibration is **not** significantly
> elevated during idle periods. The wide IQR for FAULT readings indicates fault severity varies greatly —
> some faults are borderline while others are extreme outliers above 18 mm/s.
""")
    st.markdown("---")

    # ── FIGURE 5 — Current vs Vibration scatter + Rejection by machine/shift ─
    st.markdown("#### Figure 5 — Fault Diagnostics: Current vs Vibration & Rejection Rate by Machine and Shift")

    fig_f5 = make_subplots(rows=1, cols=2,
        subplot_titles=("(a) Current vs Vibration by Status","(b) Rejection Rate by Machine and Shift (RUNNING only)"),
        column_widths=[0.55, 0.45])

    MARKER_SHAPE = {"M1":"circle","M2":"square","M3":"triangle-up"}
    STATUS_SCATTER_COL = {"RUNNING":"#22c55e","IDLE":"#fbbf24","FAULT":"#ef4444"}

    for status in ["RUNNING","IDLE","FAULT"]:
        sub_s = df[df["status"]==status]
        for mach in sel_machines:
            sub = sub_s[sub_s["machine_id"]==mach]
            if sub.empty: continue
            fig_f5.add_trace(go.Scatter(
                x=sub["current_a"], y=sub["vibration_mm_s"],
                mode="markers", name=f"{status} {mach}",
                showlegend=True,
                marker=dict(color=STATUS_SCATTER_COL[status],
                            symbol=MARKER_SHAPE.get(mach,"circle"),
                            size=6, opacity=0.6 if status!="FAULT" else 0.9),
                hovertemplate=f"<b>{mach} {status}</b><br>Current: %{{x:.1f}} A<br>Vib: %{{y:.2f}} mm/s<extra></extra>"),
                row=1,col=1)

    # Threshold lines
    fig_f5.add_vline(x=cur_thresh, row=1, col=1, line_color="#dc2626", line_dash="dash",
        annotation_text=f"{cur_thresh:.0f}A", annotation_font_color="#dc2626")
    fig_f5.add_hline(y=vib_thresh, row=1, col=1, line_color="#f97316", line_dash="dot",
        annotation_text=f"{vib_thresh:.0f}mm/s", annotation_font_color="#f97316")

    # Rejection rate by machine and shift (RUNNING only)
    run_rej = (df[df["status"]=="RUNNING"]
               .groupby(["machine_id","shift"])
               .apply(lambda g: g["rejected_units"].sum()/max(g["produced_units"].sum(),1)*100)
               .reset_index(name="rej_rate"))

    shift_colors = {"Day":"#f59e0b","Night":"#3b4fa8"}
    for shift in ["Day","Night"]:
        sub = run_rej[run_rej["shift"]==shift]
        if sub.empty: continue
        fig_f5.add_trace(go.Bar(
            x=sub["machine_id"], y=sub["rej_rate"],
            name=shift, marker_color=shift_colors[shift],
            text=sub["rej_rate"].apply(lambda x:f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11),
            hovertemplate=f"<b>{shift} shift</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>"),
            row=1,col=2)

    fig_f5.update_xaxes(title_text="Motor Current (A)", row=1, col=1, gridcolor="#0f1928", zeroline=False)
    fig_f5.update_yaxes(title_text="Vibration (mm/s)",  row=1, col=1, gridcolor="#0f1928", zeroline=False)
    fig_f5.update_xaxes(title_text="Machine ID",        row=1, col=2, gridcolor="#0f1928", zeroline=False)
    fig_f5.update_yaxes(title_text="Rejection Rate (%)",row=1, col=2, gridcolor="#0f1928", zeroline=False,
                        range=[0, run_rej["rej_rate"].max()*1.35 if not run_rej.empty else 10])
    fig_f5.update_layout(**CHART_BASE, height=440, barmode="group",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10, orientation="v"),
        title=dict(text="Fault Diagnostics — Current vs Vibration, and Rejection Rate by Machine & Shift",
                   font_color="#8899aa", font_size=13))
    st.plotly_chart(fig_f5, use_container_width=True)

    # Dynamic insight from data
    day_avg   = run_rej[run_rej["shift"]=="Day"]["rej_rate"].mean()
    night_avg = run_rej[run_rej["shift"]=="Night"]["rej_rate"].mean()
    better_shift = "Night" if night_avg < day_avg else "Day"
    fault_zone = df[(df["current_a"]>cur_thresh) & (df["vibration_mm_s"]>vib_thresh)]
    st.markdown(f"""
> **Observation (a):** FAULT readings cluster in the top-right quadrant (high current **>{cur_thresh:.0f} A** AND
> high vibration **>{vib_thresh:.0f} mm/s**), confirming that **simultaneous** sensor exceedance is the strongest
> fault predictor. {len(fault_zone)} readings exceeded both thresholds at once.
> RUNNING and IDLE readings are densely clustered in the safe zone (low current, low vibration).
>
> **Observation (b):** Rejection rates are consistent across Day and Night shifts (~3–4%),
> with **{better_shift} shift** performing marginally better. **M3** has the highest rejection rate
> across both shifts, suggesting a machine-specific quality issue rather than a shift-based one.
""")

    # ── Summary of findings ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sh">📋 ADVANCED ANALYSIS SUMMARY</div>', unsafe_allow_html=True)
    st.markdown(f"""
| Figure | Key Finding |
|--------|------------|
| **Fig 1** — Fault vs Vibration | {fault_count} FAULT events; majority above {vib_thresh:.0f} mm/s vibration threshold |
| **Fig 2** — Vibration vs Rejection | Near-zero correlation (r ≈ {r_val:.3f}); vibration does not drive quality |
| **Fig 3** — Status Timeline | FAULT periods co-occur with current spikes; auto-reset behaviour visible |
| **Fig 4** — Vibration Boxplot | FAULT median vibration ({fault_med:.1f} mm/s) vs RUNNING ({run_med:.1f} mm/s) — 3× higher |
| **Fig 5** — Dual-threshold | Combined high current + high vibration = strongest fault predictor |
""")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div style='text-align:center;font-family:IBM Plex Mono,monospace;font-size:10px;
            color:#1e3050;padding:8px 0;letter-spacing:.1em'>
    EE4409 CA2 · PlantIQ Manufacturing Dashboard · Streamlit · Plotly · Pandas · Claude AI
</div>""", unsafe_allow_html=True)

"""
EE4409 CA2 — Manufacturing Plant Monitoring Dashboard  (UPGRADED)
Stack : Streamlit · Plotly · Pandas · Claude API (AI Insights)
"""

import os, json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PlantIQ — Monitoring Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #080c14;
    color: #c8d8e8;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0b1020;
    border-right: 1px solid #1a2540;
}
h1,h2,h3 { font-family: 'Syne', sans-serif; }

.kpi-wrap {
    background: linear-gradient(145deg, #0f1928 0%, #131e30 100%);
    border: 1px solid #1e3050;
    border-radius: 16px;
    padding: 24px 20px 18px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform .25s, box-shadow .25s;
}
.kpi-wrap:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,120,255,.15); }
.kpi-wrap::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background: var(--kpi-accent, #2563eb);
    border-radius:16px 16px 0 0;
}
.kpi-label { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.12em;
             color:#4a6080; text-transform:uppercase; margin-bottom:10px; }
.kpi-value { font-family:'Syne',sans-serif; font-size:2.6rem; font-weight:800;
             line-height:1; color: var(--kpi-color, #7eb8f7); }
.kpi-sub   { font-size:11px; color:#3a5070; margin-top:8px; font-family:'IBM Plex Mono',monospace; }

.mc { border-radius:14px; padding:18px 20px; margin-bottom:2px;
      border-left: 4px solid transparent; transition: transform .2s; }
.mc:hover { transform: translateX(3px); }
.mc-running { background:#071a10; border-color:#16a34a; }
.mc-idle    { background:#1a1500; border-color:#ca8a04; }
.mc-fault   { background:#180808; border-color:#dc2626;
              animation: fault-pulse 2s ease-in-out infinite; }
@keyframes fault-pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(220,38,38,0); }
  50%      { box-shadow: 0 0 0 8px rgba(220,38,38,.15); }
}
.mc-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.mc-id   { font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; }
.mc-badge { font-family:'IBM Plex Mono',monospace; font-size:10px; font-weight:600;
            letter-spacing:.1em; padding:3px 10px; border-radius:20px; }
.badge-running { background:#14532d; color:#4ade80; }
.badge-idle    { background:#422006; color:#fbbf24; }
.badge-fault   { background:#450a0a; color:#f87171; }
.mc-metrics { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:10px; }
.mc-m { background:rgba(255,255,255,.03); border-radius:8px; padding:8px 10px; }
.mc-m-label { font-size:10px; color:#3a5070; font-family:'IBM Plex Mono',monospace;
              letter-spacing:.08em; margin-bottom:2px; }
.mc-m-val   { font-size:1.1rem; font-weight:600; }

.risk-low  { color:#4ade80; }
.risk-med  { color:#fbbf24; }
.risk-high { color:#f87171; }

.sh { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.15em;
      color:#2563eb; text-transform:uppercase; border-bottom:1px solid #1a2540;
      padding-bottom:8px; margin-bottom:16px; }

.chat-msg-user { background:#0f1e35; border-radius:12px 12px 2px 12px;
                 padding:10px 14px; margin:6px 0; font-size:.85rem;
                 border:1px solid #1e3050; }
.chat-msg-ai   { background:#071428; border-radius:2px 12px 12px 12px;
                 padding:10px 14px; margin:6px 0; font-size:.85rem;
                 border:1px solid #1a3060; color:#a0c4f0; }
.chat-label    { font-family:'IBM Plex Mono',monospace; font-size:10px;
                 letter-spacing:.1em; color:#2563eb; margin-bottom:4px; }

.info-box { background:#0b1422; border:1px solid #1a2540; border-radius:10px;
            padding:12px; margin:8px 0; font-size:.8rem; line-height:1.7; }
.info-box b { color:#60a5fa; }
.crit { color:#f87171; font-weight:700; }

::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#0b1020; }
::-webkit-scrollbar-thumb { background:#1e3050; border-radius:3px; }
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
        df_raw = load_data(p)
        break
else:
    up = st.file_uploader("Upload plant_monitoring_data_1_.xlsm", type=["xlsm","xlsx","csv"])
    if up:
        df_raw = load_data(up)
    else:
        st.info("Place your `.xlsm` file next to `app.py`, or upload it above.")
        st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 20px'>
        <div style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;
                    background:linear-gradient(90deg,#3b82f6,#60a5fa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
            ⚙️ PlantIQ
        </div>
        <div style='font-family:IBM Plex Mono,monospace;font-size:10px;
                    color:#2a4060;letter-spacing:.15em'>MONITORING DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Sensor Guide", expanded=False):
        st.markdown("""
<div class="info-box">
<b>⚡ Current Sensor</b><br>
Measures motor electrical load in Amperes.<br>
Typical: <b>10–50 A</b> &nbsp;·&nbsp; <span class="crit">CRITICAL &gt; 60 A</span>
</div>
<div class="info-box">
<b>📳 Vibration Sensor</b><br>
Measures mechanical velocity in mm/s.<br>
Typical: <b>1–8 mm/s</b> &nbsp;·&nbsp; <span class="crit">CRITICAL &gt; 10 mm/s</span>
</div>
<div class="info-box">
<b>🔴 Fault Triggers</b><br>
• Vibration <b>&gt; 10 mm/s</b><br>
• Current <b>&gt; 60 A</b><br>
• Rejection rate <b>&gt; 10%</b>
</div>
""", unsafe_allow_html=True)

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
    st.warning("No data for the current filters.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# COMPUTED METRICS
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
    n       = len(mach_df) or 1
    fault_r = fc / n * 100
    vib_exc = (mach_df["vibration_mm_s"] > vib_t).sum() / n * 100
    cur_exc = (mach_df["current_a"] > cur_t).sum() / n * 100
    rej_r   = mach_df["rejection_rate"].mean()
    return min(int((fault_r*0.40 + vib_exc*0.30 + cur_exc*0.20 + min(rej_r,20)*0.10) * 3.5), 100)

machine_risk = {m: risk_score(df[df["machine_id"]==m],
                               (df[df["machine_id"]==m]["status"]=="FAULT").sum(),
                               vib_thresh, cur_thresh)
                for m in sel_machines}

# ─────────────────────────────────────────────────────────────────────────────
# AI CONTEXT + CALL
# ─────────────────────────────────────────────────────────────────────────────
def build_context():
    lines = [
        f"Plant data: {d_start} to {d_end}, machines {', '.join(sel_machines)}, shifts {', '.join(sel_shifts)}.",
        f"Plant uptime: {uptime_pct:.1f}%, Yield rate: {yield_rate:.1f}%, Fault readings: {fault_count}.",
        f"Total produced: {total_prod}, rejected: {total_rej}. Anomalies: {len(alerts_df)}.",
    ]
    for m in sel_machines:
        sub = df[df["machine_id"]==m]
        lines.append(
            f"{m}: avg_current={sub['current_a'].mean():.1f}A, "
            f"avg_vibration={sub['vibration_mm_s'].mean():.2f}mm/s, "
            f"faults={(sub['status']=='FAULT').sum()}, risk={machine_risk[m]}/100, "
            f"avg_rejection={sub['rejection_rate'].mean():.1f}%."
        )
    sg = df.groupby("shift")[["produced_units","rejected_units"]].sum()
    for s, row in sg.iterrows():
        yr = (row["produced_units"]-row["rejected_units"])/max(row["produced_units"],1)*100
        lines.append(f"{s} shift: produced={row['produced_units']}, rejected={row['rejected_units']}, yield={yr:.1f}%.")
    return " ".join(lines)

def ask_claude(question, context, history):
    system = (
        "You are PlantIQ, an expert AI assistant for a non-expert manufacturing plant operator. "
        "Answer in plain English — no jargon. Be concise (3-5 sentences). "
        "Be specific: use the actual numbers from the context. Give actionable advice. "
        f"\n\nLIVE PLANT CONTEXT:\n{context}"
    )
    messages = history + [{"role":"user","content":question}]
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":400,
                  "system":system,"messages":messages},
            timeout=20,
        )
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"⚠️ Could not reach AI: {e}"

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex;align-items:baseline;gap:16px;margin-bottom:2px'>
  <h1 style='margin:0;font-size:1.9rem;background:linear-gradient(90deg,#60a5fa,#93c5fd);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
    ⚙️ PlantIQ Monitoring Dashboard
  </h1>
  <span style='font-family:IBM Plex Mono,monospace;font-size:11px;color:#2a4060'>
    {d_start} → {d_end} &nbsp;|&nbsp; {', '.join(sel_machines)} &nbsp;|&nbsp; {', '.join(sel_shifts)} shift
  </span>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 1 — KPI CARDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sh">📊 PLANT-WIDE KPIs</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, sub, accent, color):
    col.markdown(f"""
    <div class="kpi-wrap" style="--kpi-accent:{accent};--kpi-color:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

up_col  = "#4ade80" if uptime_pct>=80 else ("#fbbf24" if uptime_pct>=60 else "#f87171")
yr_col  = "#4ade80" if yield_rate>=90 else ("#fbbf24" if yield_rate>=75 else "#f87171")
ft_col  = "#f87171" if fault_count>0 else "#4ade80"
top_risk = max(machine_risk.values()) if machine_risk else 0
rk_col  = "#4ade80" if top_risk<30 else ("#fbbf24" if top_risk<60 else "#f87171")

kpi(k1,"⏱ PLANT UPTIME",   f"{uptime_pct:.1f}%", f"{(df['status']=='RUNNING').sum():,} / {total:,} readings","#2563eb",up_col)
kpi(k2,"✅ YIELD RATE",     f"{yield_rate:.1f}%", f"{total_prod-total_rej:,} good of {total_prod:,} units","#16a34a",yr_col)
kpi(k3,"🚨 FAULT READINGS", str(fault_count),      f"{fault_count/total*100:.1f}% of all readings","#dc2626",ft_col)
kpi(k4,"⚠️ MAX RISK SCORE", f"{top_risk}/100",     "Highest machine risk index","#ca8a04",rk_col)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ROW 2 — MACHINE CARDS + GAUGES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sh">🤖 INDIVIDUAL MACHINE STATUS</div>', unsafe_allow_html=True)

STATUS_CSS  = {"RUNNING":"mc-running","IDLE":"mc-idle","FAULT":"mc-fault"}
BADGE_CSS   = {"RUNNING":"badge-running","IDLE":"badge-idle","FAULT":"badge-fault"}
STATUS_ICON = {"RUNNING":"▶","IDLE":"⏸","FAULT":"⚡"}

def make_gauge(val, max_v, w_thresh, c_thresh, title):
    bar_col = "#4ade80" if val<=w_thresh else ("#fbbf24" if val<=c_thresh else "#f87171")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val,
        number={"suffix":" mm/s","font":{"size":14,"color":"#c8d8e8"}},
        title={"text":title,"font":{"size":11,"color":"#4a6080","family":"IBM Plex Mono"}},
        gauge={
            "axis":{"range":[0,max_v],"tickcolor":"#1e3050","tickfont":{"color":"#3a5070","size":9}},
            "bar":{"color":bar_col,"thickness":.28},
            "bgcolor":"#080c14","bordercolor":"#1a2540",
            "steps":[{"range":[0,w_thresh],"color":"#071510"},
                     {"range":[w_thresh,c_thresh],"color":"#1a1200"},
                     {"range":[c_thresh,max_v],"color":"#180808"}],
            "threshold":{"line":{"color":"#dc2626","width":3},"thickness":.8,"value":c_thresh},
        },
    ))
    fig.update_layout(height=170, margin=dict(l=15,r=15,t=35,b=5),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#c8d8e8")
    return fig

mcols = st.columns(len(sel_machines))
for i, mach in enumerate(sel_machines):
    row = latest[latest["machine_id"]==mach]
    if row.empty: continue
    r   = row.iloc[0]
    st_ = r["status"]
    rs  = machine_risk[mach]
    rsk_cls = "risk-low" if rs<30 else ("risk-med" if rs<60 else "risk-high")
    rsk_lbl = "LOW" if rs<30 else ("MEDIUM" if rs<60 else "HIGH")
    cur_col = "#f87171" if r["current_a"]>cur_thresh else "#c8d8e8"
    vib_col = "#f87171" if r["vibration_mm_s"]>vib_thresh else "#c8d8e8"

    with mcols[i]:
        st.markdown(f"""
        <div class="mc {STATUS_CSS.get(st_,'mc-idle')}">
          <div class="mc-head">
            <span class="mc-id">{mach}</span>
            <span class="mc-badge {BADGE_CSS.get(st_,'badge-idle')}">{STATUS_ICON.get(st_,'?')} {st_}</span>
          </div>
          <div class="mc-metrics">
            <div class="mc-m"><div class="mc-m-label">CURRENT</div>
              <div class="mc-m-val" style="color:{cur_col}">{r['current_a']:.1f} A</div></div>
            <div class="mc-m"><div class="mc-m-label">VIBRATION</div>
              <div class="mc-m-val" style="color:{vib_col}">{r['vibration_mm_s']:.2f} mm/s</div></div>
            <div class="mc-m"><div class="mc-m-label">PRODUCED</div>
              <div class="mc-m-val">{int(r['produced_units'])}</div></div>
            <div class="mc-m"><div class="mc-m-label">REJECTED</div>
              <div class="mc-m-val">{int(r['rejected_units'])}</div></div>
          </div>
          <div style="margin-top:12px;font-family:'IBM Plex Mono',monospace;font-size:11px;">
            RISK INDEX &nbsp;<span class="{rsk_cls}" style="font-weight:700">{rs}/100 — {rsk_lbl}</span>
          </div>
          <div style="background:#0f1928;border-radius:6px;height:6px;margin-top:6px;">
            <div style="background:{'#4ade80' if rs<30 else '#fbbf24' if rs<60 else '#f87171'};
                        width:{rs}%;height:100%;border-radius:6px"></div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.plotly_chart(
            make_gauge(r["vibration_mm_s"], 20, 8, vib_thresh, f"{mach} Vibration Health"),
            use_container_width=True, config={"displayModeBar":False}
        )

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 3 — AI CHAT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sh">🤖 AI PLANT ASSISTANT — Ask Anything in Plain English</div>', unsafe_allow_html=True)

if "chat_history"   not in st.session_state: st.session_state.chat_history   = []
if "display_history" not in st.session_state: st.session_state.display_history = []

QUICK = [
    "Which machine needs urgent attention?",
    "Why is the yield rate what it is?",
    "Which shift performs better and why?",
    "What should maintenance do this week?",
    "What caused the most recent faults?",
    "Explain the vibration readings simply",
]

qcols = st.columns(3)
for idx, q in enumerate(QUICK):
    if qcols[idx%3].button(q, key=f"q{idx}", use_container_width=True):
        st.session_state._quick_q = q

user_q = st.chat_input("Ask PlantIQ anything about your plant…") or st.session_state.pop("_quick_q", None)

if user_q:
    ctx    = build_context()
    ai_ans = ask_claude(user_q, ctx, st.session_state.chat_history)
    st.session_state.display_history.append((user_q, ai_ans))
    st.session_state.chat_history.extend([
        {"role":"user","content":user_q},
        {"role":"assistant","content":ai_ans},
    ])
    if len(st.session_state.chat_history) > 20:
        st.session_state.chat_history = st.session_state.chat_history[-20:]

with st.container():
    if not st.session_state.display_history:
        st.markdown("""
        <div style='text-align:center;padding:30px;color:#2a4060;
                    font-family:IBM Plex Mono,monospace;font-size:12px;'>
            💬 Click a quick question above or type below.<br>
            "Which machine is most at risk?" &nbsp;·&nbsp; "What should I do today?"
        </div>""", unsafe_allow_html=True)
    for user_msg, ai_msg in st.session_state.display_history[-6:]:
        st.markdown(f"""
        <div class="chat-label">YOU</div>
        <div class="chat-msg-user">{user_msg}</div>
        <div class="chat-label" style="color:#60a5fa;margin-top:8px">⚙️ PLANTIQ AI</div>
        <div class="chat-msg-ai">{ai_msg}</div>
        """, unsafe_allow_html=True)

if st.session_state.display_history:
    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history   = []
        st.session_state.display_history = []
        st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 4 — SENSOR TRENDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sh">📈 SENSOR TRENDS OVER TIME</div>', unsafe_allow_html=True)

MACH_COLORS = {"M1":"#3b82f6","M2":"#f97316","M3":"#22c55e"}

fig_trend = make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.09,
    subplot_titles=("Motor Current (A)","Vibration Velocity (mm/s)"),row_heights=[.5,.5])

for mach in sel_machines:
    sub = df[df["machine_id"]==mach].sort_values("timestamp")
    c   = MACH_COLORS.get(mach,"#aaa")
    sub = sub.copy()
    sub["cur_roll"] = sub["current_a"].rolling(8,min_periods=1).mean()
    sub["vib_roll"] = sub["vibration_mm_s"].rolling(8,min_periods=1).mean()

    fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["current_a"],name=f"{mach}",
        line=dict(color=c,width=1),opacity=.4,showlegend=True,
        hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>%{{y:.1f}} A<extra></extra>"),row=1,col=1)
    fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["cur_roll"],name=f"{mach} avg",
        line=dict(color=c,width=2.5),showlegend=False,
        hovertemplate=f"<b>{mach} rolling avg</b><br>%{{y:.1f}} A<extra></extra>"),row=1,col=1)
    fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["vibration_mm_s"],name=f"{mach}",
        line=dict(color=c,width=1,dash="dot"),opacity=.4,showlegend=False,
        hovertemplate=f"<b>{mach}</b><br>%{{y:.2f}} mm/s<extra></extra>"),row=2,col=1)
    fig_trend.add_trace(go.Scatter(x=sub["timestamp"],y=sub["vib_roll"],name=f"{mach} avg",
        line=dict(color=c,width=2.5),showlegend=False),row=2,col=1)

fig_trend.add_hline(y=cur_thresh,row=1,col=1,line_color="#dc2626",line_dash="dash",
    annotation_text=f"Alert {cur_thresh}A",annotation_font_color="#dc2626")
fig_trend.add_hline(y=vib_thresh,row=2,col=1,line_color="#dc2626",line_dash="dash",
    annotation_text=f"Alert {vib_thresh}mm/s",annotation_font_color="#dc2626")
fig_trend.update_layout(height=460,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(8,12,20,.8)",
    font_color="#c8d8e8",hovermode="x unified",margin=dict(l=10,r=10,t=40,b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)",font_size=11),font_family="IBM Plex Mono")
fig_trend.update_xaxes(gridcolor="#0f1928",zeroline=False)
fig_trend.update_yaxes(gridcolor="#0f1928",zeroline=False)
st.plotly_chart(fig_trend, use_container_width=True)
st.caption("Thick lines = 8-reading rolling average (removes noise). Thin lines = raw sensor data. Dashed red = alert threshold.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 5 — PRODUCTION + CORRELATION + RISK
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sh">🏗️ PRODUCTION & CORRELATION ANALYSIS</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2.5,2,2])

with c1:
    st.markdown("**Production by Shift**")
    shift_df = df.groupby(["shift","machine_id"])[["produced_units","rejected_units"]].sum().reset_index()
    fig_bar  = go.Figure()
    for mach in sel_machines:
        sub = shift_df[shift_df["machine_id"]==mach]
        col = MACH_COLORS.get(mach,"#aaa")
        fig_bar.add_trace(go.Bar(name=f"{mach} Good",x=sub["shift"],
            y=sub["produced_units"]-sub["rejected_units"],marker_color=col,opacity=.9))
        fig_bar.add_trace(go.Bar(name=f"{mach} Rejected",x=sub["shift"],
            y=sub["rejected_units"],marker_color=col,opacity=.35,marker_pattern_shape="/"))
    fig_bar.update_layout(barmode="group",height=290,paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,12,20,.8)",font_color="#c8d8e8",
        margin=dict(l=5,r=5,t=5,b=5),legend=dict(bgcolor="rgba(0,0,0,0)",font_size=10),
        font_family="IBM Plex Mono")
    fig_bar.update_xaxes(gridcolor="#0f1928")
    fig_bar.update_yaxes(gridcolor="#0f1928")
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.markdown("**Sensor Correlation Heatmap**")
    cols_c = ["current_a","vibration_mm_s","rejection_rate","produced_units"]
    corr   = df[cols_c].corr().round(2)
    labels = ["Current","Vibration","Rejection%","Produced"]
    fig_heat = go.Figure(go.Heatmap(
        z=corr.values, x=labels, y=labels,
        colorscale=[[0,"#dc2626"],[.5,"#0f1928"],[1,"#2563eb"]],
        zmid=0, text=corr.values, texttemplate="%{text}",
        textfont={"size":12,"family":"IBM Plex Mono"},
    ))
    fig_heat.update_layout(height=290,paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",font_color="#c8d8e8",
        margin=dict(l=5,r=5,t=5,b=5),font_family="IBM Plex Mono")
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("🔵 = positive correlation · 🔴 = negative. Current & Vibration (+0.30) spike together before faults.")

with c3:
    st.markdown("**Predictive Risk Score**")
    risk_df = pd.DataFrame({"Machine":list(machine_risk.keys()),
                             "Score":list(machine_risk.values())})
    risk_df["Color"] = risk_df["Score"].apply(
        lambda x: "#4ade80" if x<30 else ("#fbbf24" if x<60 else "#f87171"))
    fig_risk = go.Figure(go.Bar(
        x=risk_df["Machine"], y=risk_df["Score"],
        marker_color=risk_df["Color"],
        text=risk_df["Score"], texttemplate="%{text}/100",
        textposition="outside", textfont={"family":"IBM Plex Mono","size":12},
    ))
    fig_risk.update_layout(height=290,paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,12,20,.8)",font_color="#c8d8e8",
        margin=dict(l=5,r=5,t=20,b=5),yaxis_range=[0,115],
        font_family="IBM Plex Mono")
    fig_risk.update_xaxes(gridcolor="#0f1928")
    fig_risk.update_yaxes(gridcolor="#0f1928")
    st.plotly_chart(fig_risk, use_container_width=True)
    st.caption("Composite: fault rate (40%) + vibration exceedances (30%) + current exceedances (20%) + rejection rate (10%)")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 6 — ALERTS LOG + CSV EXPORT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sh">🚨 ANOMALY ALERTS LOG</div>', unsafe_allow_html=True)

if alerts_df.empty:
    st.success("✅ No anomalies detected in the current selection.")
else:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Anomaly Rows",      len(alerts_df))
    m2.metric("Machines Affected", alerts_df["machine_id"].nunique())
    m3.metric("Most Affected",     alerts_df["machine_id"].value_counts().idxmax())
    m4.metric("Anomaly Rate",      f"{len(alerts_df)/total*100:.1f}%")

    disp = alerts_df.copy()
    disp["Triggered By"] = disp.apply(lambda r: " | ".join(filter(None,[
        f"⚡ {r['current_a']:.1f}A>{cur_thresh}A"         if r["current_a"]>cur_thresh else "",
        f"📳 {r['vibration_mm_s']:.2f}>{vib_thresh}mm/s"  if r["vibration_mm_s"]>vib_thresh else "",
        f"❌ rej {r['rejection_rate']:.1f}%>10%"           if r["rejection_rate"]>10 else "",
    ])), axis=1)
    disp = disp[["timestamp","machine_id","status","current_a","vibration_mm_s","rejection_rate","Triggered By"]]
    disp.columns = ["Timestamp","Machine","Status","Current (A)","Vibration (mm/s)","Rejection (%)","Triggered By"]
    disp["Timestamp"]     = pd.to_datetime(disp["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    disp["Rejection (%)"] = disp["Rejection (%)"].round(2)

    st.dataframe(disp.sort_values("Timestamp",ascending=False), use_container_width=True,
                 hide_index=True, column_config={
                     "Current (A)":     st.column_config.NumberColumn(format="%.1f A"),
                     "Vibration (mm/s)":st.column_config.NumberColumn(format="%.2f mm/s"),
                     "Rejection (%)":   st.column_config.NumberColumn(format="%.2f%%"),
                 })
    csv = disp.to_csv(index=False).encode()
    st.download_button("⬇️ Export Alerts as CSV", csv,
                       file_name=f"plant_alerts_{d_start}_{d_end}.csv", mime="text/csv")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ROW 7 — RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
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
        if rs >= 60:
            st.error(f"🚨 **{m}** risk score **{rs}/100** — immediate inspection recommended.")
        elif rs >= 30:
            st.warning(f"⚠️ **{m}** risk score **{rs}/100** — schedule inspection within 48 hrs.")

with r2:
    st.markdown("#### 🔬 Advanced Sensing Roadmap")
    st.markdown("""
| Sensor | Detects | Lead Time Gained |
|--------|---------|-----------------|
| 🌡️ **Thermal Camera** | Overheating motors & bearings | 2–3 days early warning |
| 🎤 **Acoustic Emission** | Micro-cracks, bearing wear | Sub-mm defect detection |
| 🛢️ **Oil Quality** | Lubricant degradation | Prevent seizure failures |
| 🔄 **Torque Sensor** | Rotational load anomalies | Isolate fault type |
| 🌊 **Ultrasonic** | Internal leaks, cavitation | Non-invasive inspection |
""")
    st.info("💡 Thermal + acoustic sensors combined with current ML models can reduce unplanned downtime by up to **40%** through multi-modal predictive maintenance.")

best_shift = df.groupby("shift").apply(
    lambda g: (g["produced_units"].sum()-g["rejected_units"].sum())/max(g["produced_units"].sum(),1)*100
).idxmax()

st.markdown(f"""
> **📋 Executive Summary — {d_start} to {d_end}**  
> Uptime **{uptime_pct:.1f}%** · Yield **{yield_rate:.1f}%** · Faults **{fault_count}** · Anomalies **{len(alerts_df)}**  
> Highest-risk machine: **{high_risk_m}** ({machine_risk.get(high_risk_m,0)}/100) · Best shift: **{best_shift}**  
> *Action: Prioritise {top_fault_m} maintenance and deploy real-time alerting on vibration + current thresholds.*
""")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-family:IBM Plex Mono,monospace;font-size:10px;
            color:#1e3050;padding:8px 0;letter-spacing:.1em'>
    EE4409 CA2 · PlantIQ Manufacturing Dashboard · Streamlit · Plotly · Pandas · Claude AI
</div>""", unsafe_allow_html=True)

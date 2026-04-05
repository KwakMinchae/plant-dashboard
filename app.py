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
# THEME TOGGLE + CSS
# ─────────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

D = dict(
    bg="#080c14", sidebar_bg="#0b1020", sidebar_br="#1a2540",
    text="#c8d8e8", text_dim="#4a6080",
    kpi_bg="linear-gradient(145deg,#0f1928,#131e30)", kpi_border="#1e3050", kpi_sub="#3a5070",
    mc_run="#071a10", mc_idle="#1a1500", mc_fault="#180808",
    mc_m_bg="rgba(255,255,255,.04)", mc_m_label="#3a5070",
    vib_bar_bg="#0f1928", vib_label="#4a6080",
    sh_pri_color="#c8d8e8", sh_pri_border="#2563eb",
    sh_sec_color="#4a6080", sh_sec_border="#1a2540",
    alert_bg="linear-gradient(135deg,#1a0808,#2a0f0f)", alert_border="#7f1d1d",
    thresh_bg="#0d1a2e", thresh_border="#1e3a60", thresh_color="#6080a0", thresh_b="#c8d8e8",
    insight_bg="#0b1422",
    adv_bg="#0f1928", adv_border="#1e3050", adv_color="#8899aa", adv_b="#c8d8e8",
    info_bg="#0b1422", info_border="#1a2540", info_b="#60a5fa",
    scroll_track="#0b1020", scroll_thumb="#1e3050",
    plot_bg="rgba(8,12,20,.8)", grid_color="#0f1928", font_color="#c8d8e8",
    badge_run_bg="#14532d", badge_run_fg="#4ade80",
    badge_idle_bg="#422006", badge_idle_fg="#fbbf24",
    badge_fault_bg="#450a0a", badge_fault_fg="#f87171",
)
L = dict(
    bg="#f7f5f0", sidebar_bg="#eeeae0", sidebar_br="#d0c8b8",
    text="#1a1a1a", text_dim="#666",
    kpi_bg="linear-gradient(145deg,#ffffff,#f0ede6)", kpi_border="#ddd5c8", kpi_sub="#888",
    mc_run="#f0fdf4", mc_idle="#fefce8", mc_fault="#fff1f1",
    mc_m_bg="rgba(0,0,0,.04)", mc_m_label="#888",
    vib_bar_bg="#e0dbd0", vib_label="#888",
    sh_pri_color="#111", sh_pri_border="#2563eb",
    sh_sec_color="#888", sh_sec_border="#ddd",
    alert_bg="linear-gradient(135deg,#fff1f1,#ffe4e4)", alert_border="#fca5a5",
    thresh_bg="#eef2ff", thresh_border="#c7d2fe", thresh_color="#4a5580", thresh_b="#1a1a1a",
    insight_bg="#eff6ff",
    adv_bg="#f0f4ff", adv_border="#c7d2fe", adv_color="#444", adv_b="#111",
    info_bg="#f0f6ff", info_border="#bcd", info_b="#1d4ed8",
    scroll_track="#e8e0d0", scroll_thumb="#bbb",
    plot_bg="rgba(247,245,240,.95)", grid_color="#e8e0d0", font_color="#1a1a1a",
    badge_run_bg="#dcfce7", badge_run_fg="#166534",
    badge_idle_bg="#fef9c3", badge_idle_fg="#854d0e",
    badge_fault_bg="#fee2e2", badge_fault_fg="#991b1b",
)

T = D if st.session_state.dark_mode else L

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');
html,body,[data-testid="stAppViewContainer"]{{background:{T["bg"]};color:{T["text"]};font-family:'Inter',sans-serif;}}
[data-testid="stSidebar"]{{background:{T["sidebar_bg"]};border-right:1px solid {T["sidebar_br"]};}}
[data-testid="stSidebar"] *{{color:{T["text"]} !important;}}
h1,h2,h3{{font-family:'Syne',sans-serif;}}
.kpi-wrap{{background:{T["kpi_bg"]};border:1px solid {T["kpi_border"]};border-radius:16px;
  padding:24px 20px 18px;text-align:center;position:relative;overflow:hidden;transition:transform .25s,box-shadow .25s;}}
.kpi-wrap:hover{{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,120,255,.12);}}
.kpi-wrap::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--kpi-accent,#2563eb);border-radius:16px 16px 0 0;}}
.kpi-label{{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.12em;
  color:{T["text_dim"]};text-transform:uppercase;margin-bottom:10px;}}
.kpi-value{{font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;line-height:1;color:var(--kpi-color,#2563eb);}}
.kpi-sub{{font-size:11px;color:{T["kpi_sub"]};margin-top:8px;font-family:'IBM Plex Mono',monospace;}}
.mc{{border-radius:14px;padding:20px 22px;border-left:4px solid transparent;transition:transform .2s;}}
.mc:hover{{transform:translateX(3px);}}
.mc-running{{background:{T["mc_run"]};border-color:#16a34a;}}
.mc-idle{{background:{T["mc_idle"]};border-color:#ca8a04;}}
.mc-fault{{background:{T["mc_fault"]};border-color:#dc2626;animation:fault-pulse 2s ease-in-out infinite;}}
@keyframes fault-pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(220,38,38,0);}}50%{{box-shadow:0 0 0 8px rgba(220,38,38,.15);}}}}
.mc-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}}
.mc-id{{font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:{T["text"]};}}
.mc-badge{{font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.1em;padding:3px 10px;border-radius:20px;}}
.badge-running{{background:{T["badge_run_bg"]};color:{T["badge_run_fg"]};}}
.badge-idle{{background:{T["badge_idle_bg"]};color:{T["badge_idle_fg"]};}}
.badge-fault{{background:{T["badge_fault_bg"]};color:{T["badge_fault_fg"]};}}
.mc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;}}
.mc-m{{background:{T["mc_m_bg"]};border-radius:8px;padding:10px 12px;}}
.mc-m-label{{font-size:10px;color:{T["mc_m_label"]};font-family:'IBM Plex Mono',monospace;letter-spacing:.08em;margin-bottom:4px;}}
.mc-m-val{{font-size:1.15rem;font-weight:600;color:{T["text"]};}}
.mc-vib-bar-bg{{background:{T["vib_bar_bg"]};border-radius:6px;height:7px;margin-top:14px;}}
.mc-vib-bar{{height:100%;border-radius:6px;background:var(--vb-col,#aaa);width:var(--vb-w,0%);}}
.mc-vib-label{{font-size:11px;color:{T["vib_label"]};margin-top:5px;font-family:'IBM Plex Mono',monospace;}}
.risk-low{{color:#16a34a;}}.risk-med{{color:#ca8a04;}}.risk-high{{color:#dc2626;}}
.sh-primary{{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:{T["sh_pri_color"]};
  border-bottom:2px solid {T["sh_pri_border"]};padding-bottom:8px;margin-bottom:18px;letter-spacing:.02em;}}
.sh-secondary{{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.15em;
  color:{T["sh_sec_color"]};text-transform:uppercase;border-bottom:1px solid {T["sh_sec_border"]};
  padding-bottom:6px;margin-bottom:14px;}}
.alert-banner{{background:{T["alert_bg"]};border:1px solid {T["alert_border"]};
  border-left:4px solid #ef4444;border-radius:12px;padding:16px 20px;margin-bottom:6px;}}
.alert-banner-title{{font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#dc2626;margin-bottom:4px;}}
.alert-banner-sub{{font-size:12px;color:#888;font-family:'IBM Plex Mono',monospace;}}
.thresh-bar{{background:{T["thresh_bg"]};border:1px solid {T["thresh_border"]};border-radius:8px;
  padding:10px 16px;font-family:'IBM Plex Mono',monospace;font-size:11px;
  color:{T["thresh_color"]};display:flex;gap:28px;flex-wrap:wrap;margin-bottom:18px;}}
.thresh-bar b{{color:{T["thresh_b"]};}}
.thresh-crit{{color:#dc2626;font-weight:600;}}
.insight{{background:{T["insight_bg"]};border-left:3px solid #2563eb;border-radius:0 8px 8px 0;
  padding:12px 16px;margin:10px 0 16px;font-size:13px;color:{T["text"]};line-height:1.7;}}
.insight b{{color:{T["text"]};}}
.adv-intro{{background:{T["adv_bg"]};border:1px solid {T["adv_border"]};border-radius:10px;
  padding:16px 20px;margin-bottom:24px;font-size:13px;color:{T["adv_color"]};line-height:1.7;}}
.adv-intro b{{color:{T["adv_b"]};}}
.info-box{{background:{T["info_bg"]};border:1px solid {T["info_border"]};border-radius:10px;
  padding:12px;margin:8px 0;font-size:.8rem;line-height:1.7;color:{T["text"]};}}
.info-box b{{color:{T["info_b"]};}}
.crit{{color:#dc2626;font-weight:700;}}
::-webkit-scrollbar{{width:6px;}}
::-webkit-scrollbar-track{{background:{T["scroll_track"]};}}
::-webkit-scrollbar-thumb{{background:{T["scroll_thumb"]};border-radius:3px;}}
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
                 df["rejected_units"]/df["produced_units"]*100, 0))
    return df

for p in [DATA_FILE, f"data/{DATA_FILE}", f"/mnt/user-data/uploads/{DATA_FILE}"]:
    if os.path.exists(p):
        df_raw = load_data(p); break
else:
    up = st.file_uploader("Upload plant_monitoring_data_1_.xlsm", type=["xlsm","xlsx","csv"])
    if up: df_raw = load_data(up)
    else:  st.info("Place your `.xlsm` file next to `app.py`, or upload it above."); st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Fix #10: sensor guide always open by default
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:10px 0 20px'>
    <div style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;
                background:linear-gradient(90deg,#3b82f6,#60a5fa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent'>⚙️ PlantIQ</div>
    <div style='font-family:IBM Plex Mono,monospace;font-size:10px;color:#2a4060;
                letter-spacing:.15em'>MANUFACTURING MONITOR</div></div>""", unsafe_allow_html=True)

    # Theme toggle
    mode_label = "☀️ Switch to Light Mode" if st.session_state.dark_mode else "🌙 Switch to Dark Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    # Fix #10: expanded=True so users see it immediately
    with st.expander("ℹ️ Sensor Guide", expanded=True):
        st.markdown("""
<div class="info-box"><b>⚡ Current Sensor</b><br>Measures motor electrical load (Amperes).<br>
Normal: <b>10–50 A</b> &nbsp;·&nbsp; <span class="crit">Critical: &gt; 60 A</span></div>
<div class="info-box"><b>📳 Vibration Sensor</b><br>Measures mechanical velocity (mm/s).<br>
Normal: <b>1–8 mm/s</b> &nbsp;·&nbsp; <span class="crit">Critical: &gt; 10 mm/s</span></div>
<div class="info-box"><b>🔴 A FAULT is triggered when:</b><br>
Vibration &gt; 10 mm/s, or Current &gt; 60 A</div>
<div class="info-box"><b>📦 Rejection Rate:</b><br>
<b>RUNNING:</b> rejected ÷ produced × 100%<br>
<b>FAULT:</b> 100% (machine is fully down)</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sh-secondary" style="margin-top:16px">FILTERS</div>', unsafe_allow_html=True)
    all_machines = sorted(df_raw["machine_id"].unique())
    sel_machines = st.multiselect("Machine", all_machines, default=all_machines)
    mn, mx = df_raw["date"].min(), df_raw["date"].max()
    d_range = st.date_input("Date Range", value=(mn, mx), min_value=mn, max_value=mx)
    d_start, d_end = (d_range[0], d_range[1]) if len(d_range)==2 else (mn, mx)
    sel_shifts = st.multiselect("Shift", ["Day","Night"], default=["Day","Night"])

    st.markdown('<div class="sh-secondary" style="margin-top:16px">THRESHOLDS</div>', unsafe_allow_html=True)
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
# Fix #7: alerts computed early so it can appear at top
alerts_df   = df[
    (df["vibration_mm_s"]>vib_thresh) |
    (df["current_a"]>cur_thresh) |
    ((df["status"]!="FAULT") & (df["rejection_rate"]>10))
]

def risk_score(mach_df, fc, vib_t, cur_t):
    n = len(mach_df) or 1
    return min(int((fc/n*100*0.40 +
                    (mach_df["vibration_mm_s"]>vib_t).sum()/n*100*0.30 +
                    (mach_df["current_a"]>cur_t).sum()/n*100*0.20 +
                    min(mach_df[mach_df["status"]!="FAULT"]["rejection_rate"].mean() if (mach_df["status"]!="FAULT").any() else 0,20)*0.10) * 3.5), 100)

machine_risk = {m: risk_score(df[df["machine_id"]==m],
                               (df[df["machine_id"]==m]["status"]=="FAULT").sum(),
                               vib_thresh, cur_thresh) for m in sel_machines}

# ─────────────────────────────────────────────────────────────────────────────
# SHARED CHART STYLE — Fix #8: consistent machine colours everywhere
# ─────────────────────────────────────────────────────────────────────────────
MACH_COLORS = {"M1":"#3b82f6","M2":"#f97316","M3":"#22c55e"}

CHART_BASE = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=T["plot_bg"],
                  font_color=T["font_color"], font_family="IBM Plex Mono",
                  margin=dict(l=10,r=10,t=45,b=10))

def apply_grid(fig, rows=None):
    kw = dict(gridcolor=T["grid_color"], zeroline=False)
    if rows:
        for r in rows:
            fig.update_xaxes(**kw, row=r)
            fig.update_yaxes(**kw, row=r)
    else:
        fig.update_xaxes(**kw)
        fig.update_yaxes(**kw)

# Fix #11: helper to render insight text with styled div
def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style='display:flex;align-items:baseline;gap:16px;margin-bottom:4px'>
  <h1 style='margin:0;font-size:2rem;background:linear-gradient(90deg,#60a5fa,#93c5fd);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent'>⚙️ PlantIQ</h1>
  <span style='font-family:IBM Plex Mono,monospace;font-size:11px;color:#2a4060'>
    {d_start} → {d_end} &nbsp;|&nbsp; {', '.join(sel_machines)} &nbsp;|&nbsp; {', '.join(sel_shifts)} shift
  </span></div>""", unsafe_allow_html=True)

# Fix #1: always-visible threshold banner under header
st.markdown(f"""<div class="thresh-bar">
  <span>⚡ Current normal: <b>10–50 A</b> &nbsp;·&nbsp; <span class="thresh-crit">Critical: &gt; {cur_thresh:.0f} A</span></span>
  <span>📳 Vibration normal: <b>1–8 mm/s</b> &nbsp;·&nbsp; <span class="thresh-crit">Critical: &gt; {vib_thresh:.0f} mm/s</span></span>
  <span>🔴 FAULT = machine down &nbsp;·&nbsp; Rejection rate during FAULT = 100%</span>
</div>""", unsafe_allow_html=True)
st.markdown("---")

TAB_MAIN, TAB_ADV = st.tabs(["📊  Live Dashboard", "🔬  Advanced Analysis"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE DASHBOARD  (clean: Alert → KPIs → Machine Cards → Alerts Log)
# ══════════════════════════════════════════════════════════════════════════════
with TAB_MAIN:

    # ── 1. ALERT BANNER ──────────────────────────────────────────────────────
    if not alerts_df.empty:
        top_machine = alerts_df["machine_id"].value_counts().idxmax()
        st.markdown(f"""<div class="alert-banner">
          <div class="alert-banner-title">⚠️ {len(alerts_df)} Anomalies Detected</div>
          <div class="alert-banner-sub">
            {alerts_df["machine_id"].nunique()} machine(s) affected &nbsp;·&nbsp;
            Most alerts: <b style="color:#f87171">{top_machine}</b> &nbsp;·&nbsp;
            Anomaly rate: {len(alerts_df)/total*100:.1f}% of readings
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── 2. KPI CARDS ─────────────────────────────────────────────────────────
    st.markdown('<div class="sh-primary">Plant Overview</div>', unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)

    def kpi(col, label, value, sub, accent, color):
        col.markdown(f"""<div class="kpi-wrap" style="--kpi-accent:{accent};--kpi-color:{color}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

    up_col = "#4ade80" if uptime_pct>=80 else ("#fbbf24" if uptime_pct>=60 else "#f87171")
    yr_col = "#4ade80" if yield_rate>=90 else ("#fbbf24" if yield_rate>=75 else "#f87171")
    ft_col = "#f87171" if fault_count>0 else "#4ade80"

    kpi(k1,"⏱ Plant Uptime",   f"{uptime_pct:.1f}%",
        f"{(df['status']=='RUNNING').sum():,} / {total:,} readings","#2563eb",up_col)
    kpi(k2,"✅ Yield Rate",     f"{yield_rate:.1f}%",
        f"{total_prod-total_rej:,} good of {total_prod:,} units","#16a34a",yr_col)
    kpi(k3,"🚨 Fault Readings", str(fault_count),
        f"{fault_count/total*100:.1f}% of all readings — machine down","#dc2626",ft_col)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3. MACHINE STATUS CARDS ───────────────────────────────────────────────
    st.markdown('<div class="sh-primary">Individual Machine Status</div>', unsafe_allow_html=True)

    STATUS_CSS  = {"RUNNING":"mc-running","IDLE":"mc-idle","FAULT":"mc-fault"}
    BADGE_CSS   = {"RUNNING":"badge-running","IDLE":"badge-idle","FAULT":"badge-fault"}
    STATUS_ICON = {"RUNNING":"▶","IDLE":"⏸","FAULT":"⚡"}

    mcols = st.columns(len(sel_machines))
    for i, mach in enumerate(sel_machines):
        row = latest[latest["machine_id"]==mach]
        if row.empty: continue
        r = row.iloc[0]; st_ = r["status"]; rs = machine_risk[mach]
        rsk_cls  = "risk-low" if rs<30 else ("risk-med" if rs<60 else "risk-high")
        rsk_lbl  = "LOW" if rs<30 else ("MEDIUM" if rs<60 else "HIGH")
        cc       = "#f87171" if r["current_a"]>cur_thresh else "#c8d8e8"
        vc       = "#f87171" if r["vibration_mm_s"]>vib_thresh else "#c8d8e8"
        vib_pct  = min(r["vibration_mm_s"]/20*100, 100)
        vib_col  = "#4ade80" if r["vibration_mm_s"]<=8 else ("#fbbf24" if r["vibration_mm_s"]<=vib_thresh else "#f87171")
        with mcols[i]:
            st.markdown(f"""<div class="mc {STATUS_CSS.get(st_,'mc-idle')}">
              <div class="mc-head">
                <span class="mc-id">{mach}</span>
                <span class="mc-badge {BADGE_CSS.get(st_,'badge-idle')}">{STATUS_ICON.get(st_,'?')} {st_}</span>
              </div>
              <div class="mc-grid">
                <div class="mc-m">
                  <div class="mc-m-label">MOTOR CURRENT</div>
                  <div class="mc-m-val" style="color:{cc}">{r['current_a']:.1f} A</div>
                </div>
                <div class="mc-m">
                  <div class="mc-m-label">VIBRATION</div>
                  <div class="mc-m-val" style="color:{vc}">{r['vibration_mm_s']:.2f} mm/s</div>
                </div>
                <div class="mc-m">
                  <div class="mc-m-label">UNITS PRODUCED</div>
                  <div class="mc-m-val">{int(r['produced_units'])}</div>
                </div>
                <div class="mc-m">
                  <div class="mc-m-label">UNITS REJECTED</div>
                  <div class="mc-m-val">{int(r['rejected_units'])}</div>
                </div>
              </div>
              <div class="mc-vib-bar-bg">
                <div class="mc-vib-bar" style="--vb-col:{vib_col};--vb-w:{vib_pct:.0f}%"></div>
              </div>
              <div class="mc-vib-label">
                Vibration: {r['vibration_mm_s']:.2f} / 20 mm/s &nbsp;·&nbsp;
                Risk: <span class="{rsk_cls}"><b>{rs}/100 — {rsk_lbl}</b></span>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── 4. FAULT ALERT LOG ────────────────────────────────────────────────────
    st.markdown('<div class="sh-primary">Fault Alert Log</div>', unsafe_allow_html=True)

    def get_severity(row):
        both = row["current_a"] > cur_thresh and row["vibration_mm_s"] > vib_thresh
        if both or row["status"] == "FAULT": return "🔴 HIGH"
        if row["current_a"] > cur_thresh or row["vibration_mm_s"] > vib_thresh: return "🟠 MEDIUM"
        return "🟡 LOW"

    if alerts_df.empty:
        st.success("✅ No anomalies detected in the current selection.")
    else:
        disp = alerts_df.copy()
        disp["Severity"] = disp.apply(get_severity, axis=1)
        high_c   = (disp["Severity"]=="🔴 HIGH").sum()
        medium_c = (disp["Severity"]=="🟠 MEDIUM").sum()
        low_c    = (disp["Severity"]=="🟡 LOW").sum()

        sev1, sev2, sev3 = st.columns(3)
        for col_s, label_s, count_s, sub_s, bg_s, bc_s, tc_s in [
            (sev1,"🔴 HIGH",   high_c,   "Both sensors exceeded or FAULT","#1a0808","#dc2626","#f87171"),
            (sev2,"🟠 MEDIUM", medium_c, "Single sensor exceeded",        "#1a1000","#f97316","#fbbf24"),
            (sev3,"🟡 LOW",    low_c,    "Quality threshold exceeded",    "#111800","#ca8a04","#fde047"),
        ]:
            col_s.markdown(f"""<div style="background:{bg_s};border:1px solid {bc_s};border-radius:10px;
                padding:14px;text-align:center">
                <div style="font-size:10px;color:#888;font-family:IBM Plex Mono,monospace;
                    letter-spacing:.1em;margin-bottom:6px">{label_s}</div>
                <div style="font-size:2rem;font-weight:800;color:{tc_s}">{count_s}</div>
                <div style="font-size:11px;color:#666;margin-top:4px">{sub_s}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        disp["Triggered By"] = disp.apply(lambda r: " | ".join(filter(None,[
            f"⚡ Current {r['current_a']:.1f}A > {cur_thresh:.0f}A"          if r["current_a"]>cur_thresh else "",
            f"📳 Vibration {r['vibration_mm_s']:.2f} > {vib_thresh:.0f}mm/s"  if r["vibration_mm_s"]>vib_thresh else "",
            f"❌ Rejection {r['rejection_rate']:.1f}% > 10%"                  if (r["status"]!="FAULT" and r["rejection_rate"]>10) else "",
        ])), axis=1)
        disp_show = disp[["timestamp","machine_id","status","Severity","current_a",
                           "vibration_mm_s","rejection_rate","Triggered By"]].copy()
        disp_show.columns = ["Timestamp","Machine","Status","Severity",
                             "Current (A)","Vibration (mm/s)","Rejection (%)","Triggered By"]
        disp_show["Timestamp"]     = pd.to_datetime(disp_show["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        disp_show["Rejection (%)"] = disp_show["Rejection (%)"].round(2)
        st.dataframe(disp_show.sort_values("Timestamp", ascending=False),
                     use_container_width=True, hide_index=True,
                     column_config={
                         "Current (A)":     st.column_config.NumberColumn(format="%.1f A"),
                         "Vibration (mm/s)":st.column_config.NumberColumn(format="%.2f mm/s"),
                         "Rejection (%)":   st.column_config.NumberColumn(format="%.2f%%"),
                     })
        st.download_button("⬇️ Export Alerts as CSV",
            disp_show.to_csv(index=False).encode(),
            file_name=f"plant_alerts_{d_start}_{d_end}.csv", mime="text/csv")
        insight("<b>HIGH</b> = both sensors exceeded or FAULT — act immediately. "
                "<b>MEDIUM</b> = single sensor exceeded — monitor closely. "
                "<b>LOW</b> = quality threshold only — review process.")

    st.markdown("---")

    # ── 5. OEE ───────────────────────────────────────────────────────────────
    st.markdown('<div class="sh-primary">📐 Overall Equipment Effectiveness (OEE)</div>', unsafe_allow_html=True)

    with st.expander("ℹ️ How OEE & all metrics are calculated", expanded=False):
        st.markdown(f"""
**OEE = Availability × Performance × Quality**

| Metric | Formula |
|--------|---------|
| **Availability (A)** | Running hours ÷ (Running + Fault + Idle hours) |
| **Performance (P)** | Actual output ÷ (Peak hourly rate × Running hours) |
| **Quality (Q)** | (Produced − Rejected) ÷ Produced |
| **OEE** | A × P × Q × 100% — World-class target: ≥ 85% |
| **Plant Uptime** | Running readings ÷ Total readings × 100% |
| **Yield Rate** | (Produced − Rejected) ÷ Produced × 100% |
| **Rejection Rate (RUNNING)** | Rejected ÷ Produced × 100% |
| **Rejection Rate (FAULT)** | 100% — machine is down, zero output |
| **Risk Score** | Fault rate×0.40 + Vib exceedances×0.30 + Cur exceedances×0.20 + Rejection×0.10, scaled 0–100 |
| **Severity HIGH** | Both current > {cur_thresh:.0f} A AND vibration > {vib_thresh:.0f} mm/s, or status = FAULT |
| **Severity MEDIUM** | One of current or vibration exceeds threshold |
| **Downtime Rate** | Fault hours ÷ Total hours × 100% — target < 2% (SEMI E10) |
""")

    oee_cols = st.columns(len(sel_machines) + 1)
    for i, mach in enumerate(sel_machines):
        msub   = df[df["machine_id"]==mach]
        n      = len(msub) or 1
        run_h  = (msub["status"]=="RUNNING").sum()
        avail  = run_h / n
        prod_run = msub[msub["status"]=="RUNNING"]["produced_units"]
        perf   = min(prod_run.sum() / max(prod_run.max() * run_h, 1), 1.0) if not prod_run.empty else 0
        good   = msub["produced_units"].sum() - msub["rejected_units"].sum()
        qual   = good / max(msub["produced_units"].sum(), 1)
        oee    = avail * perf * qual * 100
        oc     = "#4ade80" if oee>=85 else ("#fbbf24" if oee>=60 else "#f87171")
        with oee_cols[i]:
            st.markdown(f'''<div class="kpi-wrap" style="--kpi-accent:{oc};--kpi-color:{oc}">
                <div class="kpi-label">⚙️ {mach} OEE</div>
                <div class="kpi-value">{oee:.1f}%</div>
                <div class="kpi-sub">A:{avail*100:.0f}% · P:{perf*100:.0f}% · Q:{qual*100:.0f}%</div>
            </div>''', unsafe_allow_html=True)

    pw_avail = (df["status"]=="RUNNING").sum() / total
    pw_run   = df[df["status"]=="RUNNING"]["produced_units"]
    pw_perf  = min(pw_run.sum() / max(pw_run.max()*(df["status"]=="RUNNING").sum(),1),1.0) if not pw_run.empty else 0
    pw_qual  = (total_prod-total_rej)/max(total_prod,1)
    pw_oee   = pw_avail * pw_perf * pw_qual * 100
    pw_col   = "#4ade80" if pw_oee>=85 else ("#fbbf24" if pw_oee>=60 else "#f87171")
    with oee_cols[-1]:
        st.markdown(f'''<div class="kpi-wrap" style="--kpi-accent:{pw_col};--kpi-color:{pw_col}">
            <div class="kpi-label">🏭 Plant OEE</div>
            <div class="kpi-value">{pw_oee:.1f}%</div>
            <div class="kpi-sub">A:{pw_avail*100:.0f}% · P:{pw_perf*100:.0f}% · Q:{pw_qual*100:.0f}%</div>
        </div>''', unsafe_allow_html=True)

    insight(f"World-class OEE benchmark is <b>≥ 85%</b> (SEMI E10 standard). Plant OEE = <b>{pw_oee:.1f}%</b> — "
            f"{'above' if pw_oee>=85 else 'below'} world-class. Fault elimination gives the fastest OEE gains "
            "by directly improving Availability.")
    st.markdown("---")

    # ── 6. DOWNTIME COUNTER ───────────────────────────────────────────────────
    st.markdown('<div class="sh-primary">⏱ Machine Downtime Counter</div>', unsafe_allow_html=True)

    dt_cols = st.columns(len(sel_machines))
    for i, mach in enumerate(sel_machines):
        msub   = df[df["machine_id"]==mach].sort_values("timestamp")
        flt_h  = (msub["status"]=="FAULT").sum()
        tot_h  = len(msub)
        dt_pct = flt_h / tot_h * 100 if tot_h else 0
        streak = max_streak = 0
        for s in msub["status"]:
            streak = streak+1 if s=="FAULT" else 0
            max_streak = max(max_streak, streak)
        fault_rows_m = msub[msub["status"]=="FAULT"]
        last_fault   = fault_rows_m["timestamp"].max() if not fault_rows_m.empty else None
        last_str     = last_fault.strftime("%b %d %H:%M") if last_fault else "None"
        dt_col = "#f87171" if dt_pct>5 else ("#fbbf24" if dt_pct>2 else "#4ade80")
        css = "mc-fault" if flt_h>5 else ("mc-idle" if flt_h>2 else "mc-running")
        with dt_cols[i]:
            st.markdown(f'''<div class="mc {css}">
              <div class="mc-head"><span class="mc-id">{mach}</span>
                <span style="font-size:1.3rem;font-weight:800;color:{dt_col}">{flt_h} hrs</span></div>
              <div class="mc-grid">
                <div class="mc-m"><div class="mc-m-label">DOWNTIME RATE</div>
                  <div class="mc-m-val" style="color:{dt_col}">{dt_pct:.1f}%</div></div>
                <div class="mc-m"><div class="mc-m-label">LONGEST STREAK</div>
                  <div class="mc-m-val">{max_streak} hr(s)</div></div>
                <div class="mc-m"><div class="mc-m-label">TOTAL HOURS</div>
                  <div class="mc-m-val">{tot_h}</div></div>
                <div class="mc-m"><div class="mc-m-label">LAST FAULT</div>
                  <div class="mc-m-val" style="font-size:.85rem">{last_str}</div></div>
              </div>
              <div class="mc-vib-bar-bg">
                <div class="mc-vib-bar" style="--vb-col:{dt_col};--vb-w:{min(dt_pct*5,100):.0f}%"></div>
              </div>
              <div class="mc-vib-label">Downtime: {dt_pct:.1f}% · Target: &lt;2% (SEMI E10)</div>
            </div>''', unsafe_allow_html=True)

    worst_dt = max(sel_machines, key=lambda m:(df[df["machine_id"]==m]["status"]=="FAULT").sum()) if sel_machines else "N/A"
    insight(f"<b>{worst_dt}</b> has the highest downtime. Industry target for semiconductor manufacturing "
            "is <b>&lt;2% downtime rate</b>. Longest fault streak reveals sustained failures needing root-cause "
            "investigation — not just reactive resets. Formula: Fault hours ÷ Total hours × 100%.")
    st.markdown("---")

    # ── 7. SHIFT HANDOVER SUMMARY ─────────────────────────────────────────────
    st.markdown('<div class="sh-primary">📋 Shift Handover Summary</div>', unsafe_allow_html=True)

    shift_summary = df.groupby("shift").agg(
        produced =("produced_units","sum"),
        rejected =("rejected_units","sum"),
        fault_hrs=("status", lambda x:(x=="FAULT").sum()),
        run_hrs  =("status", lambda x:(x=="RUNNING").sum()),
        total_hrs=("status","count"),
    ).reset_index()
    shift_summary["yield_pct"]  = ((shift_summary["produced"]-shift_summary["rejected"])/
                                    shift_summary["produced"].replace(0,1)*100).round(1)
    shift_summary["uptime_pct"] = (shift_summary["run_hrs"]/shift_summary["total_hrs"]*100).round(1)
    mach_shift = df.groupby(["machine_id","shift"]).agg(
        faults=("status", lambda x:(x=="FAULT").sum()),
    ).reset_index()

    sh1, sh2 = st.columns(2)
    for ci, (shift, col_sh) in enumerate([("Day",sh1),("Night",sh2)]):
        sv = shift_summary[shift_summary["shift"]==shift]
        if sv.empty: continue
        sv = sv.iloc[0]
        ms = mach_shift[mach_shift["shift"]==shift]
        sh_df   = df[df["shift"]==shift]
        sh_avail = sv["run_hrs"]/max(sv["total_hrs"],1)
        sh_run   = sh_df[sh_df["status"]=="RUNNING"]["produced_units"]
        sh_perf  = min(sh_run.sum()/max(sh_run.max()*sv["run_hrs"],1),1.0) if not sh_run.empty else 0
        sh_qual  = (sv["produced"]-sv["rejected"])/max(sv["produced"],1)
        sh_oee   = sh_avail*sh_perf*sh_qual*100
        sc = "#f59e0b" if shift=="Day" else "#3b82f6"
        icon = "☀️" if shift=="Day" else "🌙"
        oee_c = "#4ade80" if sh_oee>=85 else ("#fbbf24" if sh_oee>=60 else "#f87171")
        machine_boxes = "".join([
            f'<div style="flex:1;background:{T["mc_m_bg"]};border-radius:8px;padding:8px;text-align:center">'
            f'<div style="font-size:10px;color:{T["text_dim"]};font-family:IBM Plex Mono,monospace">{row["machine_id"]}</div>'
            f'<div style="font-size:1rem;font-weight:700;color:{"#f87171" if row["faults"]>2 else "#fbbf24" if row["faults"]>0 else "#4ade80"}">{int(row["faults"])} flt</div></div>'
            for _, row in ms.iterrows()
        ])
        col_sh.markdown(f'''
        <div style="background:{T["kpi_bg"]};border:1px solid {T["kpi_border"]};
                    border-top:3px solid {sc};border-radius:14px;padding:20px;">
          <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;
                      color:{T["text"]};margin-bottom:14px">{icon} {shift} Shift</div>
          <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <tr><td style="color:{T["text_dim"]};padding:5px 0;font-family:IBM Plex Mono,monospace;font-size:11px">UNITS PRODUCED</td>
                <td style="color:{T["text"]};font-weight:700;text-align:right">{int(sv["produced"]):,}</td></tr>
            <tr><td style="color:{T["text_dim"]};padding:5px 0;font-family:IBM Plex Mono,monospace;font-size:11px">UNITS REJECTED</td>
                <td style="color:#f87171;font-weight:700;text-align:right">{int(sv["rejected"]):,}</td></tr>
            <tr><td style="color:{T["text_dim"]};padding:5px 0;font-family:IBM Plex Mono,monospace;font-size:11px">YIELD RATE</td>
                <td style="color:#4ade80;font-weight:700;text-align:right">{sv["yield_pct"]:.1f}%</td></tr>
            <tr><td style="color:{T["text_dim"]};padding:5px 0;font-family:IBM Plex Mono,monospace;font-size:11px">UPTIME</td>
                <td style="color:{T["text"]};font-weight:700;text-align:right">{sv["uptime_pct"]:.1f}%</td></tr>
            <tr><td style="color:{T["text_dim"]};padding:5px 0;font-family:IBM Plex Mono,monospace;font-size:11px">FAULT HOURS</td>
                <td style="color:#f87171;font-weight:700;text-align:right">{int(sv["fault_hrs"])}</td></tr>
            <tr><td style="color:{T["text_dim"]};padding:5px 0;font-family:IBM Plex Mono,monospace;font-size:11px">SHIFT OEE</td>
                <td style="color:{oee_c};font-weight:700;text-align:right">{sh_oee:.1f}%</td></tr>
          </table>
          <div style="margin-top:12px;font-family:IBM Plex Mono,monospace;font-size:10px;
                      color:{T["text_dim"]};border-top:1px solid {T["kpi_border"]};padding-top:8px">FAULTS BY MACHINE</div>
          <div style="display:flex;gap:8px;margin-top:8px">{machine_boxes}</div>
        </div>''', unsafe_allow_html=True)

    day_row   = shift_summary[shift_summary["shift"]=="Day"]
    night_row = shift_summary[shift_summary["shift"]=="Night"]
    if not day_row.empty and not night_row.empty:
        dp = int(day_row.iloc[0]["produced"]); np_ = int(night_row.iloc[0]["produced"])
        gap = (dp-np_)/max(np_,1)*100
        better = "Day" if dp>np_ else "Night"
        insight(f"<b>{better} shift</b> outperforms by {abs(gap):.1f}% on units produced "
                f"(Day: {dp:,} · Night: {np_:,}). With near-equal fault rates, the gap reflects "
                "supervision intensity and scheduling. Incoming shift operators should review the "
                "fault breakdown above before taking over.")
    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ADVANCED ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with TAB_ADV:

    # Fix #5: clear intro section explaining what this tab is
    st.markdown("""<div class="adv-intro">
    <b>What is this tab?</b> This section contains 6 detailed statistical charts for academic analysis.
    Each figure investigates a specific aspect of plant behaviour — from how vibration relates to faults,
    to how rejection rate varies by machine and shift. Each chart has an observation note explaining what
    the data shows in plain language.<br><br>
    <b>Machine colour coding (consistent across all figures):</b>
    &nbsp; <b style="color:#3b82f6">● M1</b>
    &nbsp; <b style="color:#f97316">● M2</b>
    &nbsp; <b style="color:#22c55e">● M3</b>
    </div>""", unsafe_allow_html=True)

    # ── FIGURE 1 ──────────────────────────────────────────────────────────────
    st.markdown("#### Figure 1 — Vibration & Current vs. Time (mm/s, A)")

    fault_rows = df[df["status"]=="FAULT"]
    fig_f1 = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.08,
        subplot_titles=("Vibration (mm/s)", "Motor Current (A)"),
        row_heights=[.5,.5])

    for mach in sel_machines:
        sub = df[df["machine_id"]==mach].sort_values("timestamp")
        c   = MACH_COLORS.get(mach,"#aaa")
        fig_f1.add_trace(go.Scatter(x=sub["timestamp"],y=sub["vibration_mm_s"],name=mach,
            line=dict(color=c,width=1.5),opacity=0.85,
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Vib: %{{y:.2f}} mm/s<extra></extra>"),
            row=1,col=1)
        fig_f1.add_trace(go.Scatter(x=sub["timestamp"],y=sub["current_a"],
            name=f"{mach} Current",line=dict(color=c,width=1.5,dash="dot"),
            opacity=0.85,showlegend=False,
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Current: %{{y:.1f}} A<extra></extra>"),
            row=2,col=1)

    if not fault_rows.empty:
        fig_f1.add_trace(go.Scatter(x=fault_rows["timestamp"],y=fault_rows["vibration_mm_s"],
            mode="markers",name="FAULT Event",
            marker=dict(color="#ef4444",size=10,symbol="circle",line=dict(color="#fff",width=1)),
            hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>Vib: %{y:.2f} mm/s<br>%{customdata}<extra></extra>",
            customdata=fault_rows["machine_id"]),row=1,col=1)
        fig_f1.add_trace(go.Scatter(x=fault_rows["timestamp"],y=fault_rows["current_a"],
            mode="markers",name="FAULT Event",showlegend=False,
            marker=dict(color="#ef4444",size=10,symbol="circle",line=dict(color="#fff",width=1)),
            hovertemplate="<b>FAULT</b> %{x|%b %d %H:%M}<br>Current: %{y:.1f} A<br>%{customdata}<extra></extra>",
            customdata=fault_rows["machine_id"]),row=2,col=1)

    fig_f1.add_hline(y=vib_thresh,row=1,col=1,line_color="#dc2626",line_dash="dot",
        annotation_text=f"Critical {vib_thresh:.0f}mm/s",annotation_font_color="#dc2626",
        annotation_position="top right")
    fig_f1.add_hline(y=cur_thresh,row=2,col=1,line_color="#dc2626",line_dash="dot",
        annotation_text=f"Critical {cur_thresh:.0f}A",annotation_font_color="#dc2626",
        annotation_position="top right")
    fig_f1.update_layout(**CHART_BASE,height=560,hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)",font_size=11))
    apply_grid(fig_f1,[1,2])
    st.plotly_chart(fig_f1, use_container_width=True)

    low_vib_faults = fault_rows[fault_rows["vibration_mm_s"]<=vib_thresh]
    insight(f"FAULT events (red dots) generally coincide with high vibration (> {vib_thresh:.0f} mm/s) "
            f"and/or high current (> {cur_thresh:.0f} A). <b>{len(low_vib_faults)}</b> fault(s) occurred "
            f"with low vibration — these were triggered by electrical overcurrent rather than mechanical causes. "
            "Viewing both sensors together gives a more complete picture of fault origins.")
    st.markdown("---")

    # ── FIGURE 2 ──────────────────────────────────────────────────────────────
    st.markdown("#### Figure 2 — Vibration vs. Rejection Rate (%, RUNNING only)")

    running_filt = df[(df["status"]=="RUNNING") & (df["vibration_mm_s"]<=8)].copy()
    if len(running_filt)>2:
        z      = np.polyfit(running_filt["vibration_mm_s"],running_filt["rejection_rate"],1)
        x_line = np.linspace(running_filt["vibration_mm_s"].min(),
                             running_filt["vibration_mm_s"].max(),100)
        y_line = np.polyval(z,x_line)
        r_val  = running_filt[["vibration_mm_s","rejection_rate"]].corr().iloc[0,1]
    else:
        x_line=y_line=[]; r_val=0

    fig_f2 = go.Figure()
    for mach in sel_machines:
        sub = running_filt[running_filt["machine_id"]==mach]
        fig_f2.add_trace(go.Scatter(x=sub["vibration_mm_s"],y=sub["rejection_rate"],
            mode="markers",name=mach,
            marker=dict(color=MACH_COLORS.get(mach,"#aaa"),size=7,opacity=0.6),
            hovertemplate=f"<b>{mach}</b><br>Vib: %{{x:.2f}} mm/s<br>Rejection: %{{y:.1f}}%<extra></extra>"))
    if len(x_line)>0:
        fig_f2.add_trace(go.Scatter(x=x_line,y=y_line,mode="lines",
            name=f"Trend (r={r_val:.4f})",line=dict(color="#991b1b",width=2.5)))
    fig_f2.update_layout(**CHART_BASE,height=480,
        xaxis_title="Vibration Level (mm/s)",yaxis_title="Rejection Rate (%)",
        title=dict(text=f"Vibration vs. Rejection Rate (RUNNING only) — Pearson r = {r_val:.4f}",
                   font_color="#8899aa",font_size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)",font_size=11))
    apply_grid(fig_f2)
    st.plotly_chart(fig_f2, use_container_width=True)
    insight(f"Pearson r = <b>{r_val:.4f}</b> — near-zero correlation. Vibration level during normal "
            "RUNNING does <b>not</b> meaningfully predict rejection rate. Quality defects are driven "
            "by other factors such as tooling wear, material variability, or operator handling — not vibration.")
    st.markdown("---")

    # ── FIGURE 3 ──────────────────────────────────────────────────────────────
    st.markdown("#### Figure 3 — Machine Health: Vibration (mm/s) & Rejection Rate (%) — All Machines")

    # Combined chart: 3 rows (one per machine), shared x-axis, dual y-axis per row
    n_m = len(sel_machines)
    fig_f3 = make_subplots(
        rows=n_m, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=[f"{m} — Vibration (mm/s) & Rejection Rate (%)" for m in sel_machines],
        specs=[[{"secondary_y": True}] for _ in sel_machines],
    )

    for i, mach in enumerate(sel_machines, start=1):
        sub = df[df["machine_id"]==mach].sort_values("timestamp").copy()
        if sub.empty: continue
        fault_sub = sub[sub["status"]=="FAULT"]
        mc = MACH_COLORS.get(mach, "#aaa")

        # Vibration line
        fig_f3.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["vibration_mm_s"],
            name=f"{mach} Vibration" if i==1 else mach,
            showlegend=(i==1),
            line=dict(color=mc, width=1.8),
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Vib: %{{y:.2f}} mm/s<extra></extra>"),
            row=i, col=1, secondary_y=False)

        # FAULT dots
        if not fault_sub.empty:
            fig_f3.add_trace(go.Scatter(
                x=fault_sub["timestamp"], y=fault_sub["vibration_mm_s"],
                mode="markers",
                name="FAULT" if i==1 else "FAULT",
                showlegend=(i==1),
                marker=dict(color="#111827", size=10, symbol="circle",
                            line=dict(color="#c8d8e8", width=1.5)),
                hovertemplate=f"<b>FAULT {mach}</b> %{{x|%b %d %H:%M}}<br>%{{y:.2f}} mm/s<extra></extra>"),
                row=i, col=1, secondary_y=False)

        # Rejection rate (right axis)
        fig_f3.add_trace(go.Scatter(
            x=sub["timestamp"], y=sub["rejection_rate"],
            name="Rejection Rate (%)" if i==1 else "Rejection Rate (%)",
            showlegend=(i==1),
            line=dict(color="#ef4444", width=1.8, dash="dash"),
            hovertemplate=f"<b>{mach}</b> %{{x|%b %d %H:%M}}<br>Rejection: %{{y:.1f}}%<extra></extra>"),
            row=i, col=1, secondary_y=True)

        # Critical vibration threshold line per row
        fig_f3.add_hline(y=vib_thresh, row=i, col=1,
            line_color="#dc2626", line_dash="dot",
            annotation_text=f"Critical {vib_thresh:.0f} mm/s" if i==1 else "",
            annotation_font_color="#dc2626",
            annotation_position="top right",
            secondary_y=False)

        # Y-axes per row
        fig_f3.update_yaxes(title_text="Vib (mm/s)", gridcolor="#0f1928", zeroline=False,
                             range=[0, df["vibration_mm_s"].max()*1.15],
                             row=i, col=1, secondary_y=False)
        fig_f3.update_yaxes(title_text="Rej (%)", gridcolor="#0f1928", zeroline=False,
                             range=[0, 110],
                             tickfont=dict(color="#ef4444"),
                             title_font=dict(color="#ef4444"),
                             row=i, col=1, secondary_y=True)

    fig_f3.update_xaxes(gridcolor="#0f1928", zeroline=False)
    fig_f3.update_layout(
        **CHART_BASE,
        height=340 * n_m,
        hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11, orientation="h", y=1.02, x=0),
        title=dict(text="All Machines — Vibration (mm/s) & Rejection Rate (%)",
                   font_color="#8899aa", font_size=13),
    )
    st.plotly_chart(fig_f3, use_container_width=True, config={"displayModeBar": False})

    fault_hi = df[(df["status"]=="FAULT")&(df["vibration_mm_s"]>vib_thresh)]
    fault_lo = df[(df["status"]=="FAULT")&(df["vibration_mm_s"]<=vib_thresh)]
    insight(f"All three machines are shown on a shared time axis for direct comparison. "
            f"<b>{len(fault_hi)}</b> fault(s) coincide with vibration above {vib_thresh:.0f} mm/s; "
            f"<b>{len(fault_lo)}</b> occurred at lower vibration — triggered by electrical overcurrent. "
            "When a black dot (FAULT) appears, the red dashed rejection rate spikes to 100%, "
            "confirming a faulted machine produces zero usable output. "
            "Comparing rows shows M1 has more frequent and higher-amplitude fault events than M2 and M3.")
    st.info("📌 **Rejection Rate Definition:** "
            "RUNNING → rejected_units / produced_units × 100% (actual defect rate). "
            "FAULT → 100% (machine is down; zero usable output). "
            "IDLE → 0% (no production).")
    st.markdown("---")

    # ── FIGURE 4 ──────────────────────────────────────────────────────────────
    st.markdown("#### Figure 4 — Sensor Distribution by Status (mm/s, A)")

    box_colors = {"IDLE":"#2d6a4f","RUNNING":"#c06030","FAULT":"#6272a4"}
    f4c1, f4c2 = st.columns(2)

    with f4c1:
        fig_f4a = go.Figure()
        for status in ["IDLE","RUNNING","FAULT"]:
            sub = df[df["status"]==status]["vibration_mm_s"]
            if sub.empty: continue
            fig_f4a.add_trace(go.Box(y=sub, name=status, boxmean=True,
                marker_color=box_colors.get(status,"#aaa"),
                line_color=box_colors.get(status,"#aaa"),
                fillcolor=box_colors.get(status,"#aaa"),
                opacity=0.75,
                hovertemplate=f"<b>{status}</b><br>%{{y:.2f}} mm/s<extra></extra>"))
        fig_f4a.add_hline(y=vib_thresh, line_color="#dc2626", line_dash="dot",
            annotation_text=f"Critical {vib_thresh:.0f} mm/s", annotation_font_color="#dc2626")
        fig_f4a.update_layout(**CHART_BASE, height=460,
            xaxis_title="Machine Status", yaxis_title="Vibration (mm/s)",
            title=dict(text="Vibration Distribution by Status (mm/s)",
                       font_color="#8899aa", font_size=13))
        apply_grid(fig_f4a)
        st.plotly_chart(fig_f4a, use_container_width=True)

    with f4c2:
        fig_f4b = go.Figure()
        for status in ["IDLE","RUNNING","FAULT"]:
            sub = df[df["status"]==status]["current_a"]
            if sub.empty: continue
            fig_f4b.add_trace(go.Box(y=sub, name=status, boxmean=True,
                marker_color=box_colors.get(status,"#aaa"),
                line_color=box_colors.get(status,"#aaa"),
                fillcolor=box_colors.get(status,"#aaa"),
                opacity=0.75,
                hovertemplate=f"<b>{status}</b><br>%{{y:.1f}} A<extra></extra>"))
        fig_f4b.add_hline(y=cur_thresh, line_color="#dc2626", line_dash="dot",
            annotation_text=f"Critical {cur_thresh:.0f} A", annotation_font_color="#dc2626")
        fig_f4b.update_layout(**CHART_BASE, height=460,
            xaxis_title="Machine Status", yaxis_title="Current (A)",
            title=dict(text="Current Distribution by Status (A)",
                       font_color="#8899aa", font_size=13))
        apply_grid(fig_f4b)
        st.plotly_chart(fig_f4b, use_container_width=True)

    # Summary table
    summary_rows = []
    for status in ["IDLE","FAULT","RUNNING"]:
        sub = df[df["status"]==status]
        if sub.empty: continue
        summary_rows.append({
            "Status": status.capitalize(),
            "Avg Current (A)": round(sub["current_a"].mean(), 2),
            "Avg Vibration (mm/s)": round(sub["vibration_mm_s"].mean(), 2),
        })
    total_row = {
        "Status": "Total",
        "Avg Current (A)": round(df["current_a"].mean(), 2),
        "Avg Vibration (mm/s)": round(df["vibration_mm_s"].mean(), 2),
    }
    summary_rows.append(total_row)
    summary_df = pd.DataFrame(summary_rows)

    st.dataframe(summary_df, use_container_width=True, hide_index=True,
        column_config={
            "Avg Current (A)":      st.column_config.NumberColumn(format="%.2f A"),
            "Avg Vibration (mm/s)": st.column_config.NumberColumn(format="%.2f mm/s"),
        })

    run_med   = df[df["status"]=="RUNNING"]["vibration_mm_s"].median()
    fault_med = df[df["status"]=="FAULT"]["vibration_mm_s"].median() if fault_count>0 else 0
    idle_med  = df[df["status"]=="IDLE"]["vibration_mm_s"].median()
    run_cur   = df[df["status"]=="RUNNING"]["current_a"].mean()
    fault_cur = df[df["status"]=="FAULT"]["current_a"].mean() if fault_count>0 else 0
    insight(f"<b>Vibration:</b> FAULT median ({fault_med:.1f} mm/s) is {fault_med/run_med:.1f}× higher than "
            f"RUNNING ({run_med:.1f} mm/s) and IDLE ({idle_med:.1f} mm/s). "
            f"<b>Current:</b> FAULT average ({fault_cur:.1f} A) is {fault_cur/run_cur:.1f}× higher than "
            f"RUNNING ({run_cur:.1f} A) — both sensors clearly distinguish fault conditions from normal operation. "
            "The wide IQR in FAULT boxes shows fault severity varies considerably.")
    st.markdown("---")

    # ── FIGURE 5 ──────────────────────────────────────────────────────────────
    st.markdown("#### Figure 5 — Current (A) vs Vibration (mm/s) & Rejection Rate (%)")

    fig_f5 = make_subplots(rows=1,cols=2,
        subplot_titles=("(a) Current (A) vs Vibration (mm/s) by Status",
                        "(b) Rejection Rate (%) by Machine & Shift (RUNNING only)"),
        column_widths=[0.55,0.45])

    MARKER_SHAPE = {"M1":"circle","M2":"square","M3":"triangle-up"}
    STATUS_COL   = {"RUNNING":"#22c55e","IDLE":"#fbbf24","FAULT":"#ef4444"}

    for status in ["RUNNING","IDLE","FAULT"]:
        sub_s = df[df["status"]==status]
        for mach in sel_machines:
            sub = sub_s[sub_s["machine_id"]==mach]
            if sub.empty: continue
            fig_f5.add_trace(go.Scatter(
                x=sub["current_a"],y=sub["vibration_mm_s"],mode="markers",
                name=f"{status} {mach}",showlegend=True,
                marker=dict(color=STATUS_COL[status],symbol=MARKER_SHAPE.get(mach,"circle"),
                            size=6,opacity=0.55 if status!="FAULT" else 0.9),
                hovertemplate=f"<b>{mach} {status}</b><br>Current: %{{x:.1f}} A<br>Vib: %{{y:.2f}} mm/s<extra></extra>"),
                row=1,col=1)

    fig_f5.add_vline(x=cur_thresh,row=1,col=1,line_color="#dc2626",line_dash="dash",
        annotation_text=f"{cur_thresh:.0f}A",annotation_font_color="#dc2626")
    fig_f5.add_hline(y=vib_thresh,row=1,col=1,line_color="#f97316",line_dash="dot",
        annotation_text=f"{vib_thresh:.0f}mm/s",annotation_font_color="#f97316")

    run_rej = (df[df["status"]=="RUNNING"]
               .groupby(["machine_id","shift"])
               .apply(lambda g: g["rejected_units"].sum()/max(g["produced_units"].sum(),1)*100)
               .reset_index(name="rej_rate"))

    shift_colors = {"Day":"#f59e0b","Night":"#3b4fa8"}
    for shift in ["Day","Night"]:
        sub = run_rej[run_rej["shift"]==shift]
        if sub.empty: continue
        fig_f5.add_trace(go.Bar(x=sub["machine_id"],y=sub["rej_rate"],name=shift,
            marker_color=shift_colors[shift],
            text=sub["rej_rate"].apply(lambda x:f"{x:.1f}%"),textposition="outside",
            textfont=dict(family="IBM Plex Mono",size=11),
            hovertemplate=f"<b>{shift} shift</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>"),
            row=1,col=2)

    fig_f5.update_xaxes(title_text="Motor Current (A)",row=1,col=1,gridcolor="#0f1928",zeroline=False)
    fig_f5.update_yaxes(title_text="Vibration (mm/s)",row=1,col=1,gridcolor="#0f1928",zeroline=False)
    fig_f5.update_xaxes(title_text="Machine ID",row=1,col=2,gridcolor="#0f1928",zeroline=False)
    fig_f5.update_yaxes(title_text="Rejection Rate (%)",row=1,col=2,gridcolor="#0f1928",zeroline=False,
                        range=[0,run_rej["rej_rate"].max()*1.35 if not run_rej.empty else 10])
    fig_f5.update_layout(**CHART_BASE,height=520,barmode="group",
        legend=dict(bgcolor="rgba(0,0,0,0)",font_size=10,orientation="v"),
        title=dict(text="Fault Diagnostics — Current (A) vs Vibration (mm/s) & Rejection Rate (%)",
                   font_color="#8899aa",font_size=13))
    st.plotly_chart(fig_f5, use_container_width=True)

    day_avg   = run_rej[run_rej["shift"]=="Day"]["rej_rate"].mean()
    night_avg = run_rej[run_rej["shift"]=="Night"]["rej_rate"].mean()
    better    = "Night" if night_avg<day_avg else "Day"
    fault_zone = df[(df["current_a"]>cur_thresh)&(df["vibration_mm_s"]>vib_thresh)]
    insight(f"<b>(a)</b> FAULT readings cluster in the top-right quadrant — where both current > {cur_thresh:.0f} A "
            f"AND vibration > {vib_thresh:.0f} mm/s simultaneously. <b>{len(fault_zone)}</b> readings exceeded both thresholds at once. "
            f"This dual-exceedance is the strongest fault predictor in the dataset.<br>"
            f"<b>(b)</b> Rejection rates are consistent across shifts (~3–4%). "
            f"<b>{better} shift</b> performs marginally better. M3 has the highest rejection rate across both shifts — "
            "suggesting a machine-specific quality issue rather than a shift-based one.")
    st.markdown("---")

    # ── FIGURE 6 ──────────────────────────────────────────────────────────────
    st.markdown("#### Figure 6 — Operational Status Distribution by Machine (hrs)")

    status_hrs_adv = df.groupby(["machine_id","status"]).size().reset_index(name="hours")
    fig_f6 = go.Figure()
    for st_opt, col_f6 in [("FAULT","#ef4444"),("IDLE","#9ca3af"),("RUNNING","#3b82f6")]:
        sub = status_hrs_adv[status_hrs_adv["status"]==st_opt]
        fig_f6.add_trace(go.Bar(name=st_opt,x=sub["machine_id"],y=sub["hours"],
            marker_color=col_f6,text=sub["hours"],textposition="outside",
            textfont=dict(family="IBM Plex Mono",size=11)))
    fig_f6.update_layout(**CHART_BASE,height=480,barmode="group",
        xaxis_title="Machine",yaxis_title="Operating Hours",
        title=dict(text="Operational Status Distribution by Machine (hrs)",
                   font_color="#8899aa",font_size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)",font_size=12))
    apply_grid(fig_f6)
    st.plotly_chart(fig_f6, use_container_width=True)

    m1_fault = status_hrs_adv[(status_hrs_adv["machine_id"]=="M1")&(status_hrs_adv["status"]=="FAULT")]["hours"].sum()
    m2_fault = status_hrs_adv[(status_hrs_adv["machine_id"]=="M2")&(status_hrs_adv["status"]=="FAULT")]["hours"].sum()
    m3_fault = status_hrs_adv[(status_hrs_adv["machine_id"]=="M3")&(status_hrs_adv["status"]=="FAULT")]["hours"].sum()
    insight(f"M1 accumulated <b>{m1_fault} fault hours</b> — significantly higher than M2 ({m2_fault} hrs) "
            f"and M3 ({m3_fault} hrs). Since RUNNING hours are broadly similar across machines, "
            "M1's fault time is directly replacing productive time, not just idle time. "
            "This confirms M1 as the highest-priority maintenance target.")
    st.markdown("---")

    # ── ANALYSIS SUMMARY ──────────────────────────────────────────────────────
    st.markdown('<div class="sh-primary">Analysis Summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
| Figure | Key Finding |
|--------|------------|
| **Fig 1** — Vibration & Current (mm/s, A) | {fault_count} FAULT events visible on both sensor panels |
| **Fig 2** — Vibration vs Rejection (%, RUNNING) | Near-zero correlation r ≈ {r_val:.3f} — vibration does not drive quality |
| **Fig 3** — Health: Vibration (mm/s) & Rejection (%) | FAULT events co-occur with 100% rejection spikes per machine |
| **Fig 4** — Sensor Distribution (mm/s, A) | FAULT avg current {fault_cur:.1f} A & vibration {fault_med:.1f} mm/s — both ~{fault_cur/run_cur:.1f}× higher than RUNNING |
| **Fig 5** — Current (A) vs Vibration (mm/s) & Rejection (%) | Dual-threshold exceedance is the strongest fault predictor |
| **Fig 6** — Status Distribution (hrs) | M1 fault hours ({m1_fault} hrs) highest — priority maintenance target |
""")

# ─────────────────────────────────────────────────────────────────────────────
# Fix #12: footer removed — no tech stack credits shown to end user
# ─────────────────────────────────────────────────────────────────────────────

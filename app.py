import streamlit as st
import streamlit.components.v1 as components

from auth import login
from sheets import load_data
from dashboard import show_dashboard

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Machining Analytics Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800;900&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

/* =========================================
   HIDE STREAMLIT DEFAULT UI
========================================= */

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* =========================================
   REMOVE TOP PADDING
========================================= */

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 0rem;
    padding-left: 3rem;
    padding-right: 2rem;
}

/* =========================================
   MAIN BACKGROUND
========================================= */

.stApp {
    background:
        linear-gradient(135deg,
            rgba(2, 10, 28, 0.93) 0%,
            rgba(5, 18, 45, 0.88) 50%,
            rgba(2, 10, 28, 0.95) 100%
        ),
        url("https://images.unsplash.com/photo-1565043666747-69f6646db940?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Inter', sans-serif;
}

/* =========================================
   LEFT PANEL
========================================= */

.left-panel {
    padding-top: 10px;
    color: white;
    position: relative;
}

.main-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: clamp(52px, 6vw, 76px);
    font-weight: 900;
    line-height: 1.0;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #ffffff;
    margin-bottom: 0px;
}

.blue-text {
    color: #2e8de8;
}

.headline-rule {
    width: 50px;
    height: 3px;
    background: #cc1f24;
    border-radius: 2px;
    margin: 18px 0 20px 0;
}

.sub-text {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 300;
    color: rgba(220, 230, 245, 0.78);
    line-height: 1.75;
    width: 82%;
    margin-bottom: 40px;
}

/* =========================================
   LOGIN PANEL
========================================= */

.login-panel {
    background: #f4f7fc;
    border-radius: 20px;
    padding: 32px 28px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;
}

.login-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #cc1f24 0%, #2e8de8 100%);
}

.stTextInput label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    color: #4a5e78 !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}

.stTextInput input {
    border-radius: 12px !important;
    padding: 14px 16px !important;
    border: 1.5px solid #d0d9e8 !important;
    font-size: 15px !important;
    font-family: 'Inter', sans-serif !important;
    background: #ffffff !important;
    color: #0d1f3c !important;
    box-shadow: 0 2px 6px rgba(13, 31, 60, 0.07) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.stTextInput input:focus {
    border-color: #1a6fc4 !important;
    box-shadow: 0 0 0 3px rgba(26, 111, 196, 0.14), 0 2px 6px rgba(13,31,60,0.07) !important;
    outline: none !important;
}

.stTextInput input::placeholder {
    color: #a0b0c8 !important;
    font-weight: 300 !important;
}

.stButton > button {
    width: 100% !important;
    border-radius: 12px !important;
    background: #0d1f3c !important;
    color: #ffffff !important;
    border: none !important;
    padding: 15px 24px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    margin-top: 10px !important;
    box-shadow: 0 6px 20px rgba(13, 31, 60, 0.4) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #1a2f52 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(13, 31, 60, 0.5) !important;
}

@media (max-width: 900px) {
    .main-title { font-size: 42px; }
    .sub-text { width: 100%; font-size: 15px; }
    .login-panel { margin-top: 20px; padding: 28px 24px; }
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    left, right = st.columns([1.6, 1])

    with left:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-bottom:28px;">
            <div style="font-family:'Rajdhani',sans-serif;color:#2e8de8;font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">Software Designed By</div>
            <div style="font-family:'Barlow Condensed',sans-serif;color:#ffffff;font-size:22px;font-weight:700;line-height:1.2;letter-spacing:0.5px;">Manufacturing Minds<br>Precision LLP</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="main-title">
            PRECISION DATA.<br>
            <span class="blue-text">SMARTER</span> MANUFACTURING.
        </div>
        <div class="headline-rule"></div>
        <div class="sub-text">
            Real-time insights. Intelligent analytics.<br>
            Better decisions for a stronger tomorrow.
        </div>
        """, unsafe_allow_html=True)

        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@800&family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
        <style>
            * { margin:0; padding:0; box-sizing:border-box; }
            body { background:transparent; }
            .cards { display:flex; gap:16px; flex-wrap:wrap; }
            .card {
                min-width:150px;
                background:rgba(255,255,255,0.05);
                border:1px solid rgba(255,255,255,0.12);
                border-radius:16px;
                padding:20px 22px;
                transition:all 0.28s ease;
                cursor:default;
            }
            .card:hover { transform:translateY(-4px); border-color:rgba(46,141,232,0.45); background:rgba(30,111,196,0.13); }
            .label { font-family:'Rajdhani',sans-serif; color:#8aaacf; font-size:11px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; margin-bottom:10px; }
            .value { font-family:'Barlow Condensed',sans-serif; color:#2e8de8; font-size:44px; font-weight:800; line-height:1; }
            .footer { display:flex; gap:32px; margin-top:32px; padding-top:18px; border-top:1px solid rgba(255,255,255,0.1); flex-wrap:wrap; }
            .pillar { display:flex; align-items:center; gap:8px; }
            .pillar-text { font-family:'Rajdhani',sans-serif; color:#7a94b8; font-size:13px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; }
        </style>
        <div class="cards">
            <div class="card"><div class="label">OEE</div><div class="value">87%</div></div>
            <div class="card"><div class="label">Production Trend</div><div class="value">↑ 1240</div></div>
            <div class="card"><div class="label">Spindle Load</div><div class="value">65%</div></div>
        </div>
        <div class="footer">
            <div class="pillar"><span>⊕</span><span class="pillar-text">Measure.</span></div>
            <div class="pillar"><span>📊</span><span class="pillar-text">Analyze.</span></div>
            <div class="pillar"><span>📈</span><span class="pillar-text">Optimize.</span></div>
            <div class="pillar"><span>🏆</span><span class="pillar-text">Perform.</span></div>
        </div>
        """, height=240, scrolling=False)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="login-panel">', unsafe_allow_html=True)

        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:14px;">
            <div style="flex:1;height:1px;background:#d0d9e8;"></div>
            <span style="font-family:'Rajdhani',sans-serif;color:#7a8fa8;font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;white-space:nowrap;">Kisaan DieTech</span>
            <div style="flex:1;height:1px;background:#d0d9e8;"></div>
        </div>
        
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:8px;margin-bottom:22px;">
            <div style="width:28px;height:1px;background:#cc1f24;"></div>
            <span style="font-family:'Rajdhani',sans-serif;font-size:9px;font-weight:700;letter-spacing:2.5px;color:#8a9ab8;text-transform:uppercase;">Precision In Every Detail</span>
            <div style="width:28px;height:1px;background:#cc1f24;"></div>
        </div>

        <div style="border-top:1px solid #e0e7f0;margin:0 0 22px 0;"></div>

        <div style="text-align:center;font-size:32px;margin-bottom:12px;">⚙️</div>

        <div style="font-family:'Barlow Condensed',sans-serif;text-align:center;color:#0d1f3c;font-size:34px;font-weight:800;letter-spacing:0.5px;margin-bottom:6px;">Welcome Back</div>

        <div style="text-align:center;color:#6b7f99;font-family:'Inter',sans-serif;font-size:13px;font-weight:400;line-height:1.5;margin-bottom:28px;">
            Login to access your machining analytics dashboard.
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter Username")
        password = st.text_input("Password", type="password", placeholder="Enter Password")

        if st.button("LOGIN"):
            if login(username, password):
                st.session_state.logged_in = True
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Username or Password")

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# MAIN DASHBOARD
# =========================================================

else:
    with st.spinner("Loading Dashboard..."):
        df = load_data()

    show_dashboard(df)

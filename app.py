import streamlit as st
import streamlit.components.v1 as components
import base64
import os

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
# HELPER: embed local image as base64 (so it can sit inside
# our custom HTML/CSS layout instead of a plain st.image box)
# =========================================================
def get_base64_image(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


MM_LOGO = get_base64_image("mm_logo.png")
KISAAN_LOGO = get_base64_image("kisaan_logo.png")


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800;900&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 0rem;
    padding-left: 3rem;
    padding-right: 2rem;
}

.stApp {
    background:
        linear-gradient(135deg, rgba(2, 10, 28, 0.93) 0%, rgba(5, 18, 45, 0.88) 50%, rgba(2, 10, 28, 0.95) 100%),
        url("https://images.unsplash.com/photo-1565043666747-69f6646db940?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Inter', sans-serif;
}

/* ---------------- LEFT PANEL ---------------- */
.left-panel { padding-top: 10px; color: white; position: relative; }

.brand-row { display: flex; align-items: center; gap: 18px; margin-bottom: 30px; }
.brand-row img { height: 64px; }
.brand-divider { width: 1px; height: 48px; background: rgba(255,255,255,0.25); }
.brand-credit-label { font-family:'Rajdhani',sans-serif; color:#2e8de8; font-size:11px; font-weight:600; letter-spacing:3px; text-transform:uppercase; margin-bottom:4px; }
.brand-credit-name { font-family:'Barlow Condensed',sans-serif; color:#ffffff; font-size:20px; font-weight:700; line-height:1.2; }

.main-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: clamp(48px, 5.5vw, 70px);
    font-weight: 900;
    line-height: 1.0;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #ffffff;
    margin-bottom: 0px;
}
.blue-text { color: #2e8de8; }

.headline-rule { width: 50px; height: 3px; background: #cc1f24; border-radius: 2px; margin: 18px 0 20px 0; }

.sub-text {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 300;
    color: rgba(220, 230, 245, 0.78);
    line-height: 1.75;
    width: 82%;
    margin-bottom: 32px;
}

/* ---------------- LOGIN PANEL ---------------- */
/* st.container(key="login_card") renders as a div with
   data-testid="stVerticalBlockBorderWrapper" / class "st-key-login_card".
   We style it from the outside via :has() so we don't depend on manually
   opening/closing a <div> across separate st.markdown() calls (that approach
   breaks because each markdown call is its own isolated HTML fragment). */
div.st-key-login_card,
div.st-key-login_card > div,
div.st-key-login_card [data-testid="stVerticalBlockBorderWrapper"],
div.st-key-login_card [data-testid="stVerticalBlock"] {
    overflow: visible !important;
    height: auto !important;
    max-height: none !important;
}
div.st-key-login_card {
    background: #f4f7fc;
    border-radius: 20px;
    padding: 34px 36px 26px 36px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    position: relative;
}
div.st-key-login_card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #cc1f24 0%, #2e8de8 100%);
    border-radius: 20px 20px 0 0;
}

.designed-for-row { display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:14px; }
.designed-for-row .line { flex:1; height:1px; background:#d0d9e8; }
.designed-for-row .label { font-family:'Rajdhani',sans-serif; color:#7a8fa8; font-size:10px; font-weight:700; letter-spacing:3px; text-transform:uppercase; white-space:nowrap; }

.kisaan-logo-wrap { text-align:center; margin-bottom:6px; }
.kisaan-logo-wrap img { height: 56px; }

.precision-row { display:flex; align-items:center; justify-content:center; gap:8px; margin-top:6px; margin-bottom:20px; }
.precision-row .stub { width:28px; height:1px; background:#cc1f24; }
.precision-row .text { font-family:'Rajdhani',sans-serif; font-size:9px; font-weight:700; letter-spacing:2.5px; color:#8a9ab8; text-transform:uppercase; }

.login-hr { border-top:1px solid #e0e7f0; margin:0 0 18px 0; }

.welcome-icon { text-align:center; font-size:30px; margin-bottom:10px; }
.welcome-title { font-family:'Barlow Condensed',sans-serif; text-align:center; color:#0d1f3c; font-size:32px; font-weight:800; letter-spacing:0.5px; margin-bottom:6px; }
.welcome-sub { text-align:center; color:#6b7f99; font-family:'Inter',sans-serif; font-size:13px; font-weight:400; line-height:1.5; margin-bottom:22px; }

/* Inputs with leading icons -- same st.container(key=...) + :has() pattern */
div.st-key-username_field, div.st-key-password_field {
    position: relative;
    margin-bottom: 6px;
    overflow: visible !important;
    height: auto !important;
}
div.st-key-username_field::after {
    content: '👤';
    position: absolute;
    left: 16px;
    top: 24px;
    transform: translateY(-50%);
    z-index: 5;
    font-size: 15px;
    pointer-events: none;
}
div.st-key-password_field::after {
    content: '🔒';
    position: absolute;
    left: 16px;
    top: 24px;
    transform: translateY(-50%);
    z-index: 5;
    font-size: 14px;
    pointer-events: none;
}
div.st-key-username_field .stTextInput input,
div.st-key-password_field .stTextInput input {
    padding-left: 44px !important;
}

.stTextInput label { display: none !important; }
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
.stTextInput input::placeholder { color: #a0b0c8 !important; font-weight: 300 !important; }

.remember-forgot-row { display:flex; align-items:center; justify-content:space-between; margin: 4px 0 6px 0; }
.remember-forgot-row .left { display:flex; align-items:center; gap:8px; }
.remember-forgot-row .left span { font-family:'Inter',sans-serif; font-size:13px; color:#4a5e78; }
.remember-forgot-row .right a { font-family:'Inter',sans-serif; font-size:13px; color:#1a6fc4; text-decoration:none; }

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
    margin-top: 8px !important;
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

    # -------- LEFT: brand / hero / KPI preview --------
    with left:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)

        mm_logo_html = (
            f'<img src="data:image/png;base64,{MM_LOGO}" />' if MM_LOGO else ""
        )
        st.markdown(f"""
        <div class="brand-row">
            {mm_logo_html}
            <div class="brand-divider"></div>
            <div>
                <div class="brand-credit-label">Software Designed By</div>
                <div class="brand-credit-name">Manufacturing Minds<br>Precision LLP</div>
            </div>
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

        # KPI preview cards with CSS conic-gradient gauges, matching the reference
        components.html("""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@800&family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
        <style>
            * { margin:0; padding:0; box-sizing:border-box; }
            body { background:transparent; font-family:'Inter', sans-serif; }
            .grid { display:grid; grid-template-columns: 1fr 1fr; gap:14px; }
            .card {
                background:rgba(255,255,255,0.05);
                border:1px solid rgba(255,255,255,0.12);
                border-radius:16px;
                padding:16px 18px;
                transition:all 0.28s ease;
            }
            .card:hover { transform:translateY(-3px); border-color:rgba(46,141,232,0.45); background:rgba(30,111,196,0.13); }
            .label { font-family:'Rajdhani',sans-serif; color:#8aaacf; font-size:11px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; margin-bottom:10px; }

            .gauge {
                width:64px; height:64px; border-radius:50%;
                display:flex; align-items:center; justify-content:center;
                position:relative;
            }
            .gauge-oee { background: conic-gradient(#2e8de8 0% 87%, rgba(255,255,255,0.12) 87% 100%); }
            .gauge-spindle { background: conic-gradient(#2e8de8 0% 65%, rgba(255,255,255,0.12) 65% 100%); }
            .gauge-inner {
                width:46px; height:46px; border-radius:50%;
                background:#0b1830;
                display:flex; align-items:center; justify-content:center;
                font-family:'Barlow Condensed',sans-serif; color:#fff; font-weight:800; font-size:14px;
            }

            .value { font-family:'Barlow Condensed',sans-serif; color:#2e8de8; font-size:34px; font-weight:800; line-height:1; }

            .spark { display:flex; align-items:flex-end; gap:3px; height:44px; }
            .spark div { width:6px; background:#2e8de8; border-radius:2px 2px 0 0; opacity:0.85; }

            .alert-row { display:flex; align-items:center; gap:8px; margin-top:6px; }
            .alert-row .bar { flex:1; height:6px; background:rgba(255,255,255,0.15); border-radius:3px; }

            .footer { display:flex; gap:28px; margin-top:18px; padding-top:14px; border-top:1px solid rgba(255,255,255,0.1); flex-wrap:wrap; }
            .pillar { display:flex; align-items:center; gap:8px; }
            .pillar-text { font-family:'Rajdhani',sans-serif; color:#7a94b8; font-size:12px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; }
        </style>

        <div class="grid">
            <div class="card">
                <div class="label">OEE</div>
                <div class="gauge gauge-oee"><div class="gauge-inner">87%</div></div>
            </div>
            <div class="card">
                <div class="label">Production Trend</div>
                <div class="spark">
                    <div style="height:30%"></div><div style="height:45%"></div><div style="height:35%"></div>
                    <div style="height:55%"></div><div style="height:50%"></div><div style="height:70%"></div>
                    <div style="height:65%"></div><div style="height:90%"></div><div style="height:100%"></div>
                </div>
            </div>
            <div class="card">
                <div class="label">Spindle Load</div>
                <div class="gauge gauge-spindle"><div class="gauge-inner">65%</div></div>
            </div>
            <div class="card">
                <div class="label">Alerts</div>
                <div style="font-size:20px; color:#ff9800;">⚠</div>
                <div class="alert-row"><div class="bar"></div></div>
                <div class="alert-row"><div class="bar" style="width:70%"></div></div>
            </div>
        </div>

        <div class="footer">
            <div class="pillar"><span>⊕</span><span class="pillar-text">Measure.</span></div>
            <div class="pillar"><span>📊</span><span class="pillar-text">Analyze.</span></div>
            <div class="pillar"><span>📈</span><span class="pillar-text">Optimize.</span></div>
            <div class="pillar"><span>🏆</span><span class="pillar-text">Perform.</span></div>
        </div>
        """, height=300, scrolling=False)

        st.markdown("</div>", unsafe_allow_html=True)

    # -------- RIGHT: login card --------
    # IMPORTANT: Streamlit renders every st.markdown() call as its own isolated
    # HTML fragment. You cannot open a <div> in one call and close it in a later
    # call -- the browser auto-closes the empty div immediately, which is why the
    # card background was breaking. The fix: wrap everything in a real
    # st.container(), drop an invisible marker element inside it, then use a CSS
    # `:has()` selector to style that container as the card from the outside.
    with right:
        with st.container(key="login_card"):
            st.markdown('<div class="login-card-marker"></div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="designed-for-row">
                <div class="line"></div>
                <span class="label">Designed For</span>
                <div class="line"></div>
            </div>
            """, unsafe_allow_html=True)

            if KISAAN_LOGO:
                st.markdown(
                    f'<div class="kisaan-logo-wrap"><img src="data:image/png;base64,{KISAAN_LOGO}" /></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="text-align:center;font-family:\'Barlow Condensed\',sans-serif;font-weight:800;font-size:30px;color:#0d1f3c;">KISAAN <span style="color:#cc1f24;">DieTech</span></div>',
                    unsafe_allow_html=True
                )

            st.markdown("""
            <div class="precision-row">
                <div class="stub"></div>
                <div class="text">Precision In Every Detail</div>
                <div class="stub"></div>
            </div>
            <div class="login-hr"></div>
            <div class="welcome-icon">⚙️</div>
            <div class="welcome-title">Welcome Back</div>
            <div class="welcome-sub">Login to access your machining analytics dashboard.</div>
            """, unsafe_allow_html=True)

            # Username field with leading icon (same :has() trick, scoped to a
            # container just around this one field)
            with st.container(key="username_field"):
                st.markdown('<div class="field-marker"></div>', unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Username", label_visibility="collapsed")

            # Password field with leading icon
            # NOTE: Streamlit's native text_input(type="password") does not support
            # a clickable show/hide eye icon out of the box. The icon below is shown
            # for visual parity with the design; a true toggle would require a custom
            # HTML component bound back to st.session_state (happy to build that next
            # if you want the eye to actually work).
            with st.container(key="password_field"):
                st.markdown('<div class="field-marker field-marker-lock"></div>', unsafe_allow_html=True)
                password = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")

            remember_col, forgot_col = st.columns([1, 1])
            with remember_col:
                remember = st.checkbox("Remember me", value=False, key="remember_me")
            with forgot_col:
                st.markdown(
                    '<div style="text-align:right; padding-top:8px;">'
                    '<a href="#" style="font-family:\'Inter\',sans-serif; font-size:13px; color:#1a6fc4; text-decoration:none;">Forgot Password?</a>'
                    '</div>',
                    unsafe_allow_html=True
                )

            if st.button("LOGIN"):
                if login(username, password):
                    st.session_state.logged_in = True
                    st.success("Login Successful")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")


# =========================================================
# MAIN DASHBOARD
# =========================================================
else:
    with st.spinner("Loading Dashboard..."):
        df = load_data()
    show_dashboard(df)

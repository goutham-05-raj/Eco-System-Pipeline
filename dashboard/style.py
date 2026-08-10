import streamlit as st

def apply_premium_style():
    """Glass-transparent cards with cursor hover lift effects. Plain white background."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        /* ── Base ── */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', sans-serif !important;
            background-color: #ffffff !important;
            background-image: none !important;
            color: #000000 !important;
        }

        [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid rgba(0,0,0,0.08) !important;
        }
        [data-testid="stSidebar"] * { color: #000000 !important; }

        /* ── Headers ── */
        h1, h2, h3, h4, h5, h6 {
            color: #000000 !important;
            font-weight: 800 !important;
        }
        h1 { font-size: 2rem !important; margin-bottom: 0.25rem !important; }
        h2 { font-size: 1.4rem !important; }

        /* ── Metric Cards — Glass + Hover ── */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            color: #000000 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            color: #444444 !important;
        }
        [data-testid="metric-container"] {
            background: #ffffff !important;
            border: 1px solid rgba(0,0,0,0.10) !important;
            border-radius: 16px !important;
            padding: 22px !important;
            transition: transform 0.22s ease, box-shadow 0.22s ease !important;
            cursor: pointer !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
        }
        [data-testid="metric-container"]:hover {
            transform: translateY(-5px) scale(1.02) !important;
            box-shadow: 0 12px 32px rgba(0,0,0,0.15) !important;
            background: #ffffff !important;
            border-color: rgba(0,0,0,0.20) !important;
        }

        /* ── Tables ── */
        [data-testid="stDataFrame"] {
            background: #ffffff !important;
            border: 1px solid rgba(0,0,0,0.10) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        }

        /* ── Expanders ── */
        .streamlit-expanderHeader {
            background: #ffffff !important;
            border: 1px solid rgba(0,0,0,0.10) !important;
            border-radius: 10px !important;
            font-weight: 800 !important;
        }
        .streamlit-expanderHeader:hover {
            background: #f8fafc !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
        }
        .streamlit-expanderContent {
            border: 1px solid rgba(0,0,0,0.10) !important;
            border-top: none !important;
            background: #ffffff !important;
        }

        /* ── Selectboxes & Inputs ── */
        [data-testid="stSelectbox"] > div,
        [data-testid="stTextInput"] > div > div {
            border: 1px solid rgba(0,0,0,0.15) !important;
            border-radius: 8px !important;
            background: #ffffff !important;
        }

        /* ── Buttons ── */
        .stButton>button {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease !important;
        }
        .stButton>button:hover {
            background-color: #222222 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.20) !important;
        }

        /* ── Header ── */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* ── Custom cursor glow following mouse ── */
        body {
            cursor: none !important;
        }
        #cursor-glow {
            position: fixed;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(99,102,241,0.55) 0%, transparent 70%);
            pointer-events: none;
            z-index: 99999;
            transform: translate(-50%, -50%);
            transition: width 0.15s, height 0.15s, background 0.15s;
        }
        #cursor-dot {
            position: fixed;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #000000;
            pointer-events: none;
            z-index: 99999;
            transform: translate(-50%, -50%);
        }

        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>

        <!-- Custom cursor -->
        <div id="cursor-glow"></div>
        <div id="cursor-dot"></div>
        <script>
        const glow = document.getElementById('cursor-glow');
        const dot  = document.getElementById('cursor-dot');
        document.addEventListener('mousemove', e => {
            glow.style.left = e.clientX + 'px';
            glow.style.top  = e.clientY + 'px';
            dot.style.left  = e.clientX + 'px';
            dot.style.top   = e.clientY + 'px';
        });
        document.addEventListener('mouseover', e => {
            if (e.target.closest('[data-testid="metric-container"]')) {
                glow.style.width  = '60px';
                glow.style.height = '60px';
                glow.style.background = 'radial-gradient(circle, rgba(99,102,241,0.75) 0%, transparent 70%)';
            } else {
                glow.style.width  = '28px';
                glow.style.height = '28px';
                glow.style.background = 'radial-gradient(circle, rgba(99,102,241,0.55) 0%, transparent 70%)';
            }
        });
        </script>
    """, unsafe_allow_html=True)

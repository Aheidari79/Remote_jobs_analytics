import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

pages = [
    st.Page("pages/Executive_Summary.py", title="🏠 Executive Summary"),
    st.Page("pages/Geo-Arbitrage.py", title="🌍 Geo-Arbitrage"),
    st.Page("pages/Skill_Premium_Matrix.py", title="💡 Skill Premium Matrix"),
    st.Page("pages/Salary_Estimator.py", title="🔍 Salary Estimator"),
    st.Page("pages/About.py", title="ℹ️ About"),
]

pg = st.navigation(pages)

pg.run()

try:
    from streamlit_echarts import st_echarts
except ImportError:
    st.error("Please install streamlit-echarts: pip install streamlit-echarts")
    st.stop()

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Remote Job Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

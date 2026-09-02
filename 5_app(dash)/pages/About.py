import streamlit as st
from utils import apply_custom_css

# 1. Configuration
st.set_page_config(page_title="About the Project", page_icon="ℹ️", layout="wide")

# 2. Shared Setup
apply_custom_css()

# ---------------------------------------------------------
# Header / Hero Section
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>ℹ️ About This Project</h1>
        <p>
            Democratizing remote job market data through advanced analytics, 
            interactive visualizations, and data-driven insights.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ---------------------------------------------------------
# Project Overview Section
# ---------------------------------------------------------
st.markdown('<div class="section-title">🚀 Project Mission</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <p style="font-size: 1.1rem; color: #374151; line-height: 1.7;">
            The <b>Himalayas Remote Job Analytics Dashboard</b> was built to provide clarity in the rapidly evolving remote work landscape. 
            By processing thousands of job postings, this tool transforms raw data into actionable intelligence. 
            Whether you are a job seeker negotiating a salary, or a researcher analyzing global tech trends, 
            this dashboard offers real-time insights into <b>Geo-Arbitrage</b>, <b>Skill Premiums</b>, and <b>Market Liquidity</b>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---------------------------------------------------------
# Tech Stack Section
# ---------------------------------------------------------
st.markdown('<div class="section-title" style="margin-top:2rem;">🛠️ Tech Stack & Methodology</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(
        """
        <div class="chart-card" style="text-align: center; padding: 2rem 1rem;">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🐍</h1>
            <h3 style="color: #1F2937;">Python & Pandas</h3>
            <p style="color: #6B7280; font-size: 0.95rem;">Core data manipulation, cleaning, and complex aggregations handling thousands of records efficiently.</p>
        </div>
        """, unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="chart-card" style="text-align: center; padding: 2rem 1rem;">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">👑</h1>
            <h3 style="color: #1F2937;">Streamlit</h3>
            <p style="color: #6B7280; font-size: 0.95rem;">The underlying framework powering the interactive web application, routing, and user interface.</p>
        </div>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="chart-card" style="text-align: center; padding: 2rem 1rem;">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">📊</h1>
            <h3 style="color: #1F2937;">Apache ECharts</h3>
            <p style="color: #6B7280; font-size: 0.95rem;">High-performance, modern javascript charting library integrated via <code>streamlit-echarts</code> for fluid animations.</p>
        </div>
        """, unsafe_allow_html=True
    )

# ---------------------------------------------------------
# About the Developer Section
# ---------------------------------------------------------
st.markdown('<div class="section-title" style="margin-top:3rem;">👨‍💻 About the Developer</div>', unsafe_allow_html=True)

st.markdown(
"""<div style="background-color: white; padding: 2.5rem; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column; gap: 1rem;">
<h2 style="margin: 0; color: #111827;">Ali Heidari</h2>
<h4 style="margin: 0; color: #3B82F6; font-weight: 500;">Python Developer | Data Analyst | Educator</h4>
<p style="font-size: 1.05rem; color: #4B5563; line-height: 1.6; margin-top: 1rem;">
With a solid foundation in telecommunications electrical engineering and professional experience in vocational education, I bring a highly analytical and structured approach to software development. My passion lies in bridging the gap between raw data and human understanding through clean code and intuitive design.
</p>
<p style="font-size: 1.05rem; color: #4B5563; line-height: 1.6;">
Beyond data analysis and web scraping, I build automation scripts, design interactive GUIs, and constantly explore the intersection of hardware and software to create practical, real-world solutions.
</p>
<div style="margin-top: 1.5rem; display: flex; gap: 1.5rem;">
<a href="https://github.com/YOUR_GITHUB_USERNAME" target="_blank" style="text-decoration: none; font-weight: bold; color: #1F2937; background-color: #F3F4F6; padding: 0.5rem 1rem; border-radius: 6px;">🔗 GitHub</a>
<a href="https://linkedin.com/in/ali-heidari-4aa142260/" target="_blank" style="text-decoration: none; font-weight: bold; color: #ffffff; background-color: #0A66C2; padding: 0.5rem 1rem; border-radius: 6px;">💼 LinkedIn</a>
<a href="mailto:Aheidari761@gmail.com" style="text-decoration: none; font-weight: bold; color: #ffffff; background-color: #EF4444; padding: 0.5rem 1rem; border-radius: 6px;">✉️ Email</a>
</div>
</div>""",
    unsafe_allow_html=True
)
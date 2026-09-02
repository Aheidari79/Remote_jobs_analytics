import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts
from utils import load_data, apply_custom_css
import plotly.express as px



# Apply shared styling and load shared data
apply_custom_css()
df = load_data()

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

# Ensure date column is converted to datetime format once
if not pd.api.types.is_datetime64_any_dtype(df["Published Date(STD)"]):
    df["Published Date(STD)"] = pd.to_datetime(df["Published Date(STD)"])

with st.sidebar:
    st.title("📊 Filters:")
    #st.markdown('<div class="brand">📊 Filters:</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">◫ Global Filters</div>', unsafe_allow_html=True)

    # 1. Date Range Filter (Mapped from Published Date(STD))
    #period_option = st.multiselect(
    #    "Reporting Period",
    #    ["12 Months", "24 Months", "36 Months", "All Time"],
    #    default=["All Time"],
    #    placeholder="Select period",
    #    max_selections=1,
    #)

    # 2. Region / Location Filter (Mapped from Region & Location Restrictions)
    available_regions = sorted(df["Region"].dropna().unique())
    selected_regions = st.multiselect(
        "Region",
        available_regions,
        default=[],
        placeholder="All Regions",
    )

    # 3. Category Filter (Mapped from Standard Category)
    available_categories = sorted(df["Standard Category"].dropna().unique())
    selected_categories = st.multiselect(
        "Job Category",
        available_categories,
        default=[],
        placeholder="All Categories",
    )

    # 4. Seniority Level Filter (Mapped from seniority)
    available_seniorities = sorted(df["seniority"].dropna().unique())
    selected_seniority = st.multiselect(
        "Seniority Level",
        available_seniorities,
        default=[],
        placeholder="All Levels",
    )

    # 5. Employment Type Filter (Mapped from Employment Type)
    available_emp_types = sorted(df["Employment Type"].dropna().unique())
    selected_emp_types = st.multiselect(
        "Employment Type",
        available_emp_types,
        default=[],
        placeholder="All Types",
    )

    # 6. Salary Range Slider (Mapped from Avg_Salary_USD_Annual)
    min_sal = int(df["Avg_Salary_USD_Annual"].min())
    max_sal = int(df["Avg_Salary_USD_Annual"].max())
    
    with st.container(border=True):
        selected_salary_range = st.slider(
            "Annual Salary Range ($)",
            min_value=min_sal,
            max_value=max_sal,
            value=(min_sal, max_sal),
            step=5000
        )


# ==========================================
# Filtering Logic Execution
# ==========================================

# Base Copy
filtered = df.copy()

# Date Filtering
max_date = filtered["Published Date(STD)"].max()
#if "12 Months" in period_option:
#    start_date = max_date - pd.DateOffset(months=12)
#    filtered = filtered[filtered["Published Date(STD)"] >= start_date]
#elif "24 Months" in period_option:
#    start_date = max_date - pd.DateOffset(months=24)
#    filtered = filtered[filtered["Published Date(STD)"] >= start_date]
#elif "36 Months" in period_option:
#    start_date = max_date - pd.DateOffset(months=36)
#    filtered = filtered[filtered["Published Date(STD)"] >= start_date]

# Category & Categorical Filtering
if selected_regions:
    filtered = filtered[filtered["Region"].isin(selected_regions)]

if selected_categories:
    filtered = filtered[filtered["Standard Category"].isin(selected_categories)]

if selected_seniority:
    filtered = filtered[filtered["seniority"].isin(selected_seniority)]

if selected_emp_types:
    filtered = filtered[filtered["Employment Type"].isin(selected_emp_types)]

# Salary Filtering
filtered = filtered[
    (filtered["Avg_Salary_USD_Annual"] >= selected_salary_range[0]) &
    (filtered["Avg_Salary_USD_Annual"] <= selected_salary_range[1])
]


# ---------------------------------------------------------
# Aggregation (Adapted for Remote Job Market Data)
# ---------------------------------------------------------
# Ensure published date is datetime
filtered["Published Date(STD)"] = pd.to_datetime(filtered["Published Date(STD)"])

total_postings = len(filtered)
avg_salary = filtered["Avg_Salary_USD_Annual"].mean() if total_postings else 0
median_salary = filtered["Avg_Salary_USD_Annual"].median() if total_postings else 0
total_budget = filtered["Avg_Salary_USD_Annual"].sum() if total_postings else 0

# Grouping by Month for Trend Analysis
filtered["Month"] = filtered["Published Date(STD)"].dt.to_period("M").dt.to_timestamp()

monthly = (
    filtered.groupby("Month", as_index=False)
    .agg(
        Postings=("Title", "count"),
        AvgSalary=("Avg_Salary_USD_Annual", "mean"),
        TotalBudget=("Avg_Salary_USD_Annual", "sum")
    )
    .sort_values("Month")
)

# Delta Calculations (First Half vs Second Half of Selected Timeframe)
if len(monthly) >= 2:
    mid = len(monthly) // 2
    first_half = monthly.iloc[:mid]
    second_half = monthly.iloc[mid:]

    postings_delta = (
        (second_half["Postings"].sum() / first_half["Postings"].sum()) - 1
        if first_half["Postings"].sum() else 0
    )
    salary_delta = (
        (second_half["AvgSalary"].mean() / first_half["AvgSalary"].mean()) - 1
        if first_half["AvgSalary"].mean() else 0
    )
    budget_delta = (
        (second_half["TotalBudget"].sum() / first_half["TotalBudget"].sum()) - 1
        if first_half["TotalBudget"].sum() else 0
    )
else:
    postings_delta = salary_delta = budget_delta = 0


# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>📊 Himalayas Remote Job Analytics</h1>
        <p>
            An interactive dashboard tracking international remote hiring trends, 
            geographical salary ceilings, and enterprise recruitment liquidity.
        <b>Analysis period: 2026-07-24 to 2026-08-19<b>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

#start_date = filtered["Published Date(STD)"].min()
#end_date = filtered["Published Date(STD)"].max()

st.write("")

# ---------------------------------------------------------
# KPI Cards Setup
# ---------------------------------------------------------
def money(x):
    return f"${x:,.0f}"

def integer(x):
    return f"{int(x):,}"

def percent(x):
    return f"{x * 100:.1f}%"

kpi_data = [
    ("Total Postings", integer(total_postings), postings_delta),
    ("Avg Annual Salary", money(avg_salary), salary_delta),
    ("Total Market Liquidity", f"${total_budget/1e6:.1f}M", budget_delta),
    ("Median Annual Salary", money(median_salary), salary_delta),
]

cols = st.columns(4, gap="small")

for col, (title, value, delta) in zip(cols, kpi_data):
    arrow = "↑" if delta >= 0 else "↓"
    css = "delta-up" if delta >= 0 else "delta-down"
    with col:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                <span class="delta {css}">{arrow} {abs(delta):.1%}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# Performance Breakdown Section
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title" style="margin-top:1.8rem;">◫ Category & Geographical Distribution</div>',
    unsafe_allow_html=True,
)

# Category Data Aggregation
category_data = (
    filtered.groupby("Standard Category", as_index=False)
    .agg(Postings=("Title", "count"))
    .sort_values("Postings", ascending=True)
    .tail(10)  # Top 10 categories
)

category_option = {
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "grid": {"left": 120, "right": 30, "top": 20, "bottom": 30},
    "xAxis": {"type": "value"},
    "yAxis": {
        "type": "category",
        "data": category_data["Standard Category"].tolist(),
    },
    "series": [
        {
            "name": "Job Postings",
            "type": "bar",
            "data": category_data["Postings"].tolist(),
            "barMaxWidth": 24,
            "itemStyle": {"color": "#22C55E", "borderRadius": [0, 4, 4, 0]},
            "label": {"show": True, "position": "right"},
        }
    ],
}

# Region Data Aggregation
region_data = (
    filtered.groupby("Region", as_index=False)
    .agg(Postings=("Title", "count"))
    .sort_values("Postings", ascending=False)
)

region_option = {
    "tooltip": {"trigger": "item"},
    "legend": {"bottom": 0},
    "series": [
        {
            "name": "Regions",
            "type": "pie",
            "radius": ["42%", "70%"],
            "center": ["50%", "45%"],
            "avoidLabelOverlap": True,
            "itemStyle": {"borderRadius": 7, "borderColor": "#fff", "borderWidth": 2},
            "label": {"show": True, "formatter": "{b}: {d}%"},
            "data": [
                {"name": str(row["Region"]), "value": int(row["Postings"])}
                for _, row in region_data.iterrows()
            ],
        }
    ],
}

c1, c2 = st.columns(2, gap="medium")



with c1:
    with st.container(border=True):
        st.markdown(
            '<h4 style="margin:5px 0 0 4px;">Top Job Categories</h4>',
            unsafe_allow_html=True,
        )
        st_echarts(options=category_option, height="340px", key="category_chart")
        st.markdown("</div>", unsafe_allow_html=True)

with c2:
    with st.container(border=True):
        st.markdown(
                '<h4 style="margin:5px 0 0 4px;">Postings by Region</h4>',
                unsafe_allow_html=True,
            )
        st_echarts(options=region_option, height="340px", key="region_chart")
        st.markdown("</div>", unsafe_allow_html=True)
    

# ---------------------------------------------------------
# Section Heading: Job Postings Distributions
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">↗ Job Postings Distributions</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle"> posting volume trajectories by Seniority and Employment Type .</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Plotly Chart: Job Postings Distribution by senoirity
# ---------------------------------------------------------
fig3 = px.histogram(
    filtered, 
    x="Avg_Salary_USD_Annual", 
    nbins=50, 
    color='seniority', 
    #template='plotly_dark',
    title='Annual Average salary Distribution',
    labels={'Avg_Salary_USD_Annual': 'Average Annual Salary'}
)

# ۲. اضافه کردن Subtitle و تنظیم عنوان
fig3.update_layout(
    title=dict(
        text='Maximum Annual Average salary Distribution',
        font=dict(color='White', size=17),
        subtitle=dict(
            #text='How contracor positions distribute and increase max values in dataset:',
            font=dict(color='gray', size=11)
        )
    ),
    yaxis_type='log'
)

col1, col2 = st.columns(2, gap="medium")

with col1:
    with st.container(border=True):
        st.markdown('<h4 style="margin:5px 0 0 4px;">Distribution by Seniority</h4>',unsafe_allow_html=True,)
        st.plotly_chart(fig3)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Plotly Chart: Job Postings Distribution by Emloyment Type
# ---------------------------------------------------------
fig2 = px.histogram(
    filtered, 
    x="Avg_Salary_USD_Annual", 
    nbins=50, 
    color='Employment Type', 
    #template='plotly_dark',
    title='Annual Average salary Distribution',
    labels={'Avg_Salary_USD_Annual': 'Average Annual Salary'}
)

# ۲. اضافه کردن Subtitle و تنظیم عنوان
fig2.update_layout(
    title=dict(
        text='Maximum Annual Average salary Distribution',
        font=dict(color='White', size=17),
        subtitle=dict(
            #text='How contracor positions distribute and increase max values in dataset:',
            font=dict(color='gray', size=11)
        )
    ),
    yaxis_type='log'
)




with col2:
    with st.container(border=True):
        st.markdown('<h4 style="margin:5px 0 0 4px;">Distribution by Employment Type</h4>',
            unsafe_allow_html=True,)
        st.plotly_chart(fig2)
        st.markdown("</div>", unsafe_allow_html=True)


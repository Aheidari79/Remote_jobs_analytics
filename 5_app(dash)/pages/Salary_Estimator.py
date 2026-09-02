import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from utils import load_data, apply_custom_css
import plotly.express as px

# 1. Configuration
st.set_page_config(page_title="Salary Estimator", page_icon="🧮", layout="wide")

# 2. Shared Setup
apply_custom_css()
df = load_data()

# فیلتر کردن داده‌های بدون حقوق
salary_df = df[df["Avg_Salary_USD_Annual"].notnull() & (df["Avg_Salary_USD_Annual"] > 0)].copy()

# ---------------------------------------------------------
# Header / Hero Section
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🧮 Remote Salary Estimator</h1>
        <p>
            Dial in your role, seniority, and region to get a real-time, data-backed 
            salary estimate based on current remote job market postings.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# User Inputs (Filters)
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Configure Your Profile")
    #st.markdown('<div class="brand">⚙️ Configure Your Profile</div>', unsafe_allow_html=True)

    # استخراج لیست‌های یکتا برای دراپ‌داون‌ها (به علاوه گزینه همه)
    categories = ["All Categories"] + sorted(salary_df["Standard Category"].dropna().unique().tolist())
    seniorities = ["Any Seniority"] + sorted(salary_df["seniority"].dropna().unique().tolist())
    regions = ["Global (Anywhere)"] + sorted(salary_df["Region"].dropna().unique().tolist())

    # ایجاد سه ستون برای انتخاب

    selected_cat = st.selectbox("💼 Job Category", options=categories)
    selected_sen = st.selectbox("⭐ Seniority Level", options=seniorities)
    selected_reg = st.selectbox("🌎 Geographical Region", options=regions)

# ---------------------------------------------------------
# Filtering Logic
# ---------------------------------------------------------
filtered_df = salary_df.copy()

if selected_cat != "All Categories":
    filtered_df = filtered_df[filtered_df["Standard Category"] == selected_cat]

if selected_sen != "Any Seniority":
    filtered_df = filtered_df[filtered_df["seniority"] == selected_sen]

if selected_reg != "Global (Anywhere)":
    filtered_df = filtered_df[filtered_df["Region"] == selected_reg]

# ---------------------------------------------------------
# Estimation Calculations & KPIs
# ---------------------------------------------------------
st.markdown('<div class="section-title" style="margin-top:2rem;">📊 Estimation Results</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("⚠️ Not enough data for this specific combination. Try broadening your search (e.g., set Region to Global).")
else:
    job_count = len(filtered_df)
    
    # محاسبه صدک‌ها (Percentiles)
    p25_salary = filtered_df["Avg_Salary_USD_Annual"].quantile(0.25)
    median_salary = filtered_df["Avg_Salary_USD_Annual"].median()
    p75_salary = filtered_df["Avg_Salary_USD_Annual"].quantile(0.75)
    
    max_market_salary = salary_df["Avg_Salary_USD_Annual"].max()
    cat_max_salary = filtered_df["Avg_Salary_USD_Annual"].max()

    def render_kpi(title, value, sub_text, delta_class="delta-up"):
        html_string = (
            '<div class="kpi">'
            f'<div class="kpi-title">{title}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<span class="delta {delta_class}">{sub_text}</span>'
            '</div>'
        )
        st.markdown(html_string, unsafe_allow_html=True)

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="small")
    
    with kpi_col1:
        render_kpi("Matching Jobs", f"{job_count:,}", "Data points used")
    with kpi_col2:
        render_kpi("Lower Bound (25th)", f"${p25_salary:,.0f}", "Entry/Less competitive")
    with kpi_col3:
        render_kpi("Median Estimate", f"${median_salary:,.0f}", "Market Standard", "delta-up")
    with kpi_col4:
        render_kpi("Upper Bound (75th)", f"${p75_salary:,.0f}", "Premium/Highly competitive")

    st.write("")

    # ---------------------------------------------------------
    # Visualizations: Gauge Chart & Distribution Bar
    # ---------------------------------------------------------
    # چارت گیج (Gauge) برای نشان دادن میانه حقوق
    gauge_option = {
        "tooltip": {
            "formatter": "{a} <br/>{b} : ${c}"
        },
        "series": [
            {
                "name": "Salary Estimate",
                "type": "gauge",
                "max": int(cat_max_salary * 1.2) if cat_max_salary else 200000,
                "progress": {
                    "show": True,
                    "width": 18,
                    "itemStyle": {"color": "#3B82F6"}
                },
                "axisLine": {
                    "lineStyle": {"width": 18, "color": [[1, "#E5E7EB"]]}
                },
                "axisTick": {"show": False},
                "splitLine": {"length": 15, "lineStyle": {"width": 2, "color": "#9CA3AF"}},
                "axisLabel": {
                    "distance": 25,
                    "color": "#6B7280",
                    "fontSize": 10,
                    "formatter": "${value}"
                },
                "anchor": {
                    "show": True,
                    "showAbove": True,
                    "size": 24,
                    "itemStyle": {"borderWidth": 10, "borderColor": "#3B82F6"}
                },
                "pointer": {"icon": "path://M10.5,1.5 L10.5,30 L1.5,30 L1.5,1.5 Z", "length": "65%", "width": 6, "itemStyle": {"color": "#1F2937"}},
                "title": {"show": False},
                "detail": {
                    "valueAnimation": True,
                    "fontSize": 30,
                    "fontWeight": "bold",
                    "color": "#111827",
                    "formatter": "${value}",
                    "offsetCenter": [0, "70%"]
                },
                "data": [{"value": int(median_salary), "name": "Median USD"}]
            }
        ]
    }

    # نمودار میله‌ای مقایسه‌ای: اگر کاربر "همه ارشدیت‌ها" را انتخاب کرده بود، میانگین ارشدیت‌های مختلف را بهش نشان بده
    chart_col1, chart_col2 = st.columns([1.2, 1], gap="large")

    with chart_col1:
        with st.container(border=True):
            st.markdown("##### 🎯 Median Salary Meter")
            st_echarts(options=gauge_option, height="400px", key="salary_gauge")
            st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        with st.container(border=True):
            st.markdown("##### 📈 Context: Category Avg by Seniority")
        
            # محاسبه برای چارت کمکی سمت راست (بدون در نظر گرفتن فیلتر ارشدیت کاربر تا تصویر کلی را ببیند)
            context_df = salary_df.copy()
            if selected_cat != "All Categories":
                context_df = context_df[context_df["Standard Category"] == selected_cat]
            if selected_reg != "Global (Anywhere)":
                context_df = context_df[context_df["Region"] == selected_reg]
                
            context_grouped = context_df.groupby("seniority")["Avg_Salary_USD_Annual"].mean().reset_index()
            context_grouped = context_grouped.sort_values("Avg_Salary_USD_Annual")
            
            if not context_grouped.empty:
                bar_option = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "grid": {"left": 100, "right": 20, "top": 20, "bottom": 20},
                    "xAxis": {"type": "value", "axisLabel": {"formatter": "${value}"}, "splitLine": {"show": False}},
                    "yAxis": {"type": "category", "data": context_grouped["seniority"].tolist()},
                    "series": [
                        {
                            "name": "Avg Salary",
                            "type": "bar",
                            "data": [int(v) for v in context_grouped["Avg_Salary_USD_Annual"]],
                            "itemStyle": {"color": "#10B981", "borderRadius": [0, 4, 4, 0]},
                            "label": {"show": True, "position": "right", "formatter": "${c}"}
                        }
                    ]
                }
                st_echarts(options=bar_option, height="400px", key="context_bar")
            else:
                st.info("Not enough diverse seniority data to show context.")
                
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
# Section: Global Job Market Map
# ---------------------------------------------------------



st.markdown(
    '<div class="section-title">🌍 Global Job Market Distribution</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-subtitle">
        Explore the global distribution of remote job opportunities
        and compensation levels based on the selected filters.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------##################################
# Prepare Location Data
# ---------------------------------------------------------

# Work only with the already-filtered dataframe
df_loc_exploded = filtered_df.copy()


# Keep only rows that have location information
df_loc_exploded = df_loc_exploded[
    df_loc_exploded["Location Restrictions"].notna()
].copy()


# Convert location strings into lists
df_loc_exploded["Location Restrictions"] = (
    df_loc_exploded["Location Restrictions"]
    .astype(str)
    .str.split(",")
)


# One row per location
df_loc_exploded = df_loc_exploded.explode(
    "Location Restrictions"
).reset_index(drop=True)


# Clean country names
df_loc_exploded["Country"] = (
    df_loc_exploded["Location Restrictions"]
    .str.strip()
)


# Remove empty / invalid locations
df_loc_exploded = df_loc_exploded[
    df_loc_exploded["Country"].notna()
    &
    (df_loc_exploded["Country"] != "")
].copy()


# ---------------------------------------------------------
# Remove Non-Country Generic Locations
# ---------------------------------------------------------

generic_locations = {
    "Worldwide",
    "Anywhere",
    "Global",
    "Remote",
    "International",
    "Any Location",
    "All Locations",
}

df_loc_exploded = df_loc_exploded[
    ~df_loc_exploded["Country"].isin(generic_locations)
].copy()


# ---------------------------------------------------------
# Aggregate Country Statistics
# ---------------------------------------------------------

country_stats = (
    df_loc_exploded
    .groupby("Country")
    .agg(
        Job_Postings=("Title", "count"),
        Average_Salary=(
            "Avg_Salary_USD_Annual",
            "mean"
        ),
        Median_Salary=(
            "Avg_Salary_USD_Annual",
            "median"
        ),
    )
    .reset_index()
)


# ---------------------------------------------------------
# Remove Countries Without Salary Data Only If Needed
# ---------------------------------------------------------

country_stats["Average_Salary"] = (
    country_stats["Average_Salary"].round(0)
)

country_stats["Median_Salary"] = (
    country_stats["Median_Salary"].round(0)
)


# ---------------------------------------------------------
# Select Map Metric
# ---------------------------------------------------------
with st.container(border=True):

    map_metric = st.selectbox(
        "Map Metric",
        options=[
            "Average Salary",
            "Job Postings",
            "Median Salary",
        ],
        index=0,
    )


# ---------------------------------------------------------
# Empty Data Handling
# ---------------------------------------------------------
    if country_stats.empty:

        st.info(
            "No geographic data is available for the selected filters."
        )

    else:

        # -----------------------------------------------------
        # Configure Map Metric
        # -----------------------------------------------------

        if map_metric == "Job Postings":

            color_column = "Job_Postings"

            color_title = "Job Postings"

            hover_salary_format = ":$,.0f"


        elif map_metric == "Average Salary":

            color_column = "Average_Salary"

            color_title = "Average Annual Salary (USD)"

            hover_salary_format = ":$,.0f"


        else:

            color_column = "Median_Salary"

            color_title = "Median Annual Salary (USD)"

            hover_salary_format = ":$,.0f"


        # -----------------------------------------------------
        # World Choropleth Map
        # -----------------------------------------------------

        fig_map = px.choropleth(
            country_stats,
            locations="Country",
            locationmode="country names",
            color=color_column,
            color_continuous_scale="rdylbu",
            projection="natural earth",

            hover_name="Country",

            hover_data={
                "Job_Postings": ":,",
                "Average_Salary": ":$,.0f",
                "Median_Salary": ":$,.0f",
                color_column: True,
            },

            labels={
                "Job_Postings": "Job Postings",
                "Average_Salary": "Average Annual Salary",
                "Median_Salary": "Median Annual Salary",
            },

            title=(
                f"Global Remote Job Market — {map_metric}"
            ),
        )


        # -----------------------------------------------------
        # Map Styling
        # -----------------------------------------------------

        fig_map.update_geos(
            showframe=True,
            showcoastlines=True,
            projection_type="natural earth",
        )


        fig_map.update_layout(

            height=600,

            margin=dict(
                l=10,
                r=10,
                t=70,
                b=10,
            ),

            title=dict(
                x=0.5,
                xanchor="center",
            ),

            coloraxis_colorbar=dict(
                title=color_title,
            ),
        )


        # -----------------------------------------------------
        # Display
        # -----------------------------------------------------

        st.plotly_chart(
            fig_map,
            use_container_width=True,
        )
        
    # ---------------------------------------------------------
    # Sample Jobs Table
    # ---------------------------------------------------------
    st.markdown('<div class="section-title" style="margin-top:2rem;">📄 Sample Postings Matching Your Criteria</div>', unsafe_allow_html=True)
    
    display_cols = ["Title", "Company Slug", "seniority", "Location Restrictions", "Avg_Salary_USD_Annual"]
    
    # نمایش ۵ نمونه اول به صورت تصادفی از فیلتر اعمال شده
    sample_data = filtered_df[display_cols].sample(min(5, len(filtered_df)))
    
    st.dataframe(
        sample_data.style.format({
            "Avg_Salary_USD_Annual": "${:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    

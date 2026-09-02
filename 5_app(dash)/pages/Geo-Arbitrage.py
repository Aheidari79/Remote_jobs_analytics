import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from utils import load_data, apply_custom_css
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Geo Arbitrage Analytics",
    page_icon="🌎",
    layout="wide"
)


# ---------------------------------------------------------
# Shared Setup
# ---------------------------------------------------------
apply_custom_css()

df = load_data()

df.columns = df.columns.str.strip()


# Ensure required columns exist
if "clean_location" not in df.columns:
    df["clean_location"] = "Unknown"

if "Region" not in df.columns:
    df["Region"] = "Unknown"

if "Location Restrictions" not in df.columns:
    df["Location Restrictions"] = ""

if "Title" not in df.columns:
    df["Title"] = "Unknown"


# Salary dataframe
salary_df = df[
    df["Avg_Salary_USD_Annual"].notna()
    &
    (df["Avg_Salary_USD_Annual"] > 0)
].copy()


salary_df["Region"] = salary_df["Region"].fillna("Unknown")

df["clean_location"] = df["clean_location"].fillna("Unknown")


# ---------------------------------------------------------
# Hero Section
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🌎 Geo Arbitrage & Geographic Salary Analytics</h1>
        <p>
            Explore global remote pay gaps, regional compensation benchmarks,
            and location restriction patterns.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)



# ---------------------------------------------------------
# KPI Calculations
# ---------------------------------------------------------

region_salary = (
    salary_df
    .groupby("Region")["Avg_Salary_USD_Annual"]
    .mean()
)


if not region_salary.empty:
    top_region_name = region_salary.idxmax()
    top_region_val = region_salary.max()
else:
    top_region_name = "N/A"
    top_region_val = 0



total_jobs = len(df)


worldwide_jobs = df[
    df["Location Restrictions"]
    .fillna("")
    .str.contains(
        "Worldwide|Anywhere",
        case=False,
        regex=True
    )
].shape[0]


worldwide_pct = (
    worldwide_jobs / total_jobs * 100
    if total_jobs > 0
    else 0
)



global_median_sal = (
    salary_df["Avg_Salary_USD_Annual"].median()
    if not salary_df.empty
    else 0
)



top_restriction = (
    df["clean_location"].mode()[0]
    if not df["clean_location"].empty
    else "N/A"
)



# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

cols = st.columns(4, gap="small")


kpis = [
    (
        "Highest Paying Region",
        top_region_name,
        f"${top_region_val:,.0f} / year"
    ),
    (
        "Worldwide Openings",
        f"{worldwide_pct:.1f}%",
        f"{worldwide_jobs:,} roles"
    ),
    (
        "Global Median Salary",
        f"${global_median_sal:,.0f}",
        "Annual USD"
    ),
    (
        "Top Location Hub",
        top_restriction,
        "Most Frequent"
    )
]


for col, item in zip(cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-title">{item[0]}</div>
                <div class="kpi-value">{item[1]}</div>
                <span class="delta delta-up">{item[2]}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


st.write("")



# ---------------------------------------------------------
# Section 1
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Regional Compensation & Market Share</div>',
    unsafe_allow_html=True,
)



region_stats = (
    salary_df
    .groupby("Region", as_index=False)
    .agg(
        AvgSalary=("Avg_Salary_USD_Annual","mean"),
        JobCount=("Title","count")
    )
    .sort_values(
        "AvgSalary",
        ascending=True
    )
)



salary_region_option = {

    "tooltip": {
        "trigger":"axis",
        "axisPointer":{
            "type":"shadow"
        },
        "formatter":"{b}: ${c}"
    },

    "grid":{
        "left":110,
        "right":30,
        "top":20,
        "bottom":30
    },

    "xAxis":{
        "type":"value"
    },

    "yAxis":{
        "type":"category",
        "data":region_stats["Region"].tolist()
    },


    "series":[
        {
            "name":"Average Salary",
            "type":"bar",
            "data":[
                round(x,0)
                for x in region_stats["AvgSalary"]
            ],
            "label":{
                "show":True,
                "position":"right",
                "formatter":"${c}"
            },
            "itemStyle":{
                "borderRadius":5
            }
        }
    ]
}



# Location Pie


loc_data = (
    df["clean_location"]
    .value_counts()
    .head(8)
    .reset_index()
)


loc_data.columns = [
    "Location",
    "Count"
]


loc_pie_option = {

    "tooltip":{
        "trigger":"item",
        "formatter":"{b}: {c} jobs ({d}%)"
    },


    "legend":{
        "bottom":"0%",
        "type":"scroll"
    },


    "series":[
        {
            "name":"Location",
            "type":"pie",
            "radius":[
                "40%",
                "70%"
            ],

            "data":[
                {
                    "name":str(row["Location"]),
                    "value":int(row["Count"])
                }

                for _,row in loc_data.iterrows()
            ]
        }
    ]
}



col1,col2 = st.columns(2)


with col1:
    with st.container(border=True):

        st.markdown(
            "##### Average Annual Salary by Region ($)"
        )


        st_echarts(
            options=salary_region_option,
            height="360px",
            key="salary_region"
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )



with col2:
    with st.container(border=True):

        st.markdown(
            "##### Top Location Restrictions"
        )


        st_echarts(
            options=loc_pie_option,
            height="360px",
            key="location_pie"
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )




# ---------------------------------------------------------
# Section 2
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">💎 Regional Seniority Premium Gap</div>',
    unsafe_allow_html=True
)



if "seniority" in salary_df.columns:

    seniority_order = [
        "Entry-level",
        "Mid-level",
        "Senior",
        "Executive"
    ]

    # ۱. انتخاب ۴ منطقه پرتقاضا
    top_regions = (
        salary_df["Region"]
        .value_counts()
        .head(4)
        .index
    )

    # ۲. محاسبه میانگین حقوق مناطق و مرتب‌سازی آنها (نزولی: از بیشترین به کمترین)
    sorted_region_order = (
        salary_df[salary_df["Region"].isin(top_regions)]
        .groupby("Region")["Avg_Salary_USD_Annual"]
        .mean()
        .sort_values(ascending=False)  # برای صعودی کردن عبارت را True کنید
        .index
    )

    # ۳. ساخت پیوت تیبل و اعمال ترتیب بر اساس ردیف (index) و ستون (columns)
    pivot_df = (
        salary_df[
            salary_df["Region"].isin(top_regions)
            &
            salary_df["seniority"].isin(seniority_order)
        ]
        .groupby(["Region", "seniority"])["Avg_Salary_USD_Annual"]
        .mean()
        .unstack()
        .reindex(
            columns=seniority_order,
            index=sorted_region_order  # <--- مرتب‌سازی محور X بر اساس میانگین حقوق
        )
        .fillna(0)
    )

    series = []

    for level in seniority_order:
        if level in pivot_df.columns:
            series.append(
                {
                    "name": level,
                    "type": "bar",
                    "data": [
                        round(x, 0)
                        for x in pivot_df[level]
                    ]
                }
            )

    if not pivot_df.empty:
        group_option = {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"}
            },
            "legend": {
                "data": seniority_order
            },
            "xAxis": {
                "type": "category",
                "data": [str(r) for r in pivot_df.index.tolist()] # دریافت محور X مرتب‌شده
            },
            "yAxis": {
                "type": "value"
            },
            "series": series
        }

        st_echarts(
            options=group_option,
            height="380px",
            key="seniority_region"
        )

else:
    st.warning("Seniority column not available.")




# ---------------------------------------------------------
# Section 3
# ---------------------------------------------------------

with st.expander(
    "🔍 Explore Raw Regional Data"
):


    geo_summary = (
        salary_df
        .groupby("Region")
        .agg(

            Total_Jobs=("Title","count"),

            Min_Salary_USD=(
                "Min_Salary_USD_Annual",
                "min"
            ),

            Avg_Salary_USD=(
                "Avg_Salary_USD_Annual",
                "mean"
            ),

            Max_Salary_USD=(
                "Max_Salary_USD_Annual",
                "max"
            )
        )

        .reset_index()

        .sort_values(
            "Avg_Salary_USD",
            ascending=False
        )
    )


    st.dataframe(
        geo_summary.style.format(
            {
                "Min_Salary_USD":"${:,.0f}",
                "Avg_Salary_USD":"${:,.0f}",
                "Max_Salary_USD":"${:,.0f}",
                "Total_Jobs":"{:,}"
            }
        ),

        use_container_width=True
    )
    
# ---------------------------------------------------------
# Section 4
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">💲🌐 Currency & Language affect on Market Share</div>',
    unsafe_allow_html=True,
)

col3,col4 = st.columns(2)

# ------------------------------
# Fig1: Currency
# ------------------------------

df_cur_groupped = (
    df.groupby("Currency")["Avg_Salary_USD_Annual"]
    .agg(["count", "mean"])
    .reset_index()
)

# Top 10 currencies by number of job postings
top_10_currencies = (
    df_cur_groupped
    .nlargest(10, "count")
    .sort_values("count", ascending=True)
)


fig1 = px.bar(
    top_10_currencies,

    x="Currency",
    y="count",

    title="Top 10 Currencies in Remote Job Postings",

    color="mean",
    color_continuous_scale="ylgn",

    

    # Reverse category order → bars go from right to left
    category_orders={
        "Currency": top_10_currencies["Currency"].tolist()
    },
)


# ---------------------------------------------------------
# Logarithmic Y-axis
# ---------------------------------------------------------

fig1.update_yaxes(
    type="log",
    title_standoff=15,
    side="right"
)


# ---------------------------------------------------------
# Move Colorbar to the Left
# ---------------------------------------------------------

fig1.update_layout(

    coloraxis_colorbar=dict(

        # Move colorbar to left
        x=-0.12,

        xanchor="right",

        y=0.5,

        yanchor="middle",

        len=0.7,
    ),

    # Give enough space for colorbar on the left
    

)


with col3:
    with st.container(border=True):
        st.plotly_chart(fig1)
        
# ------------------------------
# Fig2: Language
# ------------------------------
df_lan_groupped = df.groupby('Language')['Avg_Salary_USD_Annual'].agg(['count','mean']).reset_index()

fig2 = px.bar(df_lan_groupped.nlargest(10, 'count'),y='count',x='Language', title='Top 10 Languages on Remote Jobs',
              color='mean',color_continuous_scale='OrRd')
fig2.update_yaxes(type='log')

with col4:
    with st.container(border=True):
        st.plotly_chart(fig2)
        
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ---------------------------------------------------------
# Section 5: Job Opportunities by Country
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">🌍 Job Opportunities by Country</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-subtitle">
        Explore job demand and salary levels across geographic locations.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Prepare Location Data
# ---------------------------------------------------------

df_loc = df.copy()

df_loc["Location Restrictions"] = (
    df_loc["Location Restrictions"]
    .fillna("Unknown")
    .astype(str)
)

# Split multiple locations and explode them into separate rows
df_loc["Location Restrictions"] = (
    df_loc["Location Restrictions"]
    .str.split(",")
)

df_loc_exploded = df_loc.explode(
    "Location Restrictions"
).copy()

# Clean location names
df_loc_exploded["Location Restrictions"] = (
    df_loc_exploded["Location Restrictions"]
    .str.strip()
)

# Remove empty values
df_loc_exploded = df_loc_exploded[
    df_loc_exploded["Location Restrictions"].ne("")
]


# ---------------------------------------------------------
# Country / Location Filter
# ---------------------------------------------------------

available_locations = sorted(
    df_loc_exploded["Location Restrictions"]
    .dropna()
    .unique()
    .tolist()
)
with st.container(border=True):
    selected_locations = st.multiselect(
        "Select Countries / Locations",
        options=available_locations,
        default=[],
        placeholder="All Countries / Locations",
    )


    # ---------------------------------------------------------
    # Apply Location Filter
    # ---------------------------------------------------------

    if selected_locations:

        filtered_loc = df_loc_exploded[
            df_loc_exploded["Location Restrictions"].isin(
                selected_locations
            )
        ].copy()

    else:

        filtered_loc = df_loc_exploded.copy()


    # ---------------------------------------------------------
    # Aggregation by Category
    # ---------------------------------------------------------

    cat_summary = (
        filtered_loc
        .groupby("Standard Category")
        .agg(
            job_count=("Title", "count"),
            avg_salary=("Avg_Salary_USD_Annual", "mean"),
        )
        .reset_index()
        .sort_values(
            "job_count",
            ascending=True
        )
    )


    # ---------------------------------------------------------
    # Empty Data Check
    # ---------------------------------------------------------

    if cat_summary.empty:

        st.warning(
            "No job postings are available for the selected locations."
        )

    else:

        # -----------------------------------------------------
        # Create Subplots
        # -----------------------------------------------------

        fig3 = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=(
                "Job Postings by Category",
                "Average Annual Salary by Category",
            ),
            shared_yaxes=True,
            horizontal_spacing=0.12,
        )


        # -----------------------------------------------------
        # Job Postings
        # -----------------------------------------------------

        fig3.add_trace(

            go.Bar(

                x=cat_summary["job_count"],

                y=cat_summary["Standard Category"],

                orientation="h",

                name="Job Postings",

                marker_color="#636EFA",

                text=cat_summary["job_count"],

                textposition="auto",

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Job Postings: %{x:,}"
                    "<extra></extra>"
                ),
            ),

            row=1,
            col=1,
        )


        # -----------------------------------------------------
        # Average Salary
        # -----------------------------------------------------

        fig3.add_trace(

            go.Bar(

                x=cat_summary["avg_salary"],

                y=cat_summary["Standard Category"],

                orientation="h",

                name="Average Annual Salary",

                marker_color="#00CC96",

                text=cat_summary["avg_salary"].apply(
                    lambda x:
                        f"${x / 1000:.1f}k"
                        if pd.notna(x)
                        else "N/A"
                ),

                textposition="auto",

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Average Annual Salary: $%{x:,.0f}"
                    "<extra></extra>"
                ),
            ),

            row=1,
            col=2,
        )


        # -----------------------------------------------------
        # Selected Location Label
        # -----------------------------------------------------

        location_label = (
            ", ".join(selected_locations)
            if selected_locations
            else "All Countries / Locations"
        )


        # -----------------------------------------------------
        # Layout
        # -----------------------------------------------------

        fig3.update_layout(

            template="plotly_dark",

            title=dict(
                text=(
                    "Job Market Overview: Demand and Compensation"
                    f"<br><sup>{location_label}</sup>"
                ),
                x=0.5,
                xanchor="center",
            ),

            showlegend=False,

            height=650,

            margin=dict(
                l=30,
                r=30,
                t=100,
                b=40,
            ),
        )


        # -----------------------------------------------------
        # Axis Formatting
        # -----------------------------------------------------

        fig3.update_xaxes(
            title_text="Number of Job Postings",
            row=1,
            col=1,
        )


        fig3.update_xaxes(
            title_text="Average Annual Salary (USD)",
            tickprefix="$",
            tickformat=",",
            row=1,
            col=2,
        )


        fig3.update_yaxes(
            title_text="",
            row=1,
            col=1,
        )


        # -----------------------------------------------------
        # Display
        # -----------------------------------------------------

        st.plotly_chart(
            fig3,
            use_container_width=True,
        )
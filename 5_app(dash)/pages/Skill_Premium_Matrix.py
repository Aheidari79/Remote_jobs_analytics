import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from utils import load_data, apply_custom_css
import plotly.express as px

# 1. Configuration
st.set_page_config(page_title="Skill Premium Matrix", page_icon="🧠", layout="wide")

# 2. Shared Setup
apply_custom_css()
df = load_data()

# Filter out rows without valid salary
salary_df = df[df["Avg_Salary_USD_Annual"].notnull() & (df["Avg_Salary_USD_Annual"] > 0)].copy()

# ---------------------------------------------------------
# Header / Hero Section
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🧠 Skill Premium Matrix</h1>
        <p>
            Discover the true market value of different skills. Compare job volume (demand) 
            against average compensation (premium) to identify the most lucrative niches.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Data Processing: Extracting Flags
# ---------------------------------------------------------
# پیدا کردن تمام ستون‌هایی که با flag_ شروع می‌شوند
flag_cols = [col for col in salary_df.columns if str(col).startswith("flag_")]

skill_data = []
for col in flag_cols:
    # تبدیل مقادیر ستون به عدد (برای اطمینان از اینکه 1 و 0 یا True/False هستند)
    salary_df[col] = pd.to_numeric(salary_df[col], errors='coerce').fillna(0)
    
    # فیلتر کردن آگهی‌هایی که این مهارت را دارند
    subset = salary_df[salary_df[col] > 0]
    
    if not subset.empty:
        count = len(subset)
        avg_sal = subset["Avg_Salary_USD_Annual"].mean()
        
        # تمیز کردن نام مهارت برای نمایش زیبا
        skill_name = col.replace("flag_", "").replace("_", " ").title()
        # تغییر نام‌های خاص برای خوانایی بهتر
        if skill_name == "Data Ai Ml": skill_name = "Data / AI / ML"
        elif skill_name == "Sales Ae": skill_name = "Sales / AE"
        elif skill_name == "Tech Stack": skill_name = "General Tech Stack"
        elif skill_name == "Software Dev": skill_name = "Software Dev"
        
        skill_data.append({
            "Skill": skill_name, 
            "Count": count, 
            "Avg_Salary": avg_sal
        })

# تبدیل به دیتافریم و مرتب‌سازی
skill_df = pd.DataFrame(skill_data)
if not skill_df.empty:
    skill_df = skill_df.sort_values("Avg_Salary", ascending=False)

# ---------------------------------------------------------
# Aggregation & Top KPIs
# ---------------------------------------------------------
if not skill_df.empty:
    top_paying_skill = skill_df.iloc[0]["Skill"]
    top_paying_val = skill_df.iloc[0]["Avg_Salary"]
    
    most_demanded_skill = skill_df.sort_values("Count", ascending=False).iloc[0]["Skill"]
    most_demanded_val = skill_df.sort_values("Count", ascending=False).iloc[0]["Count"]
    
    avg_matrix_salary = skill_df["Avg_Salary"].mean()
else:
    top_paying_skill, most_demanded_skill = "N/A", "N/A"
    top_paying_val, most_demanded_val, avg_matrix_salary = 0, 0, 0

def render_kpi(title, value, sub_text, delta_class="delta-up"):
    html_string = (
        '<div class="kpi">'
        f'<div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<span class="delta {delta_class}">{sub_text}</span>'
        '</div>'
    )
    st.markdown(html_string, unsafe_allow_html=True)

cols = st.columns(3, gap="small")

with cols[0]:
    render_kpi("Highest Paying Skill", top_paying_skill, f"${top_paying_val:,.0f} Avg")

with cols[1]:
    render_kpi("Most Demanded Skill", most_demanded_skill, f"{most_demanded_val:,} Postings")

with cols[2]:
    render_kpi("Matrix Avg Salary", f"${avg_matrix_salary:,.0f}", "Across all tracked skills")

st.write("")

# ---------------------------------------------------------
# Section 1: The Matrix (Scatter Plot)
# ---------------------------------------------------------

df3 = df
# محاسبه میانه حقوق کل بازار به عنوان خط پایه
overall_median = df3['Avg_Salary_USD_Annual'].median()

skill_stats = []
# فرض می‌کنیم ستون‌های فلگ شما با کلمه flag شروع می‌شوند
flag_cols = [col for col in df3.columns if col.startswith('flag_')]

for col in flag_cols:
    demand = df3[col].sum()
    if demand > 0:
        # محاسبه میانه حقوق فقط برای آگهی‌هایی که این مهارت را دارند
        skill_median = df3[df3[col] == 1]['Avg_Salary_USD_Annual'].median()
        premium = skill_median - overall_median # اختلاف حقوق با میانه کل
        
        # پاک کردن کلمه flag_ برای زیبایی نام در نمودار
        skill_name = col.replace('flag_', '').replace('_', ' ').title()
        skill_stats.append({'Skill': skill_name, 'Demand': demand, 'Salary_Premium': premium})

df3_skills = pd.DataFrame(skill_stats)
median_demand = df3_skills['Demand'].median()

st.info(
    "💡 **Note:** **Radiology** is outside the initial view due to its high premium ($400k+). Zoom out or scroll on the chart to view it."
)

# رسم نمودار پراکندگی (Scatter Plot)
fig1 = px.scatter(
    df3_skills.query("-50000 < Salary_Premium < 100000"), 
    x='Demand', 
    y='Salary_Premium', 
    size='Demand', # حباب‌های بزرگتر برای تقاضای بیشتر
    color='Salary_Premium',
    color_continuous_scale='RdYlGn',
    title='Skill Premium vs. Market Demand (The 4 Quadrants of Value)',
    labels={'Demand': 'Number of Job Postings', 'Salary_Premium': 'Salary Premium'},
    #template='plotly_dark',
    hover_name='Skill'
)

# اضافه کردن خطوط متقاطع برای ساختن 4 ربع (Quadrants)
fig1.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Market Average Salary",)
fig1.add_vline(x=median_demand, line_dash="dash", line_color="blue", annotation_text="Median Demand",annotation_position='bottom')
fig1.update_traces(textposition='middle right')
fig1.update_layout( height=600, showlegend=False,)

df_filtered = df3_skills.query("-50000 < Salary_Premium")

custom_offsets = {
    'Data Ai Ml': {'ax': -25, 'ay': -20},      # شیفت به بالا و چپ
    'Cloud Devops': {'ax': 50, 'ay': 20},      # شیفت به پایین و راست
    'Healthcare Clinical': {'ax': -40, 'ay': 30}, # شیفت به پایین و چپ
    'Sales Ae': {'ax': 40, 'ay': -40},         # شیفت به بالا و راست
    'Legal': {'ax': 0, 'ay': -30},
    'Cybersecurity': {'ax': -25, 'ay': -20},
    'Cloud Devops': {'ax': -25, 'ay': 20},
    'Python': {'ax': -25, 'ay': -20},
    'Finance Accounting': {'ax': -25, 'ay': 20},
    'Tech Stack': {'ax': -25, 'ay': -20},
}

for i, row in df_filtered.iterrows():
    skill = row['Skill']
    
    # ۲. مقادیر پیش‌فرض برای اکثر نقاط
    ax_val = 30
    ay_val = -30
    
    # ۳. بررسی شرط: اگر نام مهارت در دیکشنری ما بود، مقادیر اختصاصی را جایگزین کن
    if skill in custom_offsets:
        ax_val = custom_offsets[skill]['ax']
        ay_val = custom_offsets[skill]['ay']
        
    fig1.add_annotation(
        x=row['Demand'],
        y=row['Salary_Premium'],
        text=skill,
        showarrow=True,
        arrowhead=1,
        arrowsize=1,
        arrowwidth=1,
        arrowcolor="gray",
        ax=ax_val,
        ay=ay_val,
        font=dict(size=10, color="black")
    )
    fig1.add_annotation(
    text="Size = Demand",  # متنی که می‌خواهید نمایش داده شود
    xref="paper",          # مبنای محور X را کل صفحه قرار می‌دهد
    yref="paper",          # مبنای محور Y را کل صفحه قرار می‌دهد
    x=0.98,                # موقعیت افقی (نزدیک به لبه سمت راست)
    y=0.02,                # موقعیت عمودی (نزدیک به لبه پایین)
    xanchor="right",       # نقطه لنگر متن سمت راست باشد
    yanchor="bottom",      # نقطه لنگر متن پایین باشد
    showarrow=False,       # بدون فلش
    font=dict(size=12, color="white"),
    bgcolor="rgba(30, 30, 30, 0.7)", # پس‌زمینه تیره و نیمه‌شفاف برای خوانایی بهتر
    bordercolor="gray",    # رنگ حاشیه باکس
    borderwidth=1,         # ضخامت حاشیه
    borderpad=5            # فاصله متن تا حاشیه باکس
)
fig1.update_layout(yaxis=dict(range=[-50000, 40000]))  # تنظیم محدوده فوکوس


with st.container(border=True):   
    st.markdown(
        '<div class="section-title">🎯 Demand vs. Premium Matrix</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">Top right quadrant represents high demand AND high pay.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig1)

# ---------------------------------------------------------
# Section 2: Bar Charts (Rankings)
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title" style="margin-top:1.8rem;">🏆 Skill Rankings</div>',
    unsafe_allow_html=True,
)

if not skill_df.empty:
    skill_names = skill_df["Skill"].tolist()
    salary_values = [round(float(v), 0) for v in skill_df["Avg_Salary"]]
    
    # مرتب‌سازی بر اساس تعداد برای چارت دوم
    demand_df = skill_df.sort_values("Count", ascending=True)
    demand_names = demand_df["Skill"].tolist()
    demand_values = [int(v) for v in demand_df["Count"]]

    salary_bar_option = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 130, "right": 40, "top": 20, "bottom": 30},
        "xAxis": {"type": "value", "axisLabel": {"formatter": "${value}"}},
        "yAxis": {"type": "category", "data": skill_names[::-1]}, # برعکس کردن برای نمایش از بالا به پایین
        "series": [
            {
                "name": "Avg Salary",
                "type": "bar",
                "data": salary_values[::-1],
                "itemStyle": {"color": "#10B981", "borderRadius": [0, 5, 5, 0]},
                "label": {"show": True, "position": "right", "formatter": "${c}"}
            }
        ]
    }

    demand_bar_option = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 130, "right": 40, "top": 20, "bottom": 30},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "category", "data": demand_names},
        "series": [
            {
                "name": "Job Postings",
                "type": "bar",
                "data": demand_values,
                "itemStyle": {"color": "#F59E0B", "borderRadius": [0, 5, 5, 0]},
                "label": {"show": True, "position": "right"}
            }
        ]
    }

    c1, c2 = st.columns(2, gap="medium")

    with c1:
        with st.container(border=True):
            st.markdown("##### 💰 Top Paying Skills")
            st_echarts(options=salary_bar_option, height="400px", key="skill_salary_bar")
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        with st.container(border=True):
            st.markdown("##### 📈 Most Demanded Skills")
            st_echarts(options=demand_bar_option, height="400px", key="skill_demand_bar")
            st.markdown("</div>", unsafe_allow_html=True)
        
# ---------------------------------------------------------
# Section 3: treemap Charts (Rankings)
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title" style="margin-top:1.8rem;">🔬 Skill Demand & Average Salary in a look</div>',
    unsafe_allow_html=True,
)

df['Category'] =  df['Category'].str.split(', ')
df = df.explode('Category').reset_index(drop=True)

df_cat_exp_stats = (df.groupby(['Standard Category','Category'])['Avg_Salary_USD_Annual'].agg(['count','median', 'mean','sum'])).reset_index()
df_cat_exp_stats = df_cat_exp_stats.nlargest(40 ,'count')
df_cat_exp_stats = df_cat_exp_stats.sort_values(by='mean',ascending=False).head(40).reset_index(drop=True)

fig2 = px.treemap(
    df_cat_exp_stats,
    path=['Standard Category', 'Category'],
    values='count',
    color='median',
    color_continuous_scale='ylgn',
    title='Top 20 Job Roles by Posting counts',
)

st.plotly_chart(fig2)
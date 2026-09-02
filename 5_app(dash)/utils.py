import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

@st.cache_data
def load_data():
    """
    Load and process the dataset once for all pages.
    """

    BASE_DIR = Path(__file__).resolve().parent
    DATA_PATH = BASE_DIR.parent / "3_data" / "final.csv"

    df = pd.read_csv(DATA_PATH)


    # Expand seniority column
    if "seniority" in df.columns:

        df = (
            df.assign(
                seniority=df["seniority"].str.split(", ")
            )
            .explode("seniority")
            .reset_index(drop=True)
        )


    return df



# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

def apply_custom_css():

    """
    Apply unified dashboard styling.
    """

    st.markdown(

        """

<style>


/* =====================================
   Global Variables
===================================== */

:root {

    --navy:#1f2c43;
    --navy-light:#33445f;

    --text:#303441;

    --muted:#6d717a;

    --green:#16c766;
    --green-bg:#e7f8ee;

    --red:#ff4b4b;
    --red-bg:#ffebeb;

    --border:#e0e2e7;

}




/* =====================================
   Main Layout
===================================== */


.block-container {

    max-width:1280px;

    padding-top:2rem;

    padding-bottom:2rem;

}





/* =====================================
   Sidebar
===================================== */


section[data-testid="stSidebar"] {

    background:var(--navy);

}



/* Sidebar titles and labels */


section[data-testid="stSidebar"] label {

    color:#f5f7fb !important;

    font-size:0.95rem;

    font-weight:600;

}



section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p {

    color:#f5f7fb !important;

}





/* =====================================
   Selectbox / Multiselect
===================================== */



section[data-testid="stSidebar"] div[data-baseweb="select"] > div {

    background:white !important;

    border-radius:9px !important;

    border:none !important;

}



/* Selected text */


section[data-testid="stSidebar"] div[data-baseweb="select"] span {

    color:#303441 !important;

}



/* Placeholder */


section[data-testid="stSidebar"] div[data-baseweb="select"] input {

    color:#303441 !important;

}



/* Arrow */


section[data-testid="stSidebar"] svg {

    fill:#303441 !important;

}



/* Dropdown menu */


div[data-baseweb="popover"] {

    color:#303441 !important;

}



div[data-baseweb="popover"] li {

    color:#303441 !important;

    background:white !important;

}



div[data-baseweb="popover"] li:hover {

    background:#e7f8ee !important;

}





/* =====================================
   Sidebar Brand
===================================== */


.brand {

    font-size:1.65rem;

    font-weight:800;

    margin-bottom:1.2rem;

    display:flex;

    gap:0.5rem;

    align-items:center;
    
    color:#d4d4d4;

}





.sidebar-section-title {


    font-size:1.1rem;

    font-weight:800;

    margin:1.3rem 0 0.9rem;


    color:#d4d4d4;


}





/* =====================================
   Hero
===================================== */


.hero h1 {

    margin:0;

    font-size:3rem;

    letter-spacing:-1.8px;

    color:var(--text);

}



.hero p {

    margin:0.7rem 0;

    color:#494a52;

    font-size:1.12rem;

    line-height:1.6;

}




.period {

    color:#505461;

    font-size:1.05rem;

}





/* =====================================
   Section Titles
===================================== */


.section-title {

    margin-top:1.2rem;

    margin-bottom:0.25rem;

    font-size:1.75rem;

    font-weight:800;

    color:var(--text);

}



.section-subtitle {

    color:var(--muted);

    font-size:1rem;

    margin-bottom:0.7rem;

}





/* =====================================
   KPI Cards
===================================== */


.kpi {


    background:white;

    border:1px solid var(--border);

    border-radius:16px;

    padding:18px;

    min-height:152px;

    box-shadow:
    0 1px 2px rgba(0,0,0,0.02);


}



.kpi-title {

    font-size:0.95rem;

    color:#555a66;

}



.kpi-value {

    font-size:2.25rem;

    color:var(--text);

    font-weight:500;

}





.delta {


    display:inline-block;

    margin-top:0.35rem;

    padding:3px 8px;

    border-radius:14px;

    font-size:0.8rem;

    font-weight:600;

}



.delta-up {

    color:#139b4e;

    background:var(--green-bg);

}



.delta-down {

    color:#d94040;

    background:var(--red-bg);

}





/* =====================================
   Chart Cards
===================================== */


.chart-card {


    border:1px solid var(--border);

    border-radius:16px;

    padding:8px 12px 4px;

    background:white;


}




/* =====================================
   Code
===================================== */


code {


    background:#f3f4f6;

    padding:2px 6px;

    border-radius:4px;


}





/* =====================================
   Responsive
===================================== */


@media(max-width:900px){


.hero h1{

font-size:2.2rem;

}


.kpi-value{

font-size:1.8rem;

}


}



</style>


        """,

        unsafe_allow_html=True,

    )
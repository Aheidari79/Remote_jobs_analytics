import re
import pandas as pd
from cat_rules import CATEGORY_RULES
from pathlib import Path
import numpy as np

from langdetect import detect


def normalize_text(text):
    if pd.isna(text) or not text:
        return ""

    text = str(text).lower()

    text = text.replace("_", "-")
    text = text.replace(" ", "-")

    text = re.sub(r"[^a-z0-9\-]", "", text)
    text = re.sub(r"-+", "-", text)

    return text


def build_search_fields(row):
    return {
        "title": normalize_text(row.get("Title", "")),
        "parent": normalize_text(row.get("Parent Categories", "")),
        "category": normalize_text(row.get("Category", "")),
        "excerpt": normalize_text(row.get("Excerpt", "")),
    }


def classify_job(row):
    fields = build_search_fields(row)

    scores = {}

    for category, rules in CATEGORY_RULES.items():

        score = 0

        # ---------------------------------
        # STRONG KEYWORDS
        # ---------------------------------

        for keyword in rules["strong"]:

            keyword = normalize_text(keyword)

            if keyword in fields["title"]:
                score += 5

            if keyword in fields["parent"]:
                score += 4

            if keyword in fields["category"]:
                score += 3

            if keyword in fields["excerpt"]:
                score += 1

        # ---------------------------------
        # WEAK KEYWORDS
        # ---------------------------------

        for keyword in rules["weak"]:

            keyword = normalize_text(keyword)

            if keyword in fields["title"]:
                score += 2

            if keyword in fields["parent"]:
                score += 2

            if keyword in fields["category"]:
                score += 1

            if keyword in fields["excerpt"]:
                score += 1

        scores[category] = score

    # مرتب‌سازی از بیشترین امتیاز به کمترین
    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # هیچ تطابقی پیدا نشده
    if not ranked or ranked[0][1] == 0:
        return "Other", None

    primary = ranked[0][0]

    secondary = None

    # دسته دوم فقط وقتی امتیاز قابل‌توجهی داشته باشد
    if len(ranked) > 1 and ranked[1][1] >= 4:
        secondary = ranked[1][0]

    return primary, secondary


# ---------------------------------
# LOAD DATA
# ---------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

df = pd.read_csv(BASE_DIR / "3_data" / "himalayas_jobs_50000.csv")


# ---------------------------------
# CLASSIFY
# ---------------------------------

df[["Standard Category", "Secondary Category"]] = (
    df.apply(
        classify_job,
        axis=1,
        result_type="expand"
    )
)

# ---------------------------------
# map region
# ---------------------------------
def map_region(location_str):
  if pd.isna(location_str) or 'Worldwide' in location_str:
    return 'Worldwide / Unrestricted'

  # بررسی وجود کشورهای کلیدی در متن
  if any(
      c in location_str
      for c in [
          'United States',
          'Canada',
      ]
  ):
    return 'North America'
  elif any(
      c in location_str
      for c in [
          'Germany',
          'United Kingdom',
          'France',
          'Spain',
          'Italy',
          'Poland',
          'Sweden',
      ]
  ):
    return 'Europe / EU'
  elif any(
      c in location_str
      for c in [
          'Brazil',
          'Argentina',
          'Chile',
          'Mexico',
          'Colombia',
      ]
  ):
    return 'LATAM'
  elif any(
      c in location_str
      for c in [
          'Australia',
          'Singapore',
          'India',
          'Japan',
      ]
  ):
    return 'APAC'
  else:
    return 'Other Regions'


# ساخت ستون جدید منطقه
df['Region'] = df['Location Restrictions'].apply(map_region)

# ---------------------------------
# Salary Normalization
# ---------------------------------

# نرخ تبدیل تقریبی ارزها به دلار آمریکا (USD)
# در صورت اضافه شدن ارز جدید به دیتاست، فقط کافیست آن را به این دیکشنری اضافه کنید
#Currency values were converted to USD using fixed reference exchange rates.
EXCHANGE_RATES_TO_USD = {
    'USD': 1.000000,

    'EUR': 1.153500,
    'GBP': 1.344954,
    'CAD': 0.712873,
    'AUD': 0.700662,
    'CHF': 1.237661,

    'PLN': 0.268362,
    'INR': 0.010489,
    'ZAR': 0.060717,
    'PHP': 0.016413,

    'SGD': 0.780288,
    'BRL': 0.197335,
    'HKD': 0.127509,

    'SEK': 0.105012,
    'CZK': 0.047545,
    'DKK': 0.154302,
    'JPY': 0.006316,
    'HUF': 0.003165,
    'NOK': 0.104897,
    'NZD': 0.587441,

    'CLP': 0.00109,
    'IDR': 0.000056,
    'THB': 0.029998,
    'TRY': 0.021036,
    'ILS': 0.327755,
    'MXN': 0.057734,
}


def normalize_salary(row):
  """محاسبه حقوق حداقل، حداکثر و میانگین سالانه به دلار (USD)"""
  min_sal = row.get('Min Salary')
  max_sal = row.get('Max Salary')
  period = str(row.get('Salary Period', '')).lower().strip()
  currency = str(row.get('Currency', '')).upper().strip()

  # ۱. اگر هر دو مقدار نال باشند
  if pd.isna(min_sal) and pd.isna(max_sal):
    return np.nan, np.nan, np.nan

  # ۲. اگر یکی از مقادیر نال باشد، با دیگری جایگزین می‌شود
  if pd.isna(min_sal):
    min_sal = max_sal
  if pd.isna(max_sal):
    max_sal = min_sal

  # ۳. ضریب تبدیل دوره زمانی به حالت سالانه
  period_multiplier = 1.0
  if 'month' in period:
    period_multiplier = 12.0
  elif 'hour' in period:
    period_multiplier = 2080.0  # ۴۰ ساعت در هفته × ۵۲ هفته'
  # ۴. ضریب تبدیل نرخ ارز
  elif 'fortnightly' in period:
      period_multiplier = 26
  elif 'weekly' in period:
      period_multiplier = 52
  rate = EXCHANGE_RATES_TO_USD.get(currency, 1.0)

  # ۵. محاسبه حقوق سالانه بر حسب دلار
  min_annual_usd = min_sal * period_multiplier * rate
  max_annual_usd = max_sal * period_multiplier * rate
  avg_annual_usd = (min_annual_usd + max_annual_usd) / 2.0

  return min_annual_usd, max_annual_usd, avg_annual_usd


def process_salary_dataframe(df):
  """اعمال تابع نرمالسازی روی کل دیتافریم و افزودن ستون‌های جدید"""
  df_copy = df.copy()

  results = df_copy.apply(normalize_salary, axis=1)

  df_copy['Min_Salary_USD_Annual'] = [r[0] for r in results]
  df_copy['Max_Salary_USD_Annual'] = [r[1] for r in results]
  df_copy['Avg_Salary_USD_Annual'] = [r[2] for r in results]

  return df_copy

df = process_salary_dataframe(df)

# ---------------------------------
# Language detection:
# ---------------------------------

# نیازمند نصب کتابخانه langdetect: pip install langdetect


def get_language(text):
  try:
    return detect(text) if len(text) > 20 else 'unknown'
  except:
    return 'unknown'


df['Language'] = df['Excerpt'].apply(get_language)


# ---------------------------------
# separating seniorities bu dummies
# ---------------------------------

df['seniority'] = df['seniority'].str.replace('Senior, Manager' ,'Manager, Senior' )
df['seniority'] = df['seniority'].str.replace('Manager, Executive' ,'Executive, Manager' )
df['seniority'] = df['seniority'].str.replace('Director, Senior' ,'Senior, Director' )
df_seniority = df['seniority'].str.get_dummies(', ')
df = pd.concat([df, df_seniority], axis=1)


# ---------------------------------
# SAVE
# ---------------------------------

df.to_csv(
    BASE_DIR / "3_data" / "standardized.csv",
    index=False
)
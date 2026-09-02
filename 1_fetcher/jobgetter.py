import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def convert_timestamp(timestamp):
    if timestamp is None:
        return None

    return datetime.fromtimestamp(timestamp).date()


def fetch_himalayas_jobs(
    total_jobs, limit_per_request=20, output_csv="3_data/himalayas_jobs_50000.csv"
):
  """دریافت آگهی‌های شغلی از API سایت Himalayas و ذخیره آن‌ها در قالب فایل CSV.

  توضیحات پارامترهای API:
  - limit: حداکثر ۲۰ شغل در هر درخواست
  - offset: تعداد آیتم‌هایی که برای صفحه‌بندی باید اسکیپ شوند
  """
  base_url = "https://himalayas.app/jobs/api"
  all_jobs = []

  print(
      f"شروع دریافت داده‌ها از Himalayas API (هدف: {total_jobs} شغل)..."
  )

  for offset in range(0, total_jobs, limit_per_request):
    params = {"limit": limit_per_request, "offset": offset}

    try:
      response = requests.get(base_url, params=params, timeout=10)

      if response.status_code == 200:
        data = response.json()
        jobs = data.get("jobs", [])

        if not jobs:
          print("آگهی شغلی دیگری در API یافت نشد.")
          break

        for job in jobs:
          # تبدیل لیست‌ها به رشته متنی برای ساختار تمیزتر در CSV
          loc_restrictions = (
              ", ".join(job.get("locationRestrictions") or [])
              if job.get("locationRestrictions")
              else "Worldwide / Unrestricted"
          )
          tz_restrictions = (
              ", ".join(job.get("timezoneRestriction") or [])
              if job.get("timezoneRestriction")
              else "Any"
          )
          categories = (
              ", ".join(job.get("categories") or [])
              if job.get("categories")
              else ""
          )
          parent_categories = (
              ", ".join(job.get("parentCategories") or [])
              if job.get("parentCategories")
              else ""
          )
          seniority = (
              ", ".join(job.get('seniority') or [])
              if job.get('seniority')
              else ''
          )
          html = job.get("description")
          soup = BeautifulSoup(html, "xml")

          all_jobs.append({
              
              "Title": job.get("title"),
              "Company Name": job.get("companyName"),
              "Company Slug": job.get("companySlug"),
              'seniority': seniority,
              "Employment Type": job.get("employmentType"),
              "Parent Categories": parent_categories,
              "Category": categories,
              "Location Restrictions": loc_restrictions,
              "Timezone Restrictions": tz_restrictions,
              "Min Salary": job.get("minSalary"),
              "Max Salary": job.get("maxSalary"),
              "Salary Period": job.get("salaryPeriod"),
              "Currency": job.get("currency"),
              "Published Date": (job.get("pubDate")),
              "Published Date(STD)": convert_timestamp(job.get("pubDate")),
              "Expiry Date": job.get("expiryDate"),
              "Expiry Date(STD)": convert_timestamp(job.get("expiryDate")),
              "Application Link": job.get("applicationLink"),
              "Excerpt": job.get("excerpt"),
              "GUID": job.get("guid"),
              #"Education": soup.find("li").get_text(" ", strip=True)
          })

        fetched_count = len(all_jobs)
        print(
            f"پیشرفت: دریافت {fetched_count} از {total_jobs} شغل (Offset:"
            f" {offset})"
        )

        # وقفه کوتاه برای عدم تجاوز از محدودیت نرخ درخواست (Rate Limit)
        time.sleep(0.3)
      else:
        print(
            f"خطا در دریافت داده در Offset {offset}: کد وضعیت"
            f" {response.status_code}"
        )
        break

    except Exception as e:
      print(f"خطایی رخ داد: {e}")
      break

  # ذخیره نهایی در CSV
  if all_jobs:
    df = pd.DataFrame(all_jobs)
    # استفاده از utf-8-sig برای نمایش صحیح کاراکترها در اکسل
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(
        f"\nبا موفقیت {len(df)} شغل در فایل '{output_csv}' ذخیره گردید!"
    )
  else:
    print("\nهیچ داده‌ای دریافت نشد.")


if __name__ == "__main__":
  fetch_himalayas_jobs(total_jobs=50000)
"""
Job Listings Web Scraper
Requirements:
    pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import csv

URL = "https://remoteok.com/remote-dev-jobs"  # Dev-related jobs
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_jobs():
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for tr in soup.find_all("tr", class_="job"):
        title = tr.find("h2")
        company = tr.find("h3")
        link = tr.find("a", class_="preventLink")

        if title and company and link:
            job = {
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "link": "https://remoteok.com" + link["href"]
            }
            jobs.append(job)

    return jobs

def save_to_csv(jobs, filename="jobs.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "company", "link"])
        writer.writeheader()
        writer.writerows(jobs)

if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"✅ Found {len(jobs)} jobs")
    for j in jobs[:5]:  # show first 5
        print(f"{j['title']} — {j['company']} ({j['link']})")

    save_to_csv(jobs)
    print("💾 Saved to jobs.csv")

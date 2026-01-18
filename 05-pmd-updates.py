import csv 
import datetime as dt
import requests

def last_mod_dt (last_mod_str: str) -> str:
    return dt.datetime.strptime(last_mod_str, '%a, %d %b %Y %H:%M:%S %Z').isoformat(timespec="seconds")

# Base URL and chapter range 
base_url = "http://www.powermobydick.com/Moby{:03d}.html" 
chapter_range = range(1, 151)
# chapter_range = range(1, 5)
results = [] 

for i in chapter_range: 
    url = base_url.format(i)
    print(f"Checking last-modified for chapter {i}, {url}")
    try: 
        response = requests.head(url, timeout=10) 
        last_str = response.headers.get("Last-Modified", "No date available")
        last_iso = last_mod_dt(last_str)

        results.append((url, last_iso)) 
    except Exception as e: 
        results.append((url, f"Error: {e}")) 

# Sort results from latest to oldest last-modified date
results = sorted(results, key=lambda x: x[1], reverse=True)

# Save results to CSV 
with open("chapter_mod_dates.csv", "w", newline="", encoding="utf-8") as csvfile: 
    writer = csv.writer(csvfile) 
    writer.writerow(["URL", "Last-Modified"]) 
    writer.writerows(results) 
    print("Results saved to chapter_mod_dates.csv")
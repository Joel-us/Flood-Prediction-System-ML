import requests

url = "https://diagram-chasing.github.io/cwc-flood-forecasts/DATA.md"

response = requests.get(url, timeout=30)

print("Status:", response.status_code)
print("=" * 100)
print(response.text[:20000])
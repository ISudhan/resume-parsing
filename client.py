import requests

url = "http://127.0.0.1:8000/extract_numbers"
data = {"text": """ """}

response = requests.post(url, json=data)
print(response.json())

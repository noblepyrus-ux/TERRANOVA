import requests  
import json

url = "http://127.0.0.1:8000/dashboard"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc5MTUyNjQ4OH0.EVwebdW5A0ffm-figoy2jtzPJStSVljeN2FdI56myig"
}

response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"\nTotal Fincas: {response.json()['kpis']['total_fincas']}")
print(f"\nRespuesta completa:")
print(json.dumps(response.json(), indent=2))
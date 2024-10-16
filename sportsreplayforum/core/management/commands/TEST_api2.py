import requests
import json

"""

eventresults.php?id=1963827 = Singapore result
eventresults.php?id=1963830 = USA results

eventsseason.php?id=

4490 Nations League
4849 UEFA Champions League
4328 Premier League
4380 MotoGP
4407 Moto GP
4429 World Cup

"""


url = "https://www.thesportsdb.com/api/v2/json/schedule/league/4370/2024"
api_key = 449702

headers = {
    "X-API-KEY": f"{api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers = headers)
data = response.json()

if response.status_code == 200:
    print(data)

    with open("TEST_api.json", "w") as json_file:
        
        json.dump(data, json_file, indent=4)  # 'indent=4' formats the JSON for readability
    
    print("JSON data saved successfully!")
    
else:
    print(f"Request failed with status code: {response.status_code}")

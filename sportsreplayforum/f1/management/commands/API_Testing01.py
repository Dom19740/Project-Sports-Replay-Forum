import requests
import json

"""
Singapore results = eventresults.php?id=1963827
USA results =eventresults.php?id=1963830
 """

LEAGUE_ID = '4370'
SEASON = '2024'

response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3//eventresults.php?id=1963830")

if response.status_code == 200:
    # Convert the response to JSON format
    data = response.json()
    print(data)


    # Save the JSON data to a file
    with open("api_testing01.json", "w") as json_file:
        json.dump(data, json_file, indent=4)  # 'indent=4' formats the JSON for readability
    
    print("JSON data saved successfully!")
    
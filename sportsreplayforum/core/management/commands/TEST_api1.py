import thesportsdb
import json, requests

"""
4370&s=2024 F1 2024
4490 Nations League
4849 UEFA Champions League
4328 Premier League
4380 MotoGP
4407 Moto GP
4429 World Cup
"""

response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id={4490}")


if response.status_code == 200:
    # Convert the response to JSON format
    data = response.json()
    print(data)

    # Save the JSON data to a file
    with open("TEST_api1.json", "w") as json_file:
        
        json.dump(data, json_file, indent=4)  # 'indent=4' formats the JSON for readability
    
    print("JSON data saved successfully!")
    
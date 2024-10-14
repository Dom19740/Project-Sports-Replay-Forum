import requests
import json

"""
eventresults.php?id=1963827 = Singapore result
eventresults.php?id=1963830 = USA results

eventsseason.php?id=
 """

'4490' """Nations League"""
'4849' """WSL"""
'4328' """Premier League"""
'4380' """MotoGP"""
'4407' """Moto GP"""

response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id={4328}")


if response.status_code == 200:
    # Convert the response to JSON format
    data = response.json()
    print(data)

    # Save the JSON data to a file
    with open("TEST_api.json", "w") as json_file:
        
        json.dump(data, json_file, indent=4)  # 'indent=4' formats the JSON for readability
    
    print("JSON data saved successfully!")
    
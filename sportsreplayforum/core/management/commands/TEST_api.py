import requests
import json

"""
Singapore results = eventresults.php?id=1963827
USA results = eventresults.php?id=1963830

Nations League = eventsseason.php?id=4490
 """

response = requests.get("https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4490")


if response.status_code == 200:
    # Convert the response to JSON format
    data = response.json()
    print(data)


    # Save the JSON data to a file
    with open("TEST_api.json", "w") as json_file:
        
        json.dump(data, json_file, indent=4)  # 'indent=4' formats the JSON for readability
    
    print("JSON data saved successfully!")
    
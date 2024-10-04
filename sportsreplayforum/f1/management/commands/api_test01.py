import requests
import json

# Replace 'YOUR_API_KEY' with your actual API key
response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4370&s=2024")

# Check if the response is valid
if response.status_code == 200:
    # Convert the response to JSON format
    json_data = response.json()
    
    # Save the JSON data to a file
    with open("f1_2024_races.json", "w") as json_file:
        json.dump(json_data, json_file, indent=4)  # 'indent=4' formats the JSON for readability
    
    print(json_data)
    print("JSON data saved successfully!")
else:
    print(f"Error: Received response with status code {response.status_code}")

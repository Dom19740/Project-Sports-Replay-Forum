import requests
import json


# Replace 'YOUR_API_KEY' with your actual API key
response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4370&s=2024")


# Check if the response is valid
if response.status_code == 200:
    # Convert the response to JSON format
    data = response.json()
    print(data)
    
    # Save the JSON data to a file
    with open("f1_2024_races.json", "w") as json_file:
        json.dump(data, json_file, indent=4)  # 'indent=4' formats the JSON for readability
    
    print("JSON data saved successfully!")
    
    # Assuming the API response contains a list of events
    events = data['events']
    
    competition_names = []

    for event in events:
        # Extract the text in 'strEvent'
        event_text = event['strEvent']
        
        # Check if the event text contains "Grand Prix"
        if "Grand Prix" in event_text:
            # Split the text at the word 'Prix' and take the first part
            competition_name = event_text.split('Prix')[0] + 'Prix'
            
            # Check if the competition name already exists in the list
            if competition_name not in competition_names:
                competition_names.append(competition_name)

    print(competition_names)
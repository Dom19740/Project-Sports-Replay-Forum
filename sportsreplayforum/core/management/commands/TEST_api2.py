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

""" results = thesportsdb.events.nextLeagueEvents("4490")

print(results)

with open("TEST_api2.json", "w") as json_file:
    
    json.dump(results, json_file, indent=4)  # 'indent=4' formats the JSON for readability

print("JSON data saved successfully!") """

results = thesportsdb.events.eventInfo("1008672")

print(results)
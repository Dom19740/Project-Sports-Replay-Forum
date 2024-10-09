import requests

API_KEY = '15527673485049609ca47ce541fea7ba'  # Replace with your actual API key
BASE_URL = 'https://newsapi.org/v2/everything'  # Change to the relevant F1 news API endpoint

def fetch_news():
    params = {
        'q': 'Formula 1',
        'sortBy': 'publishedAt',
        'pageSize': 10,
        'apiKey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        return []

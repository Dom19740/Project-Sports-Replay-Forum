from django.core.management.base import BaseCommand, CommandError
from openai import OpenAI
import requests, os

class Command(BaseCommand):

    
    client = OpenAI(
    api_key = os.getenv('LLAMA_API_KEY'),
    base_url = "https://api.llmapi.com"
    )

    response = client.chat.completions.create(
    model="llama3.1-70b",
    messages=[
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": "Who were the founders of Microsoft?"}
    ],
        

    )

    #print(response)
    print(response.model_dump_json(indent=2))
    print(response.choices[0].message.content)
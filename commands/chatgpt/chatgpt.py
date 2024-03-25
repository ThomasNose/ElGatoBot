from openai import OpenAI
from PIL import Image

import requests

client = OpenAI(api_key="INSERT KEY HERE")
#from settings import DISCORD_API_SECRET

def gpt(prompt: str):
    completion = client.chat.completions.create(
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        model="gpt-3.5-turbo"
    )
    return(completion.choices[0].message.content)

def imagegpt(prompt: str):
    response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )
    return(response.data[0].url)
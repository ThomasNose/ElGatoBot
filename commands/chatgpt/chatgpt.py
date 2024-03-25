from openai import OpenAI
from PIL import Image

import requests

client = OpenAI(api_key="INSERT KEY HERE")
#from settings import DISCORD_API_SECRET

#prompt = "What is the maximum number of tokens you will use by default via the API?"

def gpt(prompt: str):
    completion = client.chat.completions.create(
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        model="gpt-3.5-turbo"
        #model="gpt-4"
    )
    #print(completion.choices[0].message.content)
    return(completion.choices[0].message.content)

#print(completion.choices[0].message.content)

def imagegpt(prompt: str):
    #response = None
    response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )
    #print(requests.get(response.data[0].url))
    return(response.data[0].url)
    #try:
    #    if image.status_code == 200:
    #        with open("ai_img.png", 'wb') as f:
    #            f.write(image.content)
    #            return("ai_img.png")
    #except Exception as e:
    #    print("An error occured with image ai", e)


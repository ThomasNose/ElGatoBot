import random
import os
import json

def flexing():
    images = os.listdir("commands/flex/fleximages/")
    img = random.choice(images)

    Rare = random.randrange(50)
    if Rare == 49:
        img = "commands/flex/fleximages/rare/NickEh.gif"
    return(img)

def insult():
    with open(f"commands/flex/insults.txt", 'r') as file:
        words = json.loads(file.readline())
    noun = words["Noun"]
    adjective = words["Adjective"]
    return(str(random.choice(adjective)) + " " + str(random.choice(noun)))
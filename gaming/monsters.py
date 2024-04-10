import random
import pandas as pd
import settings
import uuid
import datetime as datetime
import json

from utils.connect_db import connect_db

postgres = settings.POSTGRES_LOGIN_DETAILS



def monster_drop(message):
    conn = connect_db(postgres)
    cur = conn.cursor()

    userid = message.author.id
    content = message.content
    created = message.created_at
    # Append user information as a dictionary
    monsterid = random.randint(1,10)
    data = {
        "monsterkey": uuid.uuid5(uuid.NAMESPACE_DNS, content + str(created)),
        "monsterid": monsterid,
        "userid": str(userid).strip(),
        "guildid": str(message.guild.id),
        "dropped_at": message.created_at
    }

    # Construct the SQL query
    query = f"INSERT INTO usermonsters values('{data['monsterkey']}', {data['monsterid']}, '{data['userid']}', '{data['guildid']}', cast('{data['dropped_at']}' as timestamp))"

    cur.execute(query)

    conn.commit()

    cur.execute(f"SELECT monstername from monsters where monsterid = {monsterid}")
    monstername = cur.fetchone()

    #with open("monsters.json", "r") as file:
    # Load the data from the file
    #    monsternames = json.load(file)
    #    file.close

    conn.close()
    return(monstername[0])
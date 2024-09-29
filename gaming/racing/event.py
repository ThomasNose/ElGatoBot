import settings
from utils.connect_db import connect_db
import json

postgres = settings.POSTGRES_LOGIN_DETAILS

async def event(msg, guild, payload = None):
    if payload != None:
        winner = payload["winner"]
        places = json.dumps(payload["places"])

    conn = connect_db(postgres)
    cur = conn.cursor()
    if payload == None:
        cur.execute(f"INSERT INTO events \
                    select 'race', '{msg}', '{guild}', Null, Null")
    else:
        cur.execute(f"UPDATE events SET winner = '{winner}', payload = '{places}' WHERE discordref = '{msg}' and guildid = '{guild}'")

    conn.commit()
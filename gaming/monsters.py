import random
import pandas as pd
import settings
import uuid
import datetime as datetime

from utils.connect_db import connect_db
from gaming.roll import CustomDistributionModel

postgres = settings.POSTGRES_LOGIN_DETAILS


def monster_drop(message):
    conn = connect_db(postgres)
    cur = conn.cursor()

    # Message contents
    userid = message.author.id
    content = message.content
    created = message.created_at


    rarity_names = {"COMMON": "1", "UNCOMMON": -2, "RARE": -3, "MYTHICAL": -4, "LEGENDARY": -5}

    rarity= gen_rarity()
    cur.execute(f"SELECT monsterid FROM monsters WHERE rarity = '{rarity}'")
    monster_list = cur.fetchall()
    conn.commit()

    # If not configured yet then this will essentially give an "iou"
    if len(monster_list) > 0:
        id = random.choice(monster_list)
        monsterid = id[0]
    else:
        monsterid = rarity_names[rarity]

    data = {
        "monsterkey": uuid.uuid5(uuid.NAMESPACE_DNS, content + str(created)),
        "monsterid": monsterid,
        "userid": str(userid).strip(),
        "guildid": str(message.guild.id),
        "dropped_at": message.created_at
    }
    # Construct the SQL query
    query = f"INSERT INTO usermonsters values('{data['monsterkey']}', {int(data['monsterid'])}, '{data['userid']}', '{data['guildid']}', cast('{data['dropped_at']}' as timestamp))"

    cur.execute(query)

    conn.commit()

    cur.execute(f"SELECT monstername from monsters where monsterid = {monsterid}")
    monstername = cur.fetchone()

    conn.close()
    try:
        return(monstername[0])
    except:
        return(f"I.O.U one {rarity}")

def my_monsters(guild, user):
    conn = connect_db(postgres)
    cur = conn.cursor()

    userid = user
    guildid = guild
    query = f"SELECT m.monstername, count(*) FROM usermonsters u \
            JOIN discordusers d ON u.userid = d.userid \
            JOIN monsters m ON u.monsterid = m.monsterid \
            WHERE u.userid = cast({userid} as varchar) and guildid = cast({guildid} as varchar) \
            GROUP BY m.monstername \
            ORDER BY 2 desc"
    cur.execute(query)
    mine = cur.fetchall()

    conn.close()
    return(mine)


def gen_rarity():
    """
    Generating number based on % distribution to decide what type of
    monster pool to randomly choose from.
    """
    model = CustomDistributionModel()
    RARITY = model.generate_sample()

    return(RARITY)
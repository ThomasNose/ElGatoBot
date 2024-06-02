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
    created = message.created_at.replace(tzinfo=None)



    rarity= gen_rarity()
    cur.execute(f"SELECT monsterid FROM monsters WHERE rarity = '{rarity}'")
    monster_list = cur.fetchall()
    conn.commit()

    id = random.choice(monster_list)
    monsterid = id[0]

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
    
    return(monstername[0])

def my_monsters(guild, user):
    conn = connect_db(postgres)
    cur = conn.cursor()

    userid = user
    guildid = guild
    query = f"SELECT m.monstername, count(*), lower(m.rarity), orderid FROM usermonsters u \
            JOIN discordusers d ON u.userid = d.userid \
            JOIN monsters m ON u.monsterid = m.monsterid \
            WHERE u.userid = cast({userid} as varchar) and guildid = cast({guildid} as varchar) \
            GROUP BY m.monstername, m.rarity, orderid\
            ORDER BY orderid desc, 2 desc"
    cur.execute(query)
    mine = cur.fetchall()

    conn.close()
    return(mine)

def my_monsters_nicks(guild, user):
    conn = connect_db(postgres)
    cur = conn.cursor()

    userid = user
    guildid = guild
    query = f"SELECT m.monstername, u.monsternick, lower(m.rarity), str + coalesce(bonus_str,0) as str, pwr + coalesce(bonus_pwr,0) as pwr, evn + coalesce(bonus_evn,0) as evn, orderid FROM usermonsters u \
            JOIN discordusers d ON u.userid = d.userid \
            JOIN monsters m ON u.monsterid = m.monsterid \
            WHERE u.userid = cast({userid} as varchar) and guildid = cast({guildid} as varchar) \
            ORDER BY orderid desc, 2 desc"
    cur.execute(query)
    mine = cur.fetchall()

    conn.close()
    return(mine)

async def monster_combat(interaction, guildid, user, monster_nick):
    conn = connect_db(postgres)
    cur = conn.cursor()
    query = f"SELECT m.monstername, u.monsternick, str + coalesce(bonus_str, 0), pwr + coalesce(bonus_pwr, 0), evn + evn + coalesce(bonus_pwr, 0) \
            from usermonsters u \
            JOIN  discordusers d on u.userid = d.userid \
            JOIN monsters m ON u.monsterid = m.monsterid \
            WHERE u.guildid = '{guildid}' AND u.userid = '{user}' and u.monsternick = '{monster_nick}'\
    "
    cur.execute(query)
    stats = cur.fetchone()
    if stats == None:
        await interaction.response.send_message(content = f"{monster_nick} nickname doesn't exist. See nicknames in parentheses of /collection user list")
        return()
    else:
        return(stats)

async def monster_nick(interaction, old_nick, new_nick):
    """
        Updates monster nickname.
    """
    conn = connect_db(postgres)
    cur = conn.cursor()
    query = f"SELECT userid from usermonsters where monsternick = '{old_nick}' and guildid = '{interaction.guild.id}'"
    cur.execute(query)
    try:
        owner = cur.fetchone()[0]
    except:
        await interaction.response.send_message(content = "Monster nick doesn't exist.")
        return()
    if int(owner) != interaction.user.id:
        await interaction.response.send_message(content = "You don't own this monster.")
        conn.close()
    else:
        try:
            cur.execute(f"update usermonsters set monsternick = '{new_nick}' where monsternick = '{old_nick}' and guildid = '{interaction.guild.id}'")
            conn.commit()
            conn.close()
            await interaction.response.send_message(content = "Nickname updated.")
        except Exception as e:
            await interaction.response.send_message(content = "Exception or nickname not unique.")
            print(e)

def gen_rarity():
    """
    Generating number based on % distribution to decide what type of
    monster pool to randomly choose from.
    """
    model = CustomDistributionModel()
    RARITY = model.generate_sample()

    return(RARITY)
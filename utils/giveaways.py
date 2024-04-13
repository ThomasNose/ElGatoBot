from utils.connect_db import connect_db
import settings

postgres = settings.POSTGRES_LOGIN_DETAILS

def giveaway_create(name, date, guild):
    conn = connect_db(postgres)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO giveaways \
                SELECT '{name}', cast('{date}' as timestamp), '{guild}'")
    conn.commit()
    cur.close()
    return(name, date)

def giveaway_delete(name, guild):
    conn = connect_db(postgres)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM giveaways \
                where giveawayname = '{name}' and guildid = '{guild}'")
    conn.commit()
    cur.execute(f"DELETE FROM giveawayusers \
                where giveawayname = '{name}' and guildid = '{guild}'")
    conn.commit()
    cur.close()
    return(name)

def giveaway_list(guild):
    conn = connect_db(postgres)
    cur = conn.cursor()
    cur.execute(f"select distinct giveawayname, date \
                FROM giveaways where guildid = '{guild}'")
    results = cur.fetchall()
    cur.close()
    return(results)

def giveaway_enter(userid, giveawayname, guild):
    conn = connect_db(postgres)
    cur = conn.cursor()

    # Checks the giveaway entered exists
    cur.execute(f"SELECT giveawayname FROM giveaways \
                WHERE guildid = '{guild}'")
    full_list = cur.fetchall()
    full_list = [item for sublist in full_list for item in sublist]
    if giveawayname not in full_list:
        return("Failed")
    
    # Checks if the user has already entered
    cur.execute(f"SELECT userid FROM giveawayusers \
                WHERE giveawayname = '{giveawayname}' and guildid = '{guild}'")
    full_list = cur.fetchall()
    full_list = [item for sublist in full_list for item in sublist]
    if str(userid) in full_list:
        return("Already entered")

    cur.execute(f"INSERT INTO giveawayusers \
                SELECT '{userid}', '{giveawayname}', '{guild}' \
                ON CONFLICT (userid, giveawayname, guildid) DO NOTHING")
    conn.commit()
    cur.close()
    return()

def giveaway_draw(giveawayname):
    conn = connect_db(postgres)
    cur = conn.cursor()

    query = f"SELECT userid FROM giveawayusers \
            WHERE giveawayname = '{giveawayname}'"
    cur.execute(query)
    giveaway_pool = cur.fetchall()
    full_list = [item for sublist in giveaway_pool for item in sublist]
    return(full_list)
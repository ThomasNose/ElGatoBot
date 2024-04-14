import settings
import uuid
from utils.connect_db import connect_db
from datetime import datetime

postgres = settings.POSTGRES_LOGIN_DETAILS

def message_money_gain(points, message):
    conn = connect_db(postgres)
    cur = conn.cursor()

    # uuidv5 unique per user
    balanceid = uuid.uuid5(uuid.NAMESPACE_DNS, str(message.author.id) + "balance")

    # Checking when the latest meseage was sent to include a 5 second message cooldown
    cur.execute(f"SELECT latest_message FROM user_balance \
                WHERE userid = '{message.author.id}' and guildid = '{message.guild.id}' and currencyid = 1")
    try:
        previous = cur.fetchone()[0]
        current = message.created_at.replace(tzinfo=None)
        if abs((previous - current).total_seconds()) < 5:
            return()
    except:
        previous = 0

    cur.execute(f"INSERT INTO user_balance (balanceid, userid, guildid, currencyid, amount, latest_message) \
                VALUES ('{balanceid}', '{message.author.id}', '{message.guild.id}', 1, {points}, now()) \
                ON CONFLICT (balanceid) DO UPDATE \
                SET amount = user_balance.amount + EXCLUDED.amount, latest_message = cast('{message.created_at}' as timestamp)")
    conn.commit()
    conn.close()
    return()


def user_balance(message):
    conn = connect_db(postgres)
    cur = conn.cursor()
    cur.execute(f"SELECT b.amount, c.currencyname FROM user_balance b \
                JOIN currencies c on b.currencyid = c.currencyid \
                WHERE b.userid = '{message.user.id}' and b.guildid = '{message.guild.id}' and c.currencyid = 1")
    results = cur.fetchall()
    conn.close()
    return(results)
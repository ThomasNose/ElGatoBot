import settings
import uuid
from utils.connect_db import connect_db

postgres = settings.POSTGRES_LOGIN_DETAILS

def message_money_gain(points, message):
    conn = connect_db(postgres)
    cur = conn.cursor()

    balanceid = uuid.uuid5(uuid.NAMESPACE_DNS, str(message.author.id) + "balance")

    cur.execute(f"INSERT INTO user_balance (balanceid, userid, guildid, currencyid, amount) \
                VALUES ('{balanceid}', '{message.author.id}', '{message.guild.id}', 1, {points}) \
                ON CONFLICT (balanceid) DO UPDATE \
                SET amount = user_balance.amount + EXCLUDED.amount")
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
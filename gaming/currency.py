import settings
import uuid
from utils.connect_db import connect_db
from datetime import datetime

postgres = settings.POSTGRES_LOGIN_DETAILS

def message_money_gain(points, message):
    conn = connect_db(postgres)
    cur = conn.cursor()

    points = 0.1
    # uuidv5 unique per user
    balanceid = uuid.uuid5(uuid.NAMESPACE_DNS, str(message.author.id) + str(message.guild.id) + "balance")

    # Checking when the latest meseage was sent to include a 5 second message cooldown
    cur.execute(f"SELECT latest_message FROM user_balance \
                WHERE userid = '{message.author.id}' and guildid = '{message.guild.id}' and currencyid = 1")
    try:
        previous = cur.fetchone()[0]
        current = message.created_at.replace(tzinfo=None)
        if abs((previous - current).total_seconds()) < 30:
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

async def pay_user(interaction, member, payment):
    conn = connect_db(postgres)
    cur = conn.cursor()
    cur.execute(f"SELECT amount FROM user_balance \
            WHERE userid = '{interaction.user.id}' AND guildid = '{interaction.guild.id}'")
    # Rounding to 4 DP due to some floats being off by some amount e.g. 4.9999999999999964
    suff = round(float(cur.fetchone()[0]),4)
    if payment > suff:
        return(await interaction.response.send_message(f"You don't have the funds for that big man."))
    
    # Do the exchanger in a single query so there's no chance of duplication
    query = f"UPDATE user_balance \
            SET amount = amount + {payment} \
            WHERE userid = '{member.id}' AND guildid = '{interaction.guild.id}'; \
            UPDATE user_balance \
            SET amount = amount - {payment} \
            WHERE userid = '{interaction.user.id}' AND guildid = '{interaction.guild.id}'"
    cur.execute(query)
    conn.commit()
    conn.close()
    return(await interaction.response.send_message(f"<@{interaction.user.id}> paid <@{member.id}> {payment} coins."))
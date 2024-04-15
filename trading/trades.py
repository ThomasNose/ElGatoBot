import discord
import settings
from utils.connect_db import connect_db


async def trade_monsters(interaction, member, myitem, theiritem):
    conn = connect_db(settings.POSTGRES_LOGIN_DETAILS)
    cur = conn.cursor()

    # Check if trader already has a trade request
    checking.ongoing(cur, interaction)

    # Returning list of monsters to check valid names
    checking.valid(cur, interaction, myitem, theiritem)
    
    # Checking both users have available monsters/items
    checking.available(cur, interaction, member, myitem, theiritem)
    
    # Now we have confirmed the monsters are valid and both have at least one monster each, we can trade.
    embed = discord.Embed(title="Trade", description=f"<@{interaction.user.id}> is trading {myitem} for <@{member.id}>'s {theiritem}. \
                          Type /accept <@{interaction.user.id}> or /decline <@{interaction.user.id}>.")
    
    # We want to insert a record first as the database is the truth not discord.
    cur.execute(f"INSERT INTO monster_trades \
                SELECT '{interaction.user.id}', '{member.id}', '{myitem}', '{theiritem}', now()")
    conn.commit()
    conn.close()

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    #await msg.add_reaction("✅")
    #await msg.add_reaction("❌")


#async def trade_accept(interaction, member):
#    conn = connect_db(settings.POSTGRES_LOGIN_DETAILS)
#    cur = conn.cursor()
#    cur.execute(f"SELECT trader_user, recipient_user, trader_item, recipient_item FROM monster_trades \
#                WHERE trader_user = '{member.id}' and recipient_user = '{interaction.user.id}'")
#    results = cur.fetchone()
#    if results[0] == member.id and results[1] == interaction.user.id:
#        query = f"update user_monsters \
#                SET monster_id = {} \
#                    "


class checking():
    """
        This class is for ensuring;
        1) Multiple trades from a single user aren't ongoing.
        2) The monster names exist.
        3) Both users have the available monster to trade.
    """
    async def ongoing(cursor, interaction):
        cur = cursor
        cur.execute(f"SELECT trader from monster_trades \
                WHERE trader = '{interaction.user.id}'")
        if cur.fetchone() != None:
            return(await interaction.response.send_message("You already have a trade open, type /cancel to cancel it."))


    async def valid(cursor, interaction, myitem, theiritem):
        cur = cursor
        cur.execute("SELECT monstername FROM monsters")
        monsters = cur.fetchall()
        check = [myitem, theiritem]
        if not all(any(value in t for t in monsters) for value in check):
            return(await interaction.response.send_message("Monster name mismatch."))


    async def available(cursor, interaction, member, myitem, theiritem):
        cur = cursor
        cur.execute(f"SELECT monsterkey, monstername FROM usermonsters u \
                    JOIN monsters m on u.monsterid = m.monsterid \
                    WHERE userid = '{interaction.user.id}' and guildid = '{interaction.guild.id}' and monstername = '{myitem}'\
                    LIMIT 1")
        trader = cur.fetchone()
        cur.execute(f"SELECT monsterkey, monstername FROM usermonsters u \
                    JOIN monsters m on u.monsterid = m.monsterid \
                    WHERE userid = '{member.id}' and guildid = '{interaction.guild.id}' and monstername = '{theiritem}'\
                    LIMIT 1")
        recipient = cur.fetchone()
        if trader[1] != myitem:
            return(await interaction.response.send_message(f"You don't own a {myitem}."))
        elif  recipient[1] != theiritem:
            return(await interaction.response.send_message(f"They don't own a {theiritem}."))
            
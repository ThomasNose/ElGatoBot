import discord
import settings
from utils.connect_db import connect_db


async def trade_monsters(interaction, member, myitem, theiritem):
    if interaction.user.id == member.id:
        return(await interaction.response.send_message("You can't trade with yourself."))
    conn = connect_db(settings.POSTGRES_LOGIN_DETAILS)
    cur = conn.cursor()

    # Check if trader already has a trade request
    ongoing = await checking.ongoing(cur, interaction)
    if ongoing == True:
        conn.close()
        return(await interaction.response.send_message("You already have a trade open, type /cancel to cancel it."))

    # Returning list of monsters to check valid names
    #valid = await checking.valid(myitem, theiritem)
    #if valid == False:
    #    conn.close()
    #    return(await interaction.response.send_message("Monster name mismatch."))
    
    # Checking both users have available monsters/items
    available = await checking.available(cur, interaction, member, myitem, theiritem)
    if available[0] == "Trader no item":
        conn.close()
        return(await interaction.response.send_message(f"You don't own a {myitem}."))
    elif available[0] == "Recipient no item":
        conn.close()
        return(await interaction.response.send_message(f"They don't own a {theiritem}."))
    elif available[0] == "Invalid":
        conn.close()
        return(await interaction.response.send_message(f"One or both nicknames don't exist."))
    
    # Now we have confirmed the monsters are valid and both have at least one monster each, we can trade.
    embed = discord.Embed(title="Trade", description=f"<@{interaction.user.id}> is trading {myitem} for <@{member.id}>'s {theiritem}. \
                          Type /accept <@{interaction.user.id}> or /decline <@{interaction.user.id}>.")
    
    # We want to insert a record first as the database is the truth not discord.
    cur.execute(f"INSERT INTO monster_trades \
                SELECT '{interaction.user.id}', '{member.id}', '{myitem}', '{theiritem}', now(), '{interaction.guild.id}'")
    conn.commit()
    conn.close()

    await interaction.response.send_message(embed=embed)
    #msg = await interaction.original_response()
    #await msg.add_reaction("✅")
    #await msg.add_reaction("❌")


async def trade_accept(interaction, member):
    conn = connect_db(settings.POSTGRES_LOGIN_DETAILS)
    cur = conn.cursor()
    # Get the trade information
    cur.execute(f"SELECT trader, recipient, trader_item, recipient_item FROM monster_trades mt \
                WHERE trader = '{member.id}' and recipient = '{interaction.user.id}' and guildid = '{interaction.guild.id}'")
    results = cur.fetchone()

    # No trade currently.
    if results == None:
        return(await interaction.response.send_message("You have no incoming trades."))
    #
    elif results[0] == str(member.id) and results[1] == str(interaction.user.id):

        # keys[0] is their monsterkey and keys[1] is your monsterkey
        keys = await checking.available(cur, interaction, member, results[3], results[2])
        if keys[0] == "Invalid":
            return(await interaction.response.send_message(f"Trade no longer valid, please decline <@{member.id}>'s trade or they can cancel it."))

        # Update userid related to a monsterkey i.e. trade the keys 
        cur.execute(f"UPDATE usermonsters \
                SET userid = '{interaction.user.id}' \
                WHERE monsterkey = '{keys[1]}'; \
                UPDATE usermonsters \
                SET userid = '{member.id}' \
                WHERE monsterkey = '{keys[0]}'")
        conn.commit()
        
        # Inserting trade information into history table
        cur.execute(f"INSERT INTO monster_trades_history \
                    SELECT mt.trader, mt.recipient, mt.trader_item, mt.recipient_item, mt.created_at, mt.guildid, now() \
                    FROM monster_trades mt\
                    WHERE mt.recipient = '{interaction.user.id}' and mt.trader = '{member.id}'")
        conn.commit()

        # Delete trade from active trades
        cur.execute(f"delete from monster_trades \
                    WHERE trader = '{member.id}'")
        conn.commit()
        conn.close()
        return(await interaction.response.send_message(f"You have accepted <@{member.id}>'s trade"))
    else:
        return(await interaction.response.send_message("You have no incoming trades."))
    
async def trade_cancel(interaction, traderid):
    conn = connect_db(settings.POSTGRES_LOGIN_DETAILS)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM monster_trades \
                WHERE trader = '{traderid}' and '{interaction.user.id}' in (trader, recipient)")
    conn.commit()
    conn.close()
    return(await interaction.response.send_message("You've cancelled your trade(s)."))

async def monster_give(interaction, member, monsternick):
    """
        Gives users one of your monsters if it exists and you have at least one.
    """
    if interaction.user.id == member.id:
        return(await interaction.response.send_message("You can't trade with yourself."))
    conn = connect_db(settings.POSTGRES_LOGIN_DETAILS)
    cur = conn.cursor()

    stocked = await checking.available_give(cur, interaction, monsternick)
    if stocked == False:
        return(await interaction.response.send_message(f"You don't have {monsternick}."))
    else:
        cur.execute(f"UPDATE usermonsters \
                    SET userid = '{member.id}' \
                    WHERE monsterkey = '{stocked[0]}'")
        conn.commit()
        conn.close()
        return(await interaction.response.send_message(f"You gave <@{member.id}> your {monsternick}."))


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
                WHERE trader = '{interaction.user.id}' and guildid = '{interaction.guild.id}'")
        if cur.fetchone() != None:
            return(True)
        else:
            return(False)


    #async def valid(myitem, theiritem):
    #    with open("gaming/monsters.txt","r") as file:
    #        monsters = [line.strip().split(',')[1] for line in file.readlines()]
    #    check = [myitem, theiritem]
    #    if not all(any(value in t for t in monsters) for value in check):
    #        return(False)


    # Checking if both parties have monster available
    async def available(cursor, interaction, member, myitem, theiritem):
        cur = cursor
        cur.execute(f"SELECT monsterkey, monsternick FROM usermonsters u \
                    JOIN monsters m on u.monsterid = m.monsterid \
                    WHERE userid = '{interaction.user.id}' and guildid = '{interaction.guild.id}' and monsternick = '{myitem}'\
                    ")
        trader = cur.fetchone()
        cur.execute(f"SELECT monsterkey, monsternick FROM usermonsters u \
                    JOIN monsters m on u.monsterid = m.monsterid \
                    WHERE userid = '{member.id}' and guildid = '{interaction.guild.id}' and monsternick = '{theiritem}'\
                    ")
        recipient = cur.fetchone()
        if trader == None or recipient == None:
            return("Invalid", True)
        elif trader[1] != myitem:
            return("Trader no item", True)
        elif  recipient[1] != theiritem:
            return("Recipient no item", True)
        else:
            return(trader[0], recipient[0])
        
    async def available_give(cur, interaction, monsternick):
        cur.execute(f"SELECT monsterkey FROM usermonsters u \
                    WHERE userid = '{interaction.user.id}' and guildid = '{interaction.guild.id}' and m.monsternick = '{monsternick}'\
                    LIMIT 1")
        stock = cur.fetchone()
        if stock == None:
            return(False)
        else:
            return(stock)
        
    def name_to_id(file_path, name):
        with open(file_path, 'r') as file:
            for line in file:
                columns = line.strip().split(',')
                if len(columns) >= 2 and columns[1] == name:
                    return columns[0]
        return None
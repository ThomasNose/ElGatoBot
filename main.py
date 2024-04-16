# External package imports
import discord
import datetime as datetime
import time
import requests
import random

# External package specific imports
from discord.ext import commands
from discord import app_commands


# Unique commands or events for ElGatoBot
import settings
from BotListen.voice import voicelog
from BotListen.users import user_update
from utils.makefile import makedirectory
from utils.clean_logs import clean
from utils.giveaways import giveaway_create, giveaway_delete, giveaway_list, giveaway_enter, giveaway_draw
from commands.flex.flex import flexing, insult
from commands.chatgpt.chatgpt import gpt, imagegpt
from trading.trades import trade_monsters, trade_accept, trade_cancel
from gaming.monsters import monster_drop, my_monsters
from gaming.currency import message_money_gain, user_balance, pay_user

logger = settings.logging.getLogger("bot")
Generating = False
botid = None

def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @bot.event
    async def on_ready():
        global botid
        botid = bot.user.id
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        try:
            synced = await bot.tree.sync()
        except Exception as e:
            print(e)

        for guild in bot.guilds:
            print(f"Guild ID: {guild.id}, Guild Name: {guild.name}")

        # Accessing the command cache
        print("Registered Commands:")   
        for command in bot.commands:
            print(f"Command Name: {command.name}")

    @bot.command(
            help="Help",
            description="Description",
            brief="Brief",
            enable = False
    )
    async def ping(ctx):
        """Ping Pong"""
        await ctx.send("pong")

    @bot.command()
    async def repeat(ctx, *what):
        await ctx.send(" ".join(what))

    @bot.command()
    async def fan(ctx, name: discord.Member = discord.Interaction.user):
        await ctx.send(name.joined_at.strftime("%Y-%m-%d %H:%M:%S"))


    # Logging messages/images in case someone thinks they're a smart arse.
    @bot.listen('on_message')
    async def on_message(message):
        Drop = 25
        Chance = random.randint(1,50)
        # If person rolls DROP and isn't the bot and isn't a specific channel
        if Chance == Drop and str(message.author.id) != str(botid) and str(message.channel) != '1028024995709984889':
            monstername = monster_drop(message)
            channel = message.channel
            await channel.send(f"Congratulations <@{message.author.id}> you got a monster drop, {monstername} during the increased drop rate!")

        msgsize = len(message.content)
        if msgsize > 0 and msgsize <= 500 and str(message.author.id) != str(botid):
            message_money_gain(round(msgsize/250, 2), message)

    
        # Commented out for now as logging messages
        # isn't priority.
        path = "logs/"+f"{str(message.author.id)}"
        makedirectory(path)
        if message.attachments:
            path = "logs/"+f"{str(message.author.id)}"+"/"+"images/"
            makedirectory(path)
            for image in message.attachments:
                await image.save("logs/"+f"{str(message.author.id)}"+"/"+"images/"+f"{image.filename}")
        msg = message
        with open(f"logs/{message.author.id}/data.txt", "a") as n:
            n.write("\n" + str(msg.created_at) + f"({str(msg.channel)})" + " " + str(msg.author) + ": " + msg.content)

    @bot.tree.command(name="monsters_collection")
    @app_commands.describe(member = "discord member's monsters")
    async def collection(interaction: discord.Interaction, member: discord.Member):
        usermonsters = my_monsters(interaction.guild.id,member.id)
        
        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            description=f"------<@{member.id}>'s monster collection------",
            title="Monster collection list"
        )
        for monster, count in usermonsters:
            # Add each monster's information as a field in the embed
            embed.add_field(name=monster, value=f"Count: {count}", inline=True)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="balance", description="Discord member's balance")
    async def balance(interaction: discord.Interaction):
        userbalance = user_balance(interaction)
        
        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            description=f"<@{interaction.user.id}>'s balance",
            title=""
        )
        for value, currency in userbalance:
            # Add each monster's information as a field in the embed
            embed.add_field(name=currency+"s", value=round(value,2), inline=True)
        await interaction.response.send_message(embed=embed)


    # Logging voice duration.
    #@bot.listen('on_voice_state_update')
    #async def Activity(member, before, after):
    #    path = f"/home/thomaspi/ElGatoBot/logs/{member}/"
    #    makedirectory(path)
    #    voicelog(before, after, member, path)      

    @bot.tree.command(name="voice_activity")
    @app_commands.describe(member = "discord member")
    async def voice(interaction: discord.Interaction, member: discord.Member):
        try:
            with open(f"logs/{member}/TotalVoiceTime.txt", "r") as a:
                await interaction.response.send_message(f"<@{member.id}> " + "has been in voice channels for " + str(a.readline()))
        except:
            await interaction.response.send_message(f"<@{member.id}>  " + "has not spent any time in voice channels yet.")
        a.close()


    @bot.tree.command(name="flex")
    @app_commands.describe(member = "discord member")
    async def flex(interaction: discord.Interaction, member: discord.Member):
        #if "1178728073311563847" in [str(role.id) for role in interaction.user.roles]:
        file = discord.File(f"commands/flex/fleximages/{flexing()}")
        insult_str = insult()
        await interaction.response.send_message(file = file, content = f"<@{interaction.user.id}> " + "flexed on " + f"<@{member.id}>. You {insult_str}.")
        #else:
        #    file = discord.File(f"commands/flex/fleximages/noaccess/facepalmlaugh.png")
        #    insult_str = insult()
        #    await interaction.response.send_message(file = file, content = f"Hey everyone, look at this {insult_str}. <@{interaction.user.id}>")


    @bot.tree.command(name="gpt")
    @app_commands.describe(ctx = "This command generates responses using GPT.")
    async def openai(interaction: discord.Interaction, ctx: str):

        if any(role_id in [str(role.id) for role in interaction.user.roles] for role_id in settings.UTILITY):
            reply = gpt(ctx)
            await interaction.response.send_message(content = reply)
        else:
            await interaction.response.send_message(content = f"<@{interaction.user.id}>, you don't have access to the chatgpt command yet. Command available at level 30.")


    @bot.tree.command(name="imagegpt")
    @app_commands.describe(ctx = "This command generates images using GPT.")
    async def imageopenai(interaction: discord.Interaction, ctx: str):
        global Generating
        if Generating == True:
            interaction.response.send_message("Please wait, an image is already generating.")
        else:
            if any(role_id in [str(role.id) for role in interaction.user.roles] for role_id in settings.UTILITY) and Generating != True:
                ETA = int(time.time() + 30)
                await interaction.response.send_message(f"Generating image ETA, other commands won't work: <t:{ETA}:R>")
                images = imagegpt(ctx)
                Generating = True
                print(f"here are the images {images}")

                try:
                    img = requests.get(images)
                    with open("ai_img.png", 'wb') as f:
                        f.write(img.content)
                except Exception as e:
                    print("An error occured with image ai", e)
                    await interaction.response.send_message(e)
                msg = await interaction.followup.send(content=f"Generated: {ctx}",file=discord.File("ai_img.png"))
                Generating = False

            else:
                await interaction.response.send_message(content = f"<@{interaction.user.id}>, you don't have access to the chatgpt command yet.")


    @bot.tree.command(name="cleanlogs")
    #@app_commands.describe("This command cleans the voice activity of duplicates.")
    async def cleanlogs(interaction: discord.Interaction):
        if any(role_id in [str(role.id) for role in interaction.user.roles] for role_id in settings.UTILITY):
            clean()
            msg = await interaction.response.send_message(f"Cleaned voice logs.")
        else:
            msg = await interaction.response.send_message("You don't have access to that command")


    @bot.command()
    async def get_users(interaction: discord.Interaction):
        # Get the guild (server) the command was sent in
        guild = interaction.guild
        # Fetch all members to ensure the cache is populated
        await guild.chunk()
        user_update(guild.members)


    @bot.tree.command(name="create_giveaway")
    @app_commands.describe(ctx = "Creates a giveaway e.g. /create_giveaway skin giveaway 20240501 17:00:00")
    async def create_giveaway(interaction: discord.Interaction, ctx: str, date: str):
        guild = interaction.guild.id
        if any(role_id in [str(role.id) for role in interaction.user.roles] for role_id in settings.GIVEAWAY_CONTROL):
            created,event_date = giveaway_create(str(ctx), str(date), guild)
            await interaction.response.send_message(f"Giveaway {created} for {event_date} created.")
        else:
            await interaction.response.send_message("You don't have access to that command")


    @bot.tree.command(name="delete_giveaway")
    @app_commands.describe(ctx = "Deletes a giveaway e.g. /delete_giveaway skin giveaway")
    async def delete_giveaway(interaction: discord.Interaction, ctx: str):
        guild = interaction.guild.id
        if any(role_id in [str(role.id) for role in interaction.user.roles] for role_id in settings.GIVEAWAY_CONTROL):
            deleted = giveaway_delete(str(ctx), guild)
            await interaction.response.send_message(f"Giveaway {deleted} deleted.")
        else:
            await interaction.response.send_message("You don't have access to that command")


    @bot.tree.command(name="draw_giveaway", description="Draws the giveaways")
    async def draw_giveaway(interaction: discord.Interaction, ctx: str):
        if any(role_id in [str(role.id) for role in interaction.user.roles] for role_id in settings.GIVEAWAY_CONTROL):
            members = giveaway_draw(ctx)
            winner = random.choice(members)
            await interaction.response.send_message(f"<@{winner}> has won the giveaway!")
        else:
            await interaction.response.send_message("You don't have access to that command")


    @bot.tree.command(name="giveaways", description="Lists all giveaways")
    async def giveaways(interaction: discord.Interaction):
        guild = interaction.guild.id
        giveaways_list = giveaway_list(guild)
    
        # Add fields to the embed for each entry in the data
        embed = discord.Embed(
            colour=discord.Colour.dark_teal(),
            title="Giveaways"
        )
        # Concatenate the data for each row into a single string
        formatted_data = "\n".join(f"Name: {name}\nDate: {event_date} \n" for name, event_date in giveaways_list)

        # Add the concatenated data as a single field to the embed
        embed.add_field(name="Giveaway Information", value=formatted_data, inline=False)

        await interaction.response.send_message(embed=embed)


    @bot.tree.command(name="enter_giveaway", description="Enters into giveaways")
    async def enter_giveaway(interaction: discord.Interaction, ctx: str):
        giveaway_data = giveaway_enter(interaction.user.id, ctx, interaction.guild.id)

        if giveaway_data == "Failed":
            await interaction.response.send_message("That giveaway doesn't exist.")
        elif giveaway_data == "Already entered":
            await interaction.response.send_message("You've already entered that giveaway.")
        else:
            await interaction.response.send_message(f"You have entered the **{ctx}** giveaway!")


    @bot.tree.command(name="trade", description="Trade with users. e.g. /trade @user your_item, their_item")
    async def trade(interaction: discord.Interaction, member: discord.Member, myitem: str, theiritem: str):
        await trade_monsters(interaction, member, myitem, theiritem)
        
    @bot.tree.command(name="accept", description="Accept trade from user.")
    async def accept(interaction: discord.Interaction, member: discord.Member):
        await trade_accept(interaction, member)

    @bot.tree.command(name="decline", description="Decline trade from user.")
    async def decline(interaction: discord.Interaction, member: discord.Member):
        # For now the trader can only have 1 trade so essentially need to call the cancel trade func
        await trade_cancel(interaction, member.id)

    @bot.tree.command(name="cancel", description="Cancel your trade.")
    async def cancel(interaction: discord.Interaction):
        await trade_cancel(interaction, interaction.user.id)

    @bot.tree.command(name="pay", description="Pay a user coins.")
    async def pay(interaction: discord.Interaction, member: discord.Member, amount: float):
        await pay_user(interaction, member, amount)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()

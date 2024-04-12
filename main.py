# External package imports
import settings
import discord
import datetime as datetime
import time
import requests
import random

# External package specific imports
from discord import Attachment
from discord.ext import commands
from discord import app_commands
from makefile import makedirectory
from discord.ui import Button
from discord import ButtonStyle


# Unique commands or events for ElGatoBot
from BotListen.voice import voicelog
from commands.flex.flex import flexing, insult
from commands.chatgpt.chatgpt import gpt, imagegpt
from utils.clean_logs import clean
from BotListen.users import user_update
from gaming.monsters import monster_drop, my_monsters


logger = settings.logging.getLogger("bot")
Generating = False

def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

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
        message.author
        Drop = 25
        Chance = random.randint(1,50)
        # If person rolls DROP and isn't the bot and isn't a specific channel
        if Chance == Drop and str(message.author.id) != '1228351716072886375' and str(message.channel) != '1028024995709984889':
            monstername = monster_drop(message)
            channel = message.channel
            await channel.send(f"Congratulations <@{message.author.id}> you got a monster drop, {monstername}!")

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
        # Commented out for now as logging messages i
        # sn't priority.
        #path = "logs/"+f"{str(message.author)}"
        #makedirectory(path)
        #if message.attachments:
        #    path = "logs/"+f"{str(message.author)}"+"/"+"images/"
        #    makedirectory(path)
        #    for image in message.attachments:
        #        await image.save("logs/"+f"{str(message.author)}"+"/"+"images/"+f"{image.filename}")
        #msg = message
        #with open(f"logs/{message.author}/data.txt", "a") as n:
        #    n.write("\n" + str(msg.created_at) + f"({str(msg.channel)})" + " " + str(msg.author) + ": " + msg.content)

    # Logging voice duration.
    #@bot.listen('on_voice_state_update')
    #async def Activity(member, before, after):
    #    path = f"/home/thomaspi/ElGatoBot/logs/{member}/"
    #    makedirectory(path)
    #    voicelog(before, after, member, path)

    @bot.event
    async def on_ready():
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
        if "1178728073311563847" in [str(role.id) for role in interaction.user.roles]:
            file = discord.File(f"commands/flex/fleximages/{flexing()}")
            insult_str = insult()
            await interaction.response.send_message(file = file, content = f"<@{interaction.user.id}> " + "flexed on " + f"<@{member.id}>. You {insult_str}.")
        else:
            file = discord.File(f"commands/flex/fleximages/noaccess/facepalmlaugh.png")
            insult_str = insult()
            await interaction.response.send_message(file = file, content = f"Hey everyone, look at this {insult_str}. <@{interaction.user.id}>")

    @bot.tree.command(name="gpt")
    @app_commands.describe(ctx = "This command generates responses using GPT.")
    async def openai(interaction: discord.Interaction, ctx: str):

        if "1178728073311563847" in [str(role.id) for role in interaction.user.roles] or "1210303897768300644" in [str(role.id) for role in interaction.user.roles] or "1176134580550520842" in [str(role.id) for role in interaction.user.roles]:
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
            if "1176468007384535040" in [str(role.id) for role in interaction.user.roles] or "1209447447076671508" in [str(role.id) for role in interaction.user.roles] or "1220332638334746664" in [str(role.id) for role in interaction.user.roles]:
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
        clean()
        msg = await interaction.response.send_message(f"Cleaned voice logs.")

    @bot.command()
    async def get_users(interaction: discord.Interaction):
        # Get the guild (server) the command was sent in
        guild = interaction.guild
        # Fetch all members to ensure the cache is populated
        await guild.chunk()
        user_update(guild.members)
        

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()

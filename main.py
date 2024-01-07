import settings
import discord
import datetime as datetime
from discord import Attachment
from discord.ext import commands
from discord import app_commands
from makefile import makedirectory
#from timer import voiceactivity
from BotListen.voice import voicelog


logger = settings.logging.getLogger("bot")

def run():
    intents = discord.Intents.default()
    intents.message_content = True

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
        path = "logs/"+f"{str(message.author)}"
        makedirectory(path)
        if message.attachments:
            path = "logs/"+f"{str(message.author)}"+"/"+"images/"
            makedirectory(path)
            for image in message.attachments:
                await image.save("logs/"+f"{str(message.author)}"+"/"+"images/"+f"{image.filename}")
        msg = message
        with open(f"logs/{message.author}/data.txt", "a") as n:
            n.write("\n" + str(msg.created_at) + f"({str(msg.channel)})" + " " + str(msg.author) + ": " + msg.content)

    #@bot.listen('on_message')
    #async def on_message(message):
    #    if "cs" in message.content:
    #        print(message.content)
    #        await message.channel.send("Don't play CS")

    # Logging voice duration.
    @bot.listen('on_voice_state_update')
    async def Activity(member, before, after):
        path = f"/home/thomaspi/ElGatoBot/logs/{member}/"
        makedirectory(path)
        voicelog(before, after, member, path)

    #@tree.command(
    #        name = "voice",
    #        description = "user total time in voice (registers after a voice DC)"
    #)
    #@bot.command()
    #async def voice(ctx, member: str):
    #    try:
    #        with open(f"logs/{member}/TotalVoiceTime.txt", "r") as a:
    #            #await interaction.response.send_message(f"{member} " + "has been in voice channels for " + str(a.read()))
    #            await ctx.send(f"{member} " + "has been in voice channels for " + str(a.readline()))
    #    except:
    #        #await interaction.response.send_message(f"{member} " + "has not spent any time in voice channels yet.")
    #        await ctx.send(f"{member} " + "has not spent any time in voice channels yet.")
    #    a.close()

    @bot.event
    async def on_ready():
        try:
            synced = await bot.tree.sync()
        except Exception as e:
            print(e)
    
    @bot.tree.command(name="voice_activity")
    @app_commands.describe(member = "discord member")
    async def voice(interaction: discord.Interaction, member: discord.Member):
        try:
            with open(f"logs/{member}/TotalVoiceTime.txt", "r") as a:
                await interaction.response.send_message(f"{member} " + "has been in voice channels for " + str(a.readline()))
        except:
            await interaction.response.send_message(f"{member} " + "has not spent any time in voice channels yet.")
        a.close()


    @bot.command()
    async def guild(ctx):
        voice_channels = ctx.guild.voice_channels
        extracted_data = [(channel.id, channel.name) for channel in voice_channels]
        print(extracted_data)
        #await ctx.send(ctx.guild.voice_channels)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
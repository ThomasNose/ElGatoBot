# External package imports
import discord
import datetime as datetime
import time
import requests
import random
import math

# External package specific imports
from discord.ext import commands
from discord import app_commands
from datetime import timezone

# Unique commands or events for ElGatoBot
import settings
from BotListen.voice import voicelog
from BotListen.users import user_update
from BotListen.music import audio
from utils.makefile import makedirectory
from utils.clean_logs import clean
from utils.giveaways import giveaway_create, giveaway_delete, giveaway_list, giveaway_enter, giveaway_draw
from commands.flex.flex import flexing, insult
from commands.chatgpt.chatgpt import gpt, imagegpt
from commands.suggestions.suggestions import suggest
from trading.trades import trade_monsters, trade_accept, trade_cancel, monster_give
from gaming.monsters import monster_drop, my_monsters
from gaming.currency import message_money_gain, user_balance, pay_user


logger = settings.logging.getLogger("bot")


class PaginationView(discord.ui.View):
    """
        This class is responsible for creating embeds for listing a user's collection.
        For now this is orientated at a monster collection but different functions
        can be created later on when needed.
    """
    current_page : int = 1
    sep : int = 6
    async def send(self, interaction):
        await interaction.response.send_message(view=self)
        self.message = await interaction.original_response()
        await self.update_message(self.data[:self.sep], self.user)
        

    def create_embed(self, data, user):
        embed = discord.Embed(title = f"Page {self.current_page} of Collection", \
                              description=f"<@{user}>'s monsters")
        for monster, count, rarity, orderid in data:
            embed.add_field(name=f"{monster} ({rarity})", value=f"Count: {count}", inline=True)
        return(embed)
    
    async def update_message(self, data, user):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data, user), view = self)
    

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.previous_button.disabled = True
        else:
            self.first_page_button.disabled = False
            self.previous_button.disabled = False
        if self.current_page ==  math.ceil(len(self.data) / self.sep):
            self.next_button.disabled = True
            self.last_page_button.disabled = True
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False

    
    @discord.ui.button(label="First", style = discord.ButtonStyle.primary)
    async def first_page_button(self, interaction:discord.Interaction, button: discord.ui.Button,):
        await interaction.response.defer()
        self.current_page = 1
        until_item = self.current_page * self.sep
        await self.update_message(self.data[:until_item], self.user)

    @discord.ui.button(label="Next", style = discord.ButtonStyle.primary)
    async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item], self.user)

    @discord.ui.button(label="Previous", style = discord.ButtonStyle.primary)
    async def previous_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item], self.user)

    @discord.ui.button(label="Last",
                       style = discord.ButtonStyle.primary)
    async def last_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page =  math.ceil(len(self.data) / self.sep)
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:], self.user)


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
        Drop = 50
        Chance = random.randint(1,100)

        # Reading from local file. This is replacing a DB connection which is awful per message.
        with open("gaming/latest_drop.txt","r") as file:
            thing = file.readline().split("=")[1]
            latest = datetime.datetime.strptime(thing, "%Y-%m-%d %H:%M:%S")
            latest = abs((message.created_at.replace(tzinfo=None) - latest).total_seconds())
            file.close()

        # If person rolls DROP and isn't the bot and isn't a specific channel
        if Chance == Drop and str(message.author.id) != str(botid) and str(message.channel) != '1028024995709984889' and latest > 60:
            monstername = monster_drop(message)
            channel = message.channel
            if monstername != None:
                try:
                    file = discord.File(f"gaming/monsters/{monstername.lower()}"+"-image.png")
                except:
                    file = None
                    print(f"No image of {monstername} exists yet.")

                await channel.send(file=file, content = f"<@{message.author.id}>, you got a monster drop, {monstername}.")

                # Updates latest drop time.
                with open("gaming/latest_drop.txt","w") as file:
                    file.write(f"Latest={datetime.datetime.strptime(str(message.created_at.replace(tzinfo=None).replace(microsecond=0)), '%Y-%m-%d %H:%M:%S')}")
                    file.close()

        message_money_gain(message)

    
        # Logs user messages - not sure if this retains upon the creation of each new docker image - doesn't really matter.
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


    @bot.tree.command(name="collection")
    @app_commands.describe(member = "discord member's monsters")
    async def collection(interaction: discord.Interaction, member: discord.Member):
        usermonsters = my_monsters(interaction.guild.id,member.id)

        pagination_view = PaginationView()
        pagination_view.data = usermonsters
        pagination_view.user = member.id
        await pagination_view.send(interaction)



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
        file = discord.File(f"commands/flex/fleximages/{flexing()}")
        insult_str = insult()
        await interaction.response.send_message(file = file, content = f"<@{interaction.user.id}> " + "flexed on " + f"<@{member.id}>. You {insult_str}.")


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
    
    @bot.tree.command(name="give", description="Give a monster for nothing in return.")
    async def give(interaction: discord.Interaction, member: discord.Member, monstername: str):
        await monster_give(interaction, member, monstername)

    @bot.tree.command(name="pay", description="Pay a user coins.")
    async def pay(interaction: discord.Interaction, member: discord.Member, amount: float):
        await pay_user(interaction, member, amount)


    @bot.tree.command(name="suggestion", description="Make a bot suggestion, 500 characters max or will be truncated.")
    async def suggestion(interaction: discord.Interaction, ctx: str):
        await suggest(interaction, ctx)


    @bot.tree.command(name="play", description="Play audio via a youtube link")
    async def play(interaction: discord.Interaction, url: str):
        if interaction.user.voice == None:
            await interaction.response.send_message(content = "You must be in a voice channel.")
            return()
        #elif interaction.user.voice.channel.id != interaction.guild.voice_client
        elif url.startswith("https://www.youtube.com/") and interaction.user.voice != None:
            await audio().play_audio(interaction, url)
        else:
            await interaction.response.send_message(content = "URL not supported, please use a youtube link.")


    @bot.tree.command(name="pause", description="Pause audio.")
    async def pause(interaction: discord.Interaction):
        voice_state = interaction.guild.voice_client
        if interaction.user.voice.channel.id != voice_state.channel.id:
            return(await interaction.response.send_message("Bot not in your voice chat."))
        await audio.pause_audio(interaction)


    @bot.tree.command(name="resume", description="Resume audio.")
    async def resume(interaction: discord.Interaction):
        voice_state = interaction.guild.voice_client
        if interaction.user.voice.channel.id != voice_state.channel.id:
            return(await interaction.response.send_message("Bot not in your voice chat."))
        await audio.resume_audio(interaction)


    @bot.tree.command(name="stop", description="Stops audio.")
    async def stop(interaction: discord.Interaction):
        voice_state = interaction.guild.voice_client
        if interaction.user.voice.channel.id != voice_state.channel.id:
            return(await interaction.response.send_message("Bot not in your voice chat."))
        await audio.audio_disconnect(interaction)
    

    @bot.tree.command(name="skip", description="Skips audio.")
    async def skip(interaction: discord.Interaction):
        voice_state = interaction.guild.voice_client
        if interaction.user.voice.channel.id != voice_state.channel.id:
            return(await interaction.response.send_message("Bot not in your voice chat."))
        await audio().audio_skip(interaction)
            
        
    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()

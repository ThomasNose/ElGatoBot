import discord
import math
import random

class PaginationView(discord.ui.View):
    """
        This class is responsible for creating embeds for listing a user's collection.
        For now this is orientated at a monster collection but different functions
        can be created later on when needed.
    """
    def __init__(self, sep=1):
        super().__init__()
        self.current_page = 1
        self.sep = sep

    async def send(self, interaction):
        await interaction.response.send_message(view=self)
        self.message = await interaction.original_response()
        await self.update_message(self.data[:self.sep], self.user)
        

    def create_embed(self, data, user):
        embed = discord.Embed(title = f"Page {self.current_page} of Collection", \
                              description=f"<@{user}>'s monsters")
        if len(data[0]) == 4:
            for monster, count, rarity, orderid in data:
                embed.add_field(name=f"{monster} ({'TBC'}) ({rarity})", value=f"Count: {count}", inline=True)
                if self.sep == 1:
                    try:
                        embed.set_image(url=f"https://raw.githubusercontent.com/ThomasNose/ElGatoBot/main/gaming/monsters/monster_derivatives/{monster.lower()}/{monster.lower()}-image-64_x_64.png")
                    except Exception as e:
                        print(e)
        elif len(data[0]) == 7:
            for monster, monsternick, rarity, str, pwr, evn, orderid in data:
                embed.add_field(name=f"{monster} ({monsternick}) ({rarity})", value=f"STR: {str}, PWR: {pwr} EVN: {evn}", inline=True)
                if self.sep == 1:
                    try:
                        embed.set_image(url=f"https://raw.githubusercontent.com/ThomasNose/ElGatoBot/main/gaming/monsters/monster_derivatives/{monster.lower()}/{monster.lower()}-image-64_x_64.png")
                    except Exception as e:
                        print(e)
        return(embed)
    
    async def update_message(self, data, user):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data, user), view = self)
    

    def update_buttons(self):
        max_page = math.ceil(len(self.data) / self.sep)
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.previous_button.disabled = True
        else:
            self.first_page_button.disabled = False
            self.previous_button.disabled = False

        if self.current_page == max_page:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False

        if self.current_page >= max_page - 4 or self.sep != 1:
            self.plus5.disabled = True
        else:
            self.plus5.disabled = False

        if self.current_page <= 5 or self.sep != 1:
            self.minus5.disabled = True
        else:
            self.minus5.disabled = False


    
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

    @discord.ui.button(label="+5", style = discord.ButtonStyle.primary)
    async def plus5(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 5
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item], self.user)

    @discord.ui.button(label="-5", style = discord.ButtonStyle.primary)
    async def minus5(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 5
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        await self.update_message(self.data[from_item:until_item], self.user)


class FightingView(discord.ui.View):
    """
        This class is responsible for creating embeds for combat between two users.

        User monsters will have stats (upgradable up to 10 times across all stats) to allow some
        variation/strategy. The stats will be;

        >> Strength (STR) - health
        >> Power (PWR) - additional modier to rolls
        >> Evasion (EVN) - chance to dodge an attack.

        This class needs to ensure only the interacting and rival user can interact with the
        buttons at the appropriate times. The view will;

        >> Send a request to the user.
        >> Initiate combat based on a coin flip.
        >> Roll a "10 sided dice" (randint) and apply modifiers based on monster type.
        >> Provide user turns.
        >> Declare a winner.
    """
    def __init__(self, STR1 = 50, PWR1 = 5, EVN1 = 5, STR2 = 5, PWR2 = 5, EVN2 = 5, challenger = None, opponent = None):
        super().__init__()
        self.current_turn = 1
        self.challenger = challenger
        self.opponent = opponent
        self.curr_user = random.choice([challenger,opponent])
        
        self.STR1 = STR1
        self.STR2 = STR2
        self.PWR1 = PWR1
        self.PWR2 = PWR2
        self.EVN1 = EVN1
        self.EVN2 = EVN2

        self.HP1 = round(20 * (1.0 + (STR1/10)))

        self.Attack1.disabled = True

    async def send(self, interaction):
        await interaction.response.send_message(view=self)
        self.message = await interaction.original_response()
        await self.update_message(self.monster, self.opponent)

    
    async def update_message(self, monster, opponent):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(monster, opponent), view = self)


    def create_embed(self, monster, opponent):
        embed = discord.Embed(title = f"Turn {self.current_turn}", \
                              description=f"<@{self.curr_user}>'s monster")
        if self.HP1 <= 1:
            embed.add_field(name=f"{monster}", value=f"Fainted.", inline=True)
        else:
            embed.add_field(name=f"{monster} HP: {self.HP1}", value=f"STR:{self.STR1}, PWR:{self.PWR1}, EVN:{self.EVN1}", inline=True)
        return(embed)


    def update_buttons(self):
        if self.HP1 <= 0 or self.Accept.disabled == False:
            self.Attack1.disabled = True
        else:
            self.Attack1.disabled = False


    @discord.ui.button(label="Attack1", style = discord.ButtonStyle.primary)
    async def Attack1(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_turn += 1
        self.HP1 -= random.randint(1,6+self.PWR1)

        if self.curr_user == self.challenger:
            self.curr_user = self.opponent
        else:
            self.curr_user = self.challenger

        await self.update_message(self.monster, self.opponent)

    @discord.ui.button(label="Accept", style = discord.ButtonStyle.primary)
    async def Accept(self, interaction:discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.opponent:
            await interaction.response.defer()
            self.Accept.disabled = True
            self.update_buttons()
            await interaction.message.edit(embed=self.create_embed(self.monster, self.opponent), view = self)
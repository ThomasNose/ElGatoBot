import discord
import math
import random

from gaming.currency import balance_both, combat_pay, user_balance
from gaming.monsters import stat_upgrade, monster_combat

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
    def __init__(self, STR1 = 5, PWR1 = 5, EVN1 = 5, STR2 = 5, PWR2 = 5, EVN2 = 5, challenger = None, opponent = None, amount = 0.00):
        super().__init__()
        self.winner = None
        self.amount = amount

        self.current_turn = 1
        self.challenger = challenger
        self.opponent = opponent
        
        
        self.STR1 = STR1
        self.STR2 = STR2
        self.PWR1 = PWR1
        self.PWR2 = PWR2
        self.EVN1 = EVN1
        self.EVN2 = EVN2

        self.HP1 = round(20 * (1.0 + (STR1/10)))
        self.HP2 = round(20 * (1.0 + (STR2/10)))

        self.Attack1.disabled = True

        # Current turn display metrics
        self.curr_user = random.choice([challenger,opponent])
        self.user = None
        self.curr_monster = None
        self.curr_hp = None
        self.curr_str = None
        self.curr_pwr = None
        self.curr_evn = None

    async def send(self, interaction):
        if self.curr_user == self.challenger:
            self.user = self.chal
            self.curr_monster = self.chal_monster
            self.curr_hp = self.HP1
            self.curr_str = self.STR1
            self.curr_pwr = self.PWR1
            self.curr_evn = self.EVN1
        else:
            self.curr_monster = self.opp_monster
            self.user = self.opp
            self.curr_hp = self.HP2
            self.curr_str = self.STR1
            self.curr_pwr = self.PWR1
            self.curr_evn = self.EVN2

        await interaction.response.send_message(view=self)
        self.message = await interaction.original_response()
        await self.update_message(self.curr_monster, self.opponent, None)

    
    async def update_message(self, curr_monster, opponent, dmg):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(curr_monster, opponent, dmg), view = self)


    def create_embed(self, monster, opponent, dmg):
        embed = discord.Embed(title = f"{self.user}'s turn.", \
                              description=f"Combat for {self.amount} - winnings **{self.amount *2}**.")
        
        if dmg != None:
            embed = discord.Embed(title = f"{self.user}'s turn.", \
                              description=f"{self.curr_monster} took {dmg} damage.")

        if self.HP1 <= 1 or self.HP2 <= 1:
            embed = discord.Embed(title = f"**{self.user}'s loss.**", \
                                  description= f"<@{self.winner}> won **{self.amount *2}** coins.")
            embed.add_field(name=f"{monster}", value=f"Fainted.", inline=True)

        else:
            embed.add_field(name=f"{self.chal_monster} HP: {self.HP1}", value=f"STR:{self.STR1}, PWR:{self.PWR1}, EVN:{self.EVN1}", inline=True)
            embed.add_field(name=f"{self.opp_monster} HP: {self.HP2}", value=f"STR:{self.STR2}, PWR:{self.PWR2}, EVN:{self.EVN2}", inline=True)
        return(embed)


    def update_buttons(self):
        if self.HP1 <= 0 or self.HP2 <= 0 or self.Accept.disabled == False:
            self.Attack1.disabled = True
        else:
            self.Attack1.disabled = False


    @discord.ui.button(label="Attack1", style = discord.ButtonStyle.primary)
    async def Attack1(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user.id == self.curr_user:
            self.current_turn += 1

            if self.curr_user == self.challenger:
                dmg = random.randint(1,6+self.PWR1)
                self.HP2 -= dmg
                if self.HP2 <= 0:
                    self.winner = self.challenger
                    self.user = self.opp
                    self.curr_monster = self.opp_monster
                    await combat_pay(self.winner, interaction.guild.id, 1, self.amount * 2)
                else:
                    self.curr_user = self.opponent
                    self.user = self.opp
                    self.curr_monster = self.opp_monster
                    self.curr_hp = self.HP2
                    self.curr_str = self.STR2
                    self.curr_pwr = self.PWR2
                    self.curr_evn = self.EVN2
            else:
                dmg = random.randint(1,6+self.PWR2)
                self.HP1 -= dmg
                if self.HP1 <= 0:
                    self.winner = self.opponent
                    self.user = self.chal
                    self.curr_monster = self.chal_monster
                    await combat_pay(self.winner, interaction.guild.id, 1, self.amount * 2)
                else:
                    self.curr_user = self.challenger
                    self.user = self.chal
                    self.curr_monster = self.chal_monster
                    self.curr_hp = self.HP1
                    self.curr_str = self.STR1
                    self.curr_pwr = self.PWR1
                    self.curr_evn = self.EVN1

            await self.update_message(self.curr_monster, self.opponent, dmg)

    @discord.ui.button(label="Accept", style = discord.ButtonStyle.primary)
    async def Accept(self, interaction:discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.opponent:
            await interaction.response.defer()
            self.Accept.disabled = True
            self.update_buttons()

            bal_both = await balance_both(self.challenger, self.opponent, interaction.guild.id, self.amount)
            if bal_both == False:
                await interaction.response.send_message(content = "Users don't have sufficient balance.")
                return()
            if self.amount < 0.0:
                await interaction.response.send_message(content = "Wager amount must be positive")
                return()
            
            await interaction.message.edit(embed=self.create_embed(self.curr_monster, self.opponent, None), view = self)


class UpgradeMonster(discord.ui.View):
    def __init__(self, monster_nick, user):
        super().__init__()
        self.nick = monster_nick
        self.user = user
        self.bal = None

    async def send(self, interaction):
        await interaction.response.send_message(view=self)
        self.message = await interaction.original_response()
        stats = await monster_combat(interaction, interaction.guild.id, interaction.user.id, self.nick)
        #self.bal = self.user_bal(interaction)
        self.bal = round(user_balance(interaction.user.id, interaction.guild.id)[0][0],4)
        await self.update_message(stats)

    async def update_message(self, stats):
        self.update_buttons(stats[5])
        bal = self.bal
        await self.message.edit(embed=self.create_embed(self.nick, stats[0], stats[2], stats[3], stats[4], stats[5]), view = self)


    def create_embed(self, nick, monster, str, pwr, evn, bonus):
        embed = discord.Embed(title = f"Upgrade menu for {self.username}'s \n{monster}, {nick}.", \
                              description = f"Stat cost: {(11-bonus) * 5} - Balance: {self.bal} - bonus left: {bonus}")
        embed.add_field(name = "Strength", value = f"{str}", inline=True)
        embed.add_field(name = "Power", value = f"{pwr}", inline=True)
        embed.add_field(name = "Evasion", value = f"{evn}", inline=True)
        return(embed)
    

    def update_buttons(self, bonus):
        if bonus <= 0 or self.bal < (11-bonus) * 5:
            self.STR.disabled = True
        else:
            self.STR.disabled = False


    @discord.ui.button(label="STR", style = discord.ButtonStyle.primary)
    async def STR(self, interaction:discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user:
            await interaction.response.defer()
            str_stat = await stat_upgrade(interaction, self.nick, "STR")
            stats = await monster_combat(interaction, interaction.guild.id, interaction.user.id, self.nick)

            # if 0 then no bonus left, if "bal" then no money
            if str_stat == 0 or str_stat == "bal":
                self.update_buttons(0)
            else:
                self.bal = round(user_balance(interaction.user.id, interaction.guild.id)[0][0],4)
                await self.update_message(stats)
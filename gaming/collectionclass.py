import discord
import math

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
        for monster, count, rarity, orderid in data:
            embed.add_field(name=f"{monster} ({rarity})", value=f"Count: {count}", inline=True)
            if self.sep == 1:
                try:
                    print(f"https://raw.githubusercontent.com/ThomasNose/ElGatoBot/main/gaming/monsters/monster_derivatives/{monster.lower()}/{monster.lower()}-image-64_x_64.png")
                    embed.set_image(url=f"https://raw.githubusercontent.com/ThomasNose/ElGatoBot/main/gaming/monsters/monster_derivatives/{monster.lower()}/{monster.lower()}-image-64_x_64.png")
                except Exception as e:
                    print(e)
        return(embed)
    
    async def update_message(self, data, user):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data, user), view = self)
    

    def update_buttons(self):
        max_page = math.ceil(len(self.data) / self.sep)
        print(self.current_page, max_page)
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

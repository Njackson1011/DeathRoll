import random
import discord
import os
from discord.ext import commands
from dotenv import dotenv_values

config = dotenv_values(".env")
token = config['DISCORD_TOKEN']

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class DeathRollView(discord.ui.View):
    def __init__(self, author, target, embed_msg):
        super().__init__()
        self.author = author
        self.target = target
        self.author_accepted = False
        self.target_accepted = False
        self.embed_msg = embed_msg

    async def disable(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        self.disable()


    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author.id:
            self.author_accepted = True
            await interaction.response.defer()
        elif interaction.user.id == self.target.id:
            self.target_accepted = True
            await interaction.response.defer()

        if self.author_accepted and self.target_accepted:
            self.embed_msg.color = discord.Color.green()
            await self.message.edit(embed=self.embed_msg)
            await self.disable()
            self.stop()
        

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_msg.color = discord.Color.red()
        await self.message.edit(content=f"{self.target.mention} declined the Death Roll.", embed=self.embed_msg)
        await self.disable()
        self.stop()


@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
    print("We clown in this motherfucker!")


@bot.command()
async def roll(ctx, *, argument: str = None):
    if argument is None:
        # No argument provided, generate a random number between 1-100
        result = random.randint(1, 100)
        await ctx.send(f"{ctx.author.mention} rolled **{result}**!")

    elif argument.isdigit():
        # Argument is a positive integer, roll a number between 1 and the given number
        number = int(argument)
        if number < 1:
            await ctx.send("Please provide a positive number.")
            return
        result = random.randint(1, number)
        await ctx.send(f"{ctx.author.mention} rolled a **{result}**!")

    elif ctx.message.mentions:
        target = ctx.message.mentions[0]

        if target is None or target == ctx.author:
            await ctx.send("Invalid target. Please mention another user.")
            return

        author = ctx.author
        embed = discord.Embed(
            color=discord.Color.light_gray(),
            title="Death Roll",
            description=(f"{target.mention}, you have been challenged to a **Death Roll** by {author.mention}. Please choose whether or not you accept the Death Roll."),
        )
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/629097640000225290/953672904090992710/1011-10112146_red-dice-png-transparent-images-dado-clipart.png')
        embed.add_field(name="\u200B", value="\u200B", inline=False)
        embed.add_field(name=author.display_name, value="\u200B", inline=True)
        embed.add_field(name="**VS**", value="\u200B", inline=True)
        embed.add_field(name=target.display_name, value="\u200B", inline=True)

        view = DeathRollView(author, target, embed)

        message = await ctx.send(embed=embed, view=view)
        view.message = message

        await view.wait()
        
        if not(view.author_accepted and view.target_accepted):
            return
        
        author_results = []
        target_results = []

        parts = argument.split()

        if len(parts) == 2 and parts[1].isdigit():
            author_result = random.randint(1,int(parts[1]))

        author_result = random.randint(1, 100)
        author_results.append(author_result)

        target_result = random.randint(1, author_result)
        target_results.append(target_result)

        while author_result != 1 and target_result != 1:
            if author_result != 1:
                x = random.randint(1, target_result)
                author_result = x
                author_results.append(author_result)
                if author_result == 1:
                    break

            if target_result != 1:
                x = random.randint(1, author_result)
                target_result = x
                target_results.append(target_result)
                if target_result == 1:
                    break

        result_text = f"A **Death Roll** between {ctx.author.mention} and {target.mention} has begun!\n\n"
        min_length = min(len(author_results), len(target_results))
        for i in range(min_length):
            result_text += f"{ctx.author}: {author_results[i]}\n"
            result_text += f"{target}: {target_results[i]}\n"

        if author_result == 1:
            result_text += f"{ctx.author} lost the Death Roll against {target}!"
        else:
            result_text += f"{target} lost the Death Roll against {ctx.author}!"

        await ctx.send(result_text)


bot.run(token)

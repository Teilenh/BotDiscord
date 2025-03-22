import discord
from random import randint
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class GamesCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command()
  async def roll(self, ctx):
    result = randint(1, 8)
    await ctx.send(f'{ctx.author.name} lance un dé et obtient : {result}')

async def setup(bot):
  await bot.add_cog(GamesCog(bot))
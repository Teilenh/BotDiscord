import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive

load_dotenv()
Token=os.getenv('DISCORD_TOKEN')
if not isinstance(Token, str) or Token.strip() == "":
    raise ValueError("❌ Le token du bot est invalide ou vide !")

class Doc_hudson(commands.Bot):
  async def setup_hook(self):
    for extension in ['games', 'moderation', 'infos','event', 'BeamNGInfo','beamng_mp','BeamCar']:
      await self.load_extension(f'cogs.{extension}')
    print("✅ Cogs chargés avec succès")

  async def on_ready(self):
    print(f"Connecté en tant que {bot.user}")
    try:
      synced = await self.tree.sync()
      print(f"{len(synced)} commande(s) synchronisée(s)")
    except Exception as e:
      print(e)

intents = discord.Intents.all()
bot = Doc_hudson(command_prefix='_', intents=intents)

keep_alive()

bot.run(token=Token)

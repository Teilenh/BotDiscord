import time
import discord
import psutil
import os
from discord.ext import commands
from discord import app_commands
from datetime import datetime



class InformationCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.process = psutil.Process(os.getpid())

        # Initialisation de l'uptime du bot
        self.bot.uptime = datetime.now()

    @app_commands.command(name="ping", description="Pong!")
    async def ping(self, interaction: discord.Interaction):
        """Pong!"""
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        
        # Envoi de la réponse initiale
        msg = await interaction.response.send_message("🏓 Pong")
        
        # Calcul du ping en millisecondes
        ping = (time.monotonic() - before) * 1000
        
        # Édition du message avec les nouvelles informations
        await interaction.edit_original_response(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")


    @app_commands.command(name="invitation", description="obtenez le lien pour inviter vos amis!")
    async def invitation(self, interaction: discord.Interaction):
        """l'invitation pour rejoindre le server!"""
        if isinstance(interaction.channel, discord.DMChannel) or interaction.guild.id != 828656939365957742:
            return await interaction.response.send_message(f"**{interaction.user.name}, voici notre lien d'invitation **\nhttps://discord.gg/gx78tnB3ym")
        await interaction.response.send_message(f"**{interaction.user.name}** tu sais que je sais")

    @app_commands.command(name="à-propos", description="à propos du Bot")
    async def about(self, interaction: discord.Interaction):
        """à propos du Bot"""
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)

        embedColour = None
        if hasattr(interaction, "guild") and interaction.guild is not None:
            embedColour = interaction.guild.me.top_role.colour

        # Calcul du temps écoulé depuis le démarrage du bot
        uptime = self.bot.uptime
        uptime_delta = datetime.now() - uptime
        uptime_string = str(uptime_delta).split(".")[0]  # Formatage simple (HH:MM:SS)
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        ping = (time.monotonic() - before) * 1000
        embed = discord.Embed(
            colour=discord.Color.dark_blue(),
            title="BeamNG France - Systéme d'automatisation",
            )
        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.add_field(name="UPTIME", value=f"{uptime_string} ", inline=False)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=False)
        embed.add_field(name="PING", value=f"ws :{ping}ms, rest :{before_ws}ms")
        embed.set_footer(text="Version 0.3")

        await interaction.response.send_message(content= "",embed=embed)


async def setup(bot):
    await bot.add_cog(InformationCog(bot))



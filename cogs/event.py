import discord
import psutil
import os
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import errors

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err: Exception):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send("\n".join([
                    "Vous avez tenté d'afficher plus de 2 000 caractères...",
                    "La commande et l'erreur seront ignorées."
                ]))

            await ctx.send(f"Une erreur est survenue lors du traitement de la commande ;-;\n{error}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("Vous avez atteint la capacité maximale d'utilisation des commandes en même temps, veuillez terminer la précédente...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"Cette commande est en cooldown... essayez à nouveau dans {err.retry_after:.2f} secondes.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        to_send = next((
            chan for chan in guild.text_channels
            if chan.permissions_for(guild.me).send_messages
        ), None)

        if to_send:
            await to_send.send(self.bot.config.discord_join_message)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        location_name = ctx.guild.name if ctx.guild else "Message privé"
        print(f"{location_name} > {ctx.author} > {ctx.message.clean_content}")


async def setup(bot):
    await bot.add_cog(EventsCog(bot))

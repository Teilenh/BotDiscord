import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(
                    f"{argument} n'est pas un ID de membre valide."
                ) from None
        else:
            return m.id


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="message", description="envois mp au membre.")
    # @app_commands.check(lambda ctx: ctx.user.id == 730003416004296754)  # Vérification de l'ID ici
    async def mp(self, ctx, membre: discord.User, *, message: str):
        """ Envoi un message privé au membre indiqué """
        if not ctx.user.guild_permissions.moderate_members:
            await ctx.response.send_message("❌ Vous n'avez pas la permission pour cette commande.", ephemeral=True)
            return
        try:
            await membre.send(message)
            await ctx.response.send_message(f"✉️ Message privé envoyé à **{membre}**")
        except discord.Forbidden:
            await ctx.response.send_message("Cet utilisateur a bloqué le bot ou est lui-même un bot...")


    @app_commands.command()
    async def kick(self, ctx, membre: discord.Member, *, raison: str = None):
        if not ctx.user.guild_permissions.moderate_members:
            await ctx.response.send_message("❌ Vous n'avez pas la permission d'exclure des membres.", ephemeral=True)
            return
        await membre.kick(reason=raison)
        await ctx.send(f'{membre.name} a été exclu(e).')

    # Commande slash /exclure
    @app_commands.command(name="exclure", description="Exclut temporairement un membre pour une durée donnée (max 28 jours).")
    @app_commands.describe(
        membre="Le membre à exclure",
        unité="Unité de temps : semaine, jour, heure, minute",
        durée="Durée selon l'unité choisie",
        raison="Motif de l'exclusion"
    )
    @app_commands.choices(
        unité=[
            app_commands.Choice(name="Semaine", value="semaine"),
            app_commands.Choice(name="Jour", value="jour"),
            app_commands.Choice(name="Heure", value="heure"),
            app_commands.Choice(name="Minute", value="minute")
        ]
    )
    async def exclure(self, ctx, membre: discord.Member, unité: str, durée: int, raison: str = "Aucune raison spécifiée"):
        """Exclut temporairement un membre"""
        
        if not ctx.user.guild_permissions.moderate_members:
            await ctx.response.send_message("❌ Vous n'avez pas la permission d'exclure temporairement des membres.", ephemeral=True)
            return
        
        conversions = {
            "semaine": 7 * 24,
            "jour": 24,
            "heure": 1,
            "minute": 1 / 60
        }
        
        if unité not in conversions:
            await ctx.response.send_message("❌ Unité invalide. Choisissez entre 'Semaine', 'Jour', 'Heure', 'Minute'.", ephemeral=True)
            return
        
        durée_heures = durée * conversions[unité]
        
        if durée_heures <= 0 or durée_heures > 672:
            await ctx.response.send_message("❌ La durée doit être comprise entre 1 minute et 28 jours.", ephemeral=True)
            return
        
        try:
            await membre.timeout(timedelta(hours=durée_heures), reason=raison)
            await ctx.response.send_message(f"✅ {membre.mention} a été exclu temporairement pour {durée} {unité}(s). Raison : {raison}")
        except discord.Forbidden:
            await ctx.response.send_message("❌ Je n'ai pas la permission de timeout ce membre.", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)




    @app_commands.command(name="ban", description="Ban le membre du serveur.")
    @app_commands.guild_only()
    async def ban(self, ctx, member: str, reason: str = None):
        """ Ban le membre du serveur. """
        if not ctx.user.guild_permissions.ban_members:
            await ctx.response.send_message("❌ Vous n'avez pas la permission de bannir des membres.", ephemeral=True)
            return

        try:
            # Utilisation du convertisseur MemberID pour obtenir l'ID
            member_id = await MemberID().convert(ctx, member)
            m = ctx.guild.get_member(member_id)
            if m is not None and await permissions.check_priv(ctx, m):
                return

            await ctx.guild.ban(discord.Object(id=member_id), reason=default.responsible(ctx.user, reason))
            await ctx.response.send_message(default.actionmessage("banned"))
        except Exception as e:
            await ctx.response.send_message(str(e))


    @app_commands.command(name="clear", description="Supprime un certain nombre de messages.")
    @app_commands.guild_only()
    @app_commands.check(lambda ctx: ctx.user.guild_permissions.manage_messages)  # Vérification des permissions
    async def clear(self, ctx: discord.Interaction, number: int, member: discord.Member = None, role: discord.Role = None):
        """ Supprime les messages en fonction du nombre, du membre ou du rôle spécifié. """
        
        if number < 1 or number > 1000:
            await ctx.response.send_message("❌ Vous devez spécifier un nombre de messages entre 1 et 1000.", ephemeral=True)
            return

        # On indique que le bot va prendre un peu de temps pour répondre
        await ctx.response.defer(ephemeral=True)

        try:
            messages_to_delete = []
            async for message in ctx.channel.history(limit=number):
                if message.created_at < discord.utils.utcnow() - timedelta(days=14):
                    continue  # Ignore les messages plus anciens que 14 jours
                
                if member and message.author == member:
                    messages_to_delete.append(message)
                elif role and any(r.id == role.id for r in message.author.roles):
                    messages_to_delete.append(message)
                elif not member and not role:
                    messages_to_delete.append(message)

            if not messages_to_delete:
                await ctx.followup.send("❌ Aucun message correspondant à vos critères trouvé.", ephemeral=True)
                return

            await ctx.channel.delete_messages(messages_to_delete)

            # Confirmation avec followup.send (car ctx.response.defer a été utilisé)
            await ctx.followup.send(f"✅ {len(messages_to_delete)} messages supprimés.", ephemeral=True)

        except discord.Forbidden:
            await ctx.followup.send("❌ Je n'ai pas la permission de supprimer les messages.", ephemeral=True)
        except Exception as e:
            await ctx.followup.send(f"❌ Une erreur est survenue: {str(e)}", ephemeral=True)

    async def setup(self):
        # Register commands for your bot
        await self.bot.tree.sync()

# Ajoutez votre cog au bot
async def setup(bot):
    await bot.add_cog(ModerationCog(bot))


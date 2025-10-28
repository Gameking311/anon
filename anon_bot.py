# file: anon_bot.py
import os
import discord
from discord import app_commands
from discord.ext import commands

# Config : PLACE LES IDs en int
ANON_CHANNEL_ID = 123456789012345678  # canal public où les messages anonymes seront postés
LOG_CHANNEL_ID  = 987654321098765432  # canal privé de log (mod-only)

# Récupère le token depuis une variable d'environnement
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Définis DISCORD_BOT_TOKEN dans les variables d'environnement")

intents = discord.Intents.default()
# On n'a pas besoin de message_content pour poster via slash, mais si tu veux lire messages, active-le.
bot = commands.Bot(command_prefix="!", intents=intents)

class Anon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="anon", description="Envoyer un message public de façon anonyme (mod log garde l'auteur).")
    @app_commands.describe(message="Le message à envoyer anonymement")
    async def anon(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)  # réponse éphémère immédiate
        guild = interaction.guild
        if guild is None:
            await interaction.followup.send("Cette commande fonctionne uniquement sur un serveur.", ephemeral=True)
            return

        # Récupère les channels
        anon_channel = guild.get_channel(ANON_CHANNEL_ID)
        log_channel  = guild.get_channel(LOG_CHANNEL_ID)
        if anon_channel is None or log_channel is None:
            await interaction.followup.send("Configuration du bot incorrecte : canal introuvable.", ephemeral=True)
            return

        # Poste le message dans le canal public (sans auteur)
        embed_public = discord.Embed(
            description=message,
            color=discord.Color.blurple()
        )
        embed_public.set_footer(text="Envoyé anonymement — utilisez /report pour signaler si nécessaire.")
        posted = await anon_channel.send(embed=embed_public)

        # Log interne (visible seulement au staff/au canal de log)
        embed_log = discord.Embed(title="Message anonyme envoyé (log)", color=discord.Color.dark_grey())
        embed_log.add_field(name="Auteur", value=f"{interaction.user} — `{interaction.user.id}`", inline=False)
        embed_log.add_field(name="Message", value=message, inline=False)
        embed_log.add_field(name="Canal public", value=f"{anon_channel.mention}", inline=False)
        embed_log.add_field(name="Message ID (public)", value=str(posted.id), inline=False)
        embed_log.set_footer(text=f"Envoyé le {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        await log_channel.send(embed=embed_log)

        # Confirme à l'utilisateur (éphemère)
        await interaction.followup.send("Ton message a bien été envoyé anonymement.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Anon(bot))
    # synchronise les commandes globales (optionnel: restrict to guild for fast registering)
    # await bot.tree.sync()

# démarrage
@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user} (id: {bot.user.id})")
    # Si tu veux verrouiller les commandes au serveur pendant le dev, tu peux guild sync ici.

# charge le cog (compatibilité simple)
async def main():
    async with bot:
        await setup(bot)
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

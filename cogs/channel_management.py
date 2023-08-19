import json

import discord
from discord import app_commands
from discord.ext import commands
from modals.secret_channel import ModChannel, SecretChannel
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

with open("./config.json", "r") as f:
    config = json.load(f)

engine = create_engine(config["DATABASE"])

class ChannelManagement(commands.GroupCog, name='setup'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='set_mod_channel', description='Set the channel that the mod output goes to.')
    async def set_mod_channel(self, interaction: discord.Interaction, mod_channel: discord.TextChannel):
        async with interaction.channel.typing():
            with Session(engine) as session:
                existing_mod_channel = session.execute(select(ModChannel).where(ModChannel.guild_id==interaction.guild_id)).scalar_one_or_none()
                if existing_mod_channel is None:
                    new_mod_channel = ModChannel(
                        guild_id=interaction.guild_id,
                        channel_id=mod_channel.id
                    )
                    session.add(new_mod_channel)
                    session.commit()
                else:
                    session.execute(update(ModChannel).where(ModChannel.guild_id==interaction.guild_id).values(channel_id=mod_channel.id))
                    session.commit()
            await interaction.response.send_message(f"Set the mod channel to {mod_channel.mention}.", ephemeral=True, delete_after=30)


    @app_commands.command(name='set_anonymous_channel', description='Set the channel that the anonymous posts go to.')
    async def set_anonymous_channel(self, interaction: discord.Interaction, anon_channel: discord.TextChannel):
        async with interaction.channel.typing():
            with Session(engine) as session:
                existing_anon_channel = session.execute(select(SecretChannel).where(SecretChannel.guild_id==interaction.guild_id)).scalar_one_or_none()
                if existing_anon_channel is None:
                    new_anon_channel = SecretChannel(
                        guild_id=interaction.guild_id,
                        channel_id=anon_channel.id
                    )
                    session.add(new_anon_channel)
                    session.commit()
                else:
                    session.execute(update(SecretChannel).where(SecretChannel.guild_id==interaction.guild_id).values(channel_id=anon_channel.id))
                    session.commit()
            await interaction.response.send_message(f"Set the anonymous channel to {anon_channel.mention}.", ephemeral=True, delete_after=30)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelManagement(bot))
    print(f"{__name__[5:].upper()} loaded")


async def teardown(bot: commands.Bot):
    await bot.remove_cog(ChannelManagement(bot)) #type: ignore
    print(f"{__name__[5:].upper()} unloaded")

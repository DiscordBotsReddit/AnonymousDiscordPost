import json
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from modals.secret_channel import ModChannel, SecretChannel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

with open("./config.json", "r") as f:
    config = json.load(f)

engine = create_engine(config["DATABASE"])

async def find_cmd(bot: commands.Bot, cmd: str, group: Optional[str] = None):
    if group is None:
        command = discord.utils.find(
            lambda c: c.name.lower() == cmd.lower(),
            await bot.tree.fetch_commands(),
        )
        return command
    else:
        cmd_group = discord.utils.find(
            lambda cg: cg.name.lower() == group.lower(),
            await bot.tree.fetch_commands(),
        )
        for child in cmd_group.options:  #type: ignore
            if child.name.lower() == cmd.lower():
                return child
    return "No command found."

class Secrets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='anon_post', description='Sends an anonymous post. ** Mods can see the non-anonymous version **')
    async def send_anon_post(self, interaction: discord.Interaction, content: str):
        if len(content.strip()) == 0:
            return await interaction.response.send_message("Please send a message with something in `content`.", ephemeral=True, delete_after=30)
        with Session(engine) as session:
            mod_channel = session.execute(select(ModChannel.channel_id).where(ModChannel.guild_id==interaction.guild_id)).scalar_one_or_none()
            anon_channel = session.execute(select(SecretChannel.channel_id).where(SecretChannel.guild_id==interaction.guild_id)).scalar_one_or_none()
        if anon_channel is None:
            set_anon_command = await find_cmd(self.bot, 'set_anonymous_channel', 'setup')
            return await interaction.response.send_message(f"Anonymous channel has not been set up yet.  Please use {set_anon_command.mention}.", delete_after=120)
        anon_embed = discord.Embed(color=discord.Color.random(), title="Anonymous Says:", description=content)
        anon_channel = await self.bot.fetch_channel(anon_channel)
        anon_msg = await anon_channel.send(embed=anon_embed)
        if mod_channel is not None:
            mod_embed = discord.Embed(color=discord.Color.dark_orange(), title=f'Anonymous post by {interaction.user.display_name}', description=f"Content: {content}")
            mod_embed.add_field(name='User ID', value=interaction.user.id)
            mod_embed.add_field(name='User Link', value=interaction.user.mention)
            mod_embed.add_field(name='', value='', inline=False)
            mod_embed.add_field(name='Message ID', value=anon_msg.id)
            mod_embed.add_field(name='Message Link', value=anon_msg.jump_url)
            mod_channel = await self.bot.fetch_channel(mod_channel)
            await mod_channel.send(embed=mod_embed)
        await interaction.response.send_message(f"Your anonymous post has been sent.{'  **AS A REMINDER, MODS CAN SEE YOUR INFO IN THEIR VERSION**' if mod_channel is not None else ''}", ephemeral=True, delete_after=30)

        

async def setup(bot: commands.Bot):
    await bot.add_cog(Secrets(bot))
    print(f"{__name__[5:].upper()} loaded")


async def teardown(bot: commands.Bot):
    await bot.remove_cog(Secrets(bot)) #type: ignore
    print(f"{__name__[5:].upper()} unloaded")

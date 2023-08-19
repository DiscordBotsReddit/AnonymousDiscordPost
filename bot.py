import json
import os
from time import time
from typing import Literal, Optional

import discord
from discord.ext import commands
from discord.ext.commands import ExtensionAlreadyLoaded

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True


with open("config.json", "r") as f:
    config = json.load(f)

activity = discord.Activity(name=f"you tell secrets.", type=discord.ActivityType.watching)
bot = commands.Bot(command_prefix=config['PREFIX'], intents=intents, activity=activity)


TOKEN = config['TOKEN']


@bot.event
async def on_ready():
    for subdir, _, files in os.walk("cogs"):
        files = [file for file in files if file.endswith(".py") and "template" not in file]
        for file in files:
            if len(subdir.split("cogs\\")) >= 2:
                try:
                    sub = subdir.split('cogs\\')[1]
                    await bot.load_extension(f"cogs.{sub}.{file[:-3]}")
                except ExtensionAlreadyLoaded:
                    sub = subdir.split('cogs\\')[1]
                    await bot.reload_extension(f"cogs.{sub}.{file[:-3]}")
            else:
                try:
                    await bot.load_extension(f"{subdir}.{file[:-3]}")
                except ExtensionAlreadyLoaded:
                    await bot.reload_extension(f"{subdir}.{file[:-3]}")

    print("Current guilds:")
    for guild in bot.guilds:
        print(f"{guild.name} ({guild.id}) - {guild.member_count:,} members")
    print("Logged in as", bot.user)


@bot.command()
@commands.is_owner()
async def reload(ctx: commands.Context, extension: str):
    try:
        await ctx.message.delete()
        for subdir, _, files in os.walk("cogs"):
            files = [file for file in files if file.endswith(".py") and file.startswith(extension)]
            for file in files:
                if len(subdir.split("cogs\\")) >= 2 and file.startswith(extension):
                    try:
                        sub = subdir.split('cogs\\')[1]
                        await bot.load_extension(f"cogs.{sub}.{file[:-3]}")
                        await ctx.send(f"Loaded `cogs.{sub}.{file[:-3].upper()}`", delete_after=15)
                    except ExtensionAlreadyLoaded:
                        sub = subdir.split('cogs\\')[1]
                        await bot.reload_extension(f"cogs.{sub}.{file[:-3]}")
                        await ctx.send(f"Reloaded `cogs.{sub}.{file[:-3].upper()}`", delete_after=15)
                else:
                    try:
                        await bot.load_extension(f"cogs.{file[:-3]}")
                        await ctx.send(f"Loaded `cogs.{file[:-3].upper()}`", delete_after=15)
                    except ExtensionAlreadyLoaded:
                        await bot.reload_extension(f"cogs.{file[:-3]}")
                        await ctx.send(f"Reloaded `cogs.{file[:-3].upper()}`", delete_after=15)
    except Exception as e:
        await ctx.send(f"Error reloading `{extension.upper()}`\n{e}")


@bot.command()
@commands.is_owner()
async def reloadall(ctx: commands.Context):
    await ctx.message.delete()
    for subdir, _, files in os.walk("cogs"):
        files = [file for file in files if file.endswith(".py") and "template" not in file]
        for file in files:
            if len(subdir.split("cogs\\")) >= 2:
                try:
                    sub = subdir.split('cogs\\')[1]
                    await bot.load_extension(f"cogs.{sub}.{file[:-3]}")
                    await ctx.send(f"Loaded `cogs.{sub}.{file[:-3]}`", delete_after=15)
                except ExtensionAlreadyLoaded:
                    sub = subdir.split('cogs\\')[1]
                    await bot.reload_extension(f"cogs.{sub}.{file[:-3]}")
                    await ctx.send(f"Reloaded `cogs.{sub}.{file[:-3]}`", delete_after=15)
            else:
                try:
                    await bot.load_extension(f"{subdir}.{file[:-3]}")
                    await ctx.send(f"Loaded `{subdir}.{file[:-3]}`")
                except ExtensionAlreadyLoaded:
                    await bot.reload_extension(f"{subdir}.{file[:-3]}")
                    await ctx.send(f"Reloaded `{subdir}.{file[:-3]}`", delete_after=15)


@bot.command()
@commands.is_owner()
async def load(ctx: commands.Context, extension: str):
    await ctx.message.delete()
    try:
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Loaded `{extension.upper()}`", delete_after=15)
    except:
        await ctx.send(f"Error loading `{extension.upper()}`\n{e}")  # type: ignore



# https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^", "x"]] = None) -> None:
    await ctx.reply("Sync request received.")
    if not guilds:
        if spec == "~":  # sync all to current guild
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":   # sync global to current guild
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":  # remove commands sync'd to current guild
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        elif spec == "x":  # remove all global sync'd commands
            ctx.bot.tree.clear_commands(guild=None)
            await ctx.bot.tree.sync()
            await ctx.send("Cleared all global commands.", delete_after=15)
            return
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}", delete_after=15
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.", delete_after=15)

bot.run(TOKEN)
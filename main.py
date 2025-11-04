# main.py
import discord
from discord.ext import commands
import os
import asyncio
import importlib
import inspect
from dotenv import load_dotenv
from keep_alive import keep_alive  # keep_alive.py from earlier

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents: message_content is required to receive prefix-based commands
intents = discord.Intents.default()
intents.message_content = True

# Use a non-slash text prefix for hybrid commands (slash commands will show under /)
bot = commands.Bot(command_prefix="!", intents=intents)

# Guard to sync application commands once per process start
_synced = False

@bot.event
async def on_ready():
    global _synced
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    # Debug: show loaded cogs and commands
    try:
        print(f"🔧 Loaded cogs: {list(bot.cogs.keys())}")
        print("🔧 Loaded commands:", ", ".join(sorted(cmd.qualified_name for cmd in bot.commands)))
    except Exception as e:
        print(f"(debug) failed to list cogs/commands: {e}")
    if not _synced:
        # Optionally fast-sync to a specific guild for immediate availability
        guild_id = os.getenv("DISCORD_GUILD_ID")
        try:
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                gsynced = await bot.tree.sync(guild=guild)
                print(f"⚡ Synced {len(gsynced)} commands to guild {guild_id}.")
            # Register global application commands so they appear in / suggestions
            synced = await bot.tree.sync()
            print(f"🔁 Synced {len(synced)} application commands globally.")
        except Exception as e:
            print(f"❌ Failed to sync application commands: {e}")
        _synced = True
    print("Bot is ready!")

async def load_cogs_from_folder(folder: str = "commands"):
    """
    Dynamically import modules from the commands folder and:
      - if module has async setup(bot) -> call it
      - else find a Cog subclass in module and add it
    """
    for filename in os.listdir(folder):
        if not filename.endswith(".py") or filename.startswith("_"):
            continue
        module_name = filename[:-3]
        full_module = f"{folder}.{module_name}"
        try:
            module = importlib.import_module(full_module)
            # If module provides an async setup(bot) function, call it
            setup_func = getattr(module, "setup", None)
            if setup_func and inspect.iscoroutinefunction(setup_func):
                print(f"→ calling setup() in {full_module}")
                await setup_func(bot)
                continue

            # Otherwise, attempt to locate a Cog subclass in the module
            cog_class = None
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, commands.Cog) and obj is not commands.Cog:
                    cog_class = obj
                    break

            if cog_class:
                print(f"→ loading Cog {cog_class.__name__} from {full_module}")
                await bot.add_cog(cog_class(bot))
            else:
                print(f"⚠️ No Cog or async setup() found in {full_module}; skipping.")
        except Exception as e:
            print(f"❌ Failed to load {full_module}: {e}")

async def setup_hook():
    # discord.py will call this before login completes
    await load_cogs_from_folder("commands")

# For discord.py >=2.0 we attach setup_hook to the bot
# If you prefer, you can use bot.setup_hook = setup_hook
bot.setup_hook = setup_hook

if __name__ == "__main__":
    keep_alive()  # start the small web server for uptime pings
    bot.run(TOKEN)

import discord
from discord.ext import commands
import random

class VibeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vibe")
    async def vibe(self, ctx, mood: str):
        """Suggest media for a vibe"""
        vibes = {
            "chill": ["🎥 Before Sunrise", "🎵 Lofi Beats", "📖 Norwegian Wood"],
            "nostalgic": ["🎥 Mid90s", "🎵 Somebody Else - The 1975", "📖 Eternal Sunshine"],
            "creative": ["🎥 Inception", "🎮 Life is Strange", "📖 Steal Like an Artist"]
        }

        if mood.lower() not in vibes:
            await ctx.send("Available vibes: chill, nostalgic, creative")
            return

        items = "\n".join(vibes[mood.lower()])
        embed = discord.Embed(title=f"🎧 Vibe: {mood}", description=items, color=0xffa047)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VibeCog(bot))

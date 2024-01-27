import time
from datetime import datetime, timedelta
import discord
import requests
import asyncio
from discord.ext import commands, tasks
from dtoken import TOKEN

bot = discord.Client(intents=discord.Intents.all())
bitcoin_api_url = "https://api.blockchair.com/bitcoin/stats"
discord_token = TOKEN
channel_id = 1231231231231231  # Replace with the actual voice channel ID

@tasks.loop(minutes=3)
async def update_channel_name():
    try:
	print("[Halving Countdown]")
        # Fetch the current block number and timestamp from the API
        response = requests.get(bitcoin_api_url)
        data = response.json()
        current_block = data['data']['blocks']

        # Set the known halving block number
        halving_block = 840000

        # Calculate the blocks until halving
        blocks_until_halving = max(0, halving_block - current_block)

        # Use information about the blocks mined in the last 24 hours to estimate the average block time
        blocks_24h = data['data']['blocks_24h']
        average_block_time = (24 * 60) / blocks_24h  # Assuming blocks_24h provides the correct number of blocks in the last 24 hours

        # Calculate the estimated time until halving based on the average block time
        estimated_time_until_halving = timedelta(minutes=blocks_until_halving * average_block_time)

        # Convert the timedelta to days and hours
        days_until_halving = estimated_time_until_halving.days
        hours_until_halving = (estimated_time_until_halving.seconds // 3600) % 24

        # Format the time display
        if days_until_halving > 0:
            halving_time_display = f"{days_until_halving} days"
        elif hours_until_halving > 0:
            halving_time_display = f"{hours_until_halving} hours"
        else:
            halving_time_display = "less than 1 hour"

        new_channel_name = f"{blocks_until_halving} blocks | {halving_time_display} until halving"

        voice_channel = bot.get_channel(channel_id)
        await voice_channel.edit(name=new_channel_name)

    except Exception as e:
        print(f"Error updating channel name: {e}")



@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
    update_channel_name.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")

bot.run(discord_token)

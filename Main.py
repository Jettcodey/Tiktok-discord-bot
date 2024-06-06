import discord
import re
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

domains = ['vm.tiktok.com', 'vt.tiktok.com', 'tiktok.com']
domain_pattern = '|'.join([re.escape(domain) for domain in domains])
link_pattern = re.compile(r'https?://(?:' + domain_pattern + r')/[^\s]+')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Successfully synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.tree.command(name="search", description="DO NOT USE | Search for all links from specified domains in the channel")
async def search(interaction: discord.Interaction):
    """Search for all links from specified domains in the channel."""
    links = []
    channel = interaction.channel
    async for message in channel.history(limit=1000):
        found_links = link_pattern.findall(message.content)
        if found_links:
            links.extend(found_links)

    if links:
        links_message = '\n'.join(links)
        await interaction.response.send_message(f'Found the following links:\n```\n{links_message}\n```')
    else:
        await interaction.response.send_message('No links found from the specified domains')

@bot.tree.command(name="txt", description="Search for all links from Tiktok domains in the channel and save to a text file")
async def txt(interaction: discord.Interaction):
    """Search for all links from specified domains in the channel and save to a text file."""
    links = []
    channel = interaction.channel
    async for message in channel.history(limit=1000):
        found_links = link_pattern.findall(message.content)
        if found_links:
            links.extend(found_links)

    if links:
        with open('found_links.txt', 'w') as file:
            for link in links:
                file.write(link + '\n')
        
        await interaction.response.send_message('Links saved to found_links.txt', file=discord.File('found_links.txt'))
        
        os.remove('found_links.txt')
    else:
        await interaction.response.send_message('No links found from the specified domains')

# Run the bot with the YOUR OWN TOKEN
bot.run('YOUR_TOKEN_HERE')

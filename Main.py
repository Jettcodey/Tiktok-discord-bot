import os
import json
import httpx
import asyncio
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
import re

tiktok_link_pattern = re.compile(r'https?://(?:vm\.tiktok\.com|vt\.tiktok\.com)/[^\s]+')

async def download_media(item, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    if item.images:
        print("[*] Downloading Slideshow")
        index = 0
        for image_url in item.images:
            file_name = f"{item['id']}_{index}.jpeg"
            if os.path.exists(os.path.join(folder, file_name)):
                print(f"[!] File '{file_name}' already exists. Skipping")
                continue
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    image_data = await response.read()
                    with open(os.path.join(folder, file_name), 'wb') as file:
                        file.write(image_data)
            index += 1
    else:
        file_name = f"{item['id']}.mp4"
        if os.path.exists(os.path.join(folder, file_name)):
            print(f"[!] File '{file_name}' already exists. Skipping")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(item['url']) as response:
                video_data = await response.read()
                with open(os.path.join(folder, file_name), 'wb') as file:
                    file.write(video_data)

async def get_video(url, watermark):
    id_video = await get_id_video(url)
    api_url = f"https://api22-normal-c-alisg.tiktokv.com/aweme/v1/feed/?aweme_id={id_video}&iid=7318518857994389254&device_id=7318517321748022790&channel=googleplay&app_name=musical_ly&version_code=300904&device_platform=android&device_type=ASUS_Z01QD&version=9"
    
    async with aiohttp.ClientSession() as session:
        async with session.options(api_url) as response:
            response.raise_for_status()
            data = await response.text()
            data = json.loads(data)
    
    if not data['aweme_list']:
        print(f"Error: No aweme_list found in JSON response for MediaID: {id_video}")
        return None

    video_data = data['aweme_list'][0]
    image_urls = []
    url_media = None
    if 'image_post_info' in video_data:
        print("[*] Video is slideshow")
        for element in video_data['image_post_info']['images']:
            # url_list[0] contains a webp, url_list[1] contains a jpeg
            image_urls.append(element['display_image']['url_list'][1])
    else:
        url_media = video_data['video']['download_addr']['url_list'][0] if watermark else video_data['video']['play_addr']['url_list'][0]
    return {'url': url_media, 'images': image_urls, 'id': id_video}

async def get_redirect_url(url: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url, allow_redirects=True)
            final_url = response.url
            print("Final URL:", final_url)
            print("Response Headers:", response.headers)
        return str(final_url)
    except Exception as ex:
        print(f"Error in getting the RedirectURL: {ex}")
        return url
    
async def get_id_video(url: str) -> str:
    if "/t/" in url:
        url = await get_redirect_url(url)

    matching = "/video/" in url
    matching_photo = "/photo/" in url
    if matching:
        start_index = url.index("/video/") + 7
    elif matching_photo:
        start_index = url.index("/photo/") + 7
    else:
        print("Error: URL not found")
        return ''

    id_video = url[start_index:start_index + 19]
    if "?" in id_video:
        id_video = id_video[:id_video.index("?")]

    return id_video

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

@bot.tree.command(name="search", description="Search for all links from specified domains in the channel")
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

@bot.tree.command(name="txt", description="Search for all links from specified domains in the channel and save to a text file")
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

@bot.tree.command(name="download", description="Download media from a TikTok URL")
@app_commands.describe(
    url="The TikTok URL to download media from",
    watermark="Choose whether to download with or without watermark"
)
@app_commands.choices(watermark=[
    app_commands.Choice(name="With Watermark", value="with"),
    app_commands.Choice(name="No Watermark", value="no")
])
async def download(interaction: discord.Interaction, url: str, watermark: app_commands.Choice[str]):
    """Download media from a TikTok URL with or without watermark."""
    await interaction.response.defer()
    with_watermark = watermark.value == "with"
    media = await get_video(url, with_watermark)
    if media:
        await interaction.followup.send(f"Media URL: {media['url']}")
        if media['images']:
            await interaction.followup.send(f"Image URLs: {', '.join(media['images'])}")
        await download_media(media, "downloads/")
    else:
        await interaction.followup.send("Failed to retrieve media data.")

bot.run('YOUR_BOT_TOKEN')  # Replace 'YOUR_BOT_TOKEN' with your actual bot token


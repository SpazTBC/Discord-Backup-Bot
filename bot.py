import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import json
import requests
import asyncio

# Load environment variables
load_dotenv()

# Get the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Specify the API endpoint
API_ENDPOINT = "http://localhost:5000/api/upload"  # Updated API endpoint to handle file uploads

# Set to True if you want to send logs and JSON files to the API, Turn To False If You Don't Wish to use this.
send_to_api = True

# Create bot instance with intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to generate a random channel name
def generate_channel_name():
    adjectives = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Pink', 'Black', 'White']
    nouns = ['Channel', 'Server', 'Room', 'Zone', 'Hub', 'Nexus']
    return f'{random.choice(adjectives)}-{random.choice(nouns)}'

# Function to send data to API
async def send_data_to_api(guild_id):
    while True:
        files = {
            'backup.json': open('backup.json', 'rb'), 
            'roles_backup.json': open('roles_backup.json', 'rb'), 
            'command_log.txt': open('command_log.txt', 'rb'),
            'user_list.json': open('user_list.json', 'rb')  # Include user_list.json in the files to send
        }
        try:
            headers = {'X-Guild-ID': str(guild_id)}  # Convert guild ID to string
            response = requests.post(API_ENDPOINT, files=files, headers=headers)
            if response.status_code == 200:
                print("Data sent to API successfully!")
            else:
                print(f"Failed to send data to API. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while sending data to API: {e}")
        await asyncio.sleep(60) #Change this to how many seconds you want this to send

# Function to update user count and user list
async def update_user_info():
    try:
        user_count = sum(len(guild.members) for guild in bot.guilds)
        print(f"User count: {user_count}")
        user_list = {"users": [member.name for guild in bot.guilds for member in guild.members]}
        with open('user_list.json', 'w') as f:
            json.dump(user_list, f, indent=4)
        if send_to_api:
            for guild in bot.guilds:
                bot.loop.create_task(send_data_to_api(guild.id))
    except AttributeError:
        print("Failed to retrieve user info")

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    if send_to_api:
        for guild in bot.guilds:
            bot.loop.create_task(send_data_to_api(guild.id))
    await update_user_info()

# Log command usage
@bot.event
async def on_command(ctx):
    with open('command_log.txt', 'a') as f:
        f.write(f'Command executed: {ctx.message.content}\n')

# Command: Create multiple channels with random names
@bot.command()
async def create_channels(ctx, num_channels: int):
    for _ in range(num_channels):
        channel_name = generate_channel_name()
        await ctx.guild.create_text_channel(channel_name)
        await ctx.guild.create_voice_channel(channel_name)

# Command: Delete all channels
@bot.command()
async def delete_all_channels(ctx):
    for channel in ctx.guild.channels:
        await channel.delete()

# Command: Backup channels
@bot.command()
async def backup(ctx):
    backup_data = []

    for category in ctx.guild.categories:
        category_info = {
            "name": category.name,
            "channels": []
        }

        for channel in category.channels:
            channel_info = {
                "name": channel.name,
                "type": str(channel.type)
            }
            category_info["channels"].append(channel_info)

        backup_data.append(category_info)

    with open('backup.json', 'w') as f:
        json.dump(backup_data, f, indent=4)

    await ctx.send("Backup successfully created!")

    if send_to_api:
        bot.loop.create_task(send_data_to_api(ctx.guild.id))

# Command: Return backup
@bot.command()
async def returnback(ctx):
    with open('backup.json', 'r') as f:
        backup_data = json.load(f)

        for category_data in backup_data:
            new_category = await ctx.guild.create_category(category_data["name"])

            for channel_info in category_data["channels"]:
                channel_name = channel_info["name"]
                channel_type = discord.ChannelType[channel_info["type"]]

                if channel_type == discord.ChannelType.text:
                    await ctx.guild.create_text_channel(channel_name, category=new_category)
                elif channel_type == discord.ChannelType.voice:
                    await ctx.guild.create_voice_channel(channel_name, category=new_category)

    await ctx.send("Backup successfully returned!")

# Command: Backup roles
@bot.command()
async def backup_roles(ctx):
    backup_data = []

    for role in ctx.guild.roles:
        if role.name != "@everyone":  # Exclude the default @everyone role
            role_info = {
                "name": role.name,
                "color": role.color.value,
                "permissions": role.permissions.value,
                "members": [member.id for member in role.members],
                "hoist": role.hoist  # Include the "Display separately from other users" flag
            }
            backup_data.append(role_info)

    with open('roles_backup.json', 'w') as f:
        json.dump(backup_data, f, indent=4)

    await ctx.send("Roles backup successfully created!")

    if send_to_api:
        bot.loop.create_task(send_data_to_api(ctx.guild.id))

# Command: Restore roles
@bot.command()
async def restore_roles(ctx):
    with open('roles_backup.json', 'r') as f:
        backup_data = json.load(f)

        for role_info in backup_data:
            role_name = role_info["name"]
            role_color = role_info["color"]
            role_permissions = discord.Permissions(role_info["permissions"])
            role_members_ids = role_info["members"]
            role_hoist = role_info.get("hoist", False)  # Retrieve "Display separately from other users" flag

            # Check if role already exists
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role is None:
                # Create the role if it doesn't exist
                new_role = await ctx.guild.create_role(name=role_name, color=discord.Color(role_color), permissions=role_permissions, hoist=role_hoist)
                print(f"Role created: {new_role.name}")

                # Assign the role back to members
                for member_id in role_members_ids:
                    member = ctx.guild.get_member(member_id)
                    if member:
                        await member.add_roles(new_role)
            else:
                print(f"Role already exists: {role.name}")

    await ctx.send("Roles successfully restored!")

# Command: Delete all roles
@bot.command()
async def delete_all_roles(ctx):
    for role in ctx.guild.roles:
        if role.name != "@everyone":  # Exclude the default @everyone role
            await role.delete()
    
    await ctx.send("All roles except @everyone have been deleted!")

# Run the bot
bot.run(TOKEN)

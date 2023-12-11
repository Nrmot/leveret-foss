import discord
from discord.ext import commands
import json
import sys

# Load bot configuration from file
def load_bot_configuration():
    try:
        with open('bot_configuration.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: bot_configuration.json not found.")
        return None

bot_config = load_bot_configuration()

if bot_config:
    bot_token = bot_config.get('bot_token', '')
    bot_admins = bot_config.get('bot_admins', [])
    bot_owner_id = bot_config.get('bot_owner_id', 0)  # Replace with the actual user ID of the bot owner
    tag_creator_role_id = bot_config.get('tag_creator_role_id', [])  # Replace with the actual role ID for tag creators
else:
    print("Exiting due to missing bot configuration.")
    exit()

# Load bot bans from file
def load_bot_bans():
    try:
        with open('bot_bans.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

bot_bans = load_bot_bans()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents)

# Dictionary to store tags: {tag_name: {'message': 'tag_message', 'creator': creator_id}}
tags = {}

# Load tags from file
def load_tags():
    try:
        with open('tags_database.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save tags to file
def save_tags(tags):
    with open('tags_database.json', 'w') as file:
        json.dump(tags, file, indent=4)

#
# INCLUSIVE TAG SYSTEM THAT EVERYONE CAN USE
#

# Command to add a tag
@bot.command(name='m_addtag', help='Add a tag with a message')
async def inclusive_add_tag(ctx, tag, *, message):
    if ctx.author.id not in bot_bans:
        tags[tag] = {'message': message, 'creator': ctx.author.id, 'type':'inclusive'}
        save_tags(tags)
        await ctx.send(f'Tag `{tag}` added successfully!')
    else:
        await ctx.send("You are banned from using this bot.")

# Command to get a tag
@bot.command(name='m', help='Get the message associated with a tag')
async def inclusive_get_tag(ctx, tag):
    if tag in tags:
        await ctx.send(f'Tag `{tag}`: {tags[tag]["message"]}\nCreated by: {tags[tag]["creator"]}\nType: {tags[tag]["type"]}')
    else:
        await ctx.send(f'Tag `{tag}` not found.')

# Command to delete a tag
@bot.command(name='m_deltag', help='Delete a tag (can be deleted by the original creator or bot admins)')
async def inclusive_delete_tag(ctx, tag):
    if tag in tags:
        tag_info = tags[tag]
        if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
            del tags[tag]
            save_tags(tags)
            await ctx.send(f'Tag `{tag}` deleted successfully!')
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send(f'Tag `{tag}` not found.')

# Command to edit a tag (bot admin or tag owner only)
@bot.command(name='m_edittag', help='Edit a tag (bot admin or tag owner only)')
async def inclusive_edit_tag(ctx, tag, *, new_message):
    if tag in tags:
        tag_info = tags[tag]
        if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
            tags[tag]['message'] = new_message
            save_tags(tags)
            await ctx.send(f'Tag `{tag}` edited successfully!')
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send(f'Tag `{tag}` not found.')

#
# EXCLUSIVE TAG SYSTEM THAT REQUIRES A TAG CREATOR ROLE
#

# Command to add a tag
@bot.command(name='o_addtag', help='Add a tag with a message')
async def exclusive_add_tag(ctx, tag, *, message):
    if ctx.author.id not in bot_bans and tag_creator_role_id in [role.id for role in ctx.author.roles]:
        tags[tag] = {'message': message, 'creator': ctx.author.id, 'type':'exclusive'}
        save_tags(tags)
        await ctx.send(f'Tag `{tag}` added successfully!')
    else:
        await ctx.send("You are either banned from using this bot or do not have the required role to create tags.")

# Command to get a tag
@bot.command(name='o', help='Get the message associated with a tag')
async def exclusive_get_tag(ctx, tag):
    if tag in tags:
        await ctx.send(f'Tag `{tag}`: {tags[tag]["message"]}\nCreated by: {tags[tag]["creator"]}\nType: {tags[tag]["type"]}')
    else:
        await ctx.send(f'Tag `{tag}` not found.')

# Command to delete a tag
@bot.command(name='o_deltag', help='Delete a tag (can be deleted by the original creator or bot admins)')
async def exclusive_delete_tag(ctx, tag):
    if tag in tags:
        tag_info = tags[tag]
        if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
            del tags[tag]
            save_tags(tags)
            await ctx.send(f'Tag `{tag}` deleted successfully!')
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send(f'Tag `{tag}` not found.')\

# Command to edit a tag (bot admin or tag owner only)
@bot.command(name='o_edittag', help='Edit a tag (bot admin or tag owner only)')
async def exclusive_edit_tag(ctx, tag, *, new_message):
    if tag in tags:
        tag_info = tags[tag]
        if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
            tags[tag]['message'] = new_message
            save_tags(tags)
            await ctx.send(f'Tag `{tag}` edited successfully!')
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send(f'Tag `{tag}` not found.')

# 
# META COMMANDS
#

# Command to get information about guilds
@bot.command(name='serverinfo', help='Get information about the guilds the bot is in')
async def server_info(ctx):
    guild_info = []
    for guild in bot.guilds:
        guild_info.append(f'**Name:** {guild.name}\n**ID:** {guild.id}\n**Members:** {guild.member_count}\n\n')
    
    if guild_info:
        file_content = '\n'.join(guild_info)
        with open('guild_info.txt', 'w') as file:
            file.write(file_content)
        await ctx.send(file=discord.File('guild_info.txt', 'guild_info.txt'))
    else:
        await ctx.send('The bot is not currently in any guilds.')

# Command to dump all tags (bot owner only)
@bot.command(name='dumptags', help='Dump all tags (bot owner only)')
async def dump_tags(ctx):
    if ctx.author.id == bot_owner_id:
        dump_content = json.dumps(tags, indent=4)
        with open('tags_dump.json', 'w') as file:
            file.write(dump_content)
        await ctx.send(file=discord.File('tags_dump.json', 'tags_dump.json'))
    else:
        await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")

# Command for emergency shutdown (bot owner only)
@bot.command(name='emergency_shutdown', help='Emergency shutdown (bot owner only)')
async def emergency_shutdown(ctx):
    if ctx.author.id == bot_owner_id:
        await ctx.send('Emergency shutdown initiated. Goodbye!')
        sys.exit()
    else:
        await ctx.send("You don't have permission to perform an emergency shutdown.")

# Event when the bot is ready
@bot.event
async def on_ready():
    global tags
    tags = load_tags()
    print(f'Logged on as {bot.user}!')

# Event when a message is received
@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    if message.author.id in bot_bans:
        await message.channel.send("You are banned from using this bot.")
    else:
        await bot.process_commands(message)  # Process commands in on_message
        
bot.run(bot_token)

import discord
from discord import Embed
from discord.ext import commands
import json
import sys
import difflib
import chempy
import re
from chempy import balance_stoichiometry
from pprint import pprint

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
    tag_creator_role_id = bot_config.get('tag_creator_role_id', 0)  # Replace with the actual role ID for tag creators
    bot_bans = bot_config.get('banned_users', [])
else:
    print("Exiting due to missing bot configuration.")
    exit()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents)

# Dictionary to store inclusive tags: {tag_name: {'message': 'tag_message', 'creator': creator_id}}
inclusive_tags = {}

# Dictionary to store exclusive tags: {tag_name: {'message': 'tag_message', 'creator': creator_id}}
exclusive_tags = {}

# Load inclusive tags from file
def load_inclusive_tags():
    try:
        with open('inclusive_tags_database.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Load exclusive tags from file
def load_exclusive_tags():
    try:
        with open('exclusive_tags_database.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save inclusive tags to file
def save_inclusive_tags(tags):
    with open('inclusive_tags_database.json', 'w') as file:
        json.dump(tags, file, indent=4)

# Save exclusive tags to file
def save_exclusive_tags(tags):
    with open('exclusive_tags_database.json', 'w') as file:
        json.dump(tags, file, indent=4)

# Method to find similar tags
def find_similar_tags(tags, keyword):
    return {tag: tag_info for tag, tag_info in tags.items() if keyword.lower() in tag.lower()}

#
# INCLUSIVE TAG SYSTEM THAT EVERYONE CAN USE
#

# Command to get an inclusive tag
@bot.command(name='m', help='Get the message associated with an inclusive tag')
async def inclusive_tag(ctx, tag):
    if ctx.author.id not in bot_bans:
        if tag in inclusive_tags:
            tag_info = inclusive_tags[tag]
            message = f'{tag_info["message"]}'
            try:
                if tag_info['embed']:
                    embed = discord.Embed(description=tag_info['embed'], color=discord.Color.blue())
                    await ctx.send(content=message, embed=embed)
                else:
                    await ctx.send(message)
            except KeyError:
                await ctx.send(message)
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to add an inclusive tag
@bot.command(name='m_addtag', help='Add an inclusive tag with a message')
async def inclusive_add_tag(ctx, tag, *, message):
    if ctx.author.id not in bot_bans:
        if tag not in inclusive_tags:
            inclusive_tags[tag] = {'message': message, 'creator': ctx.author.id, 'type': 'inclusive'}
            save_inclusive_tags(inclusive_tags)
            await ctx.send(f'Tag `{tag}` added successfully!')
        else:
            await ctx.send(f'Tag `{tag}` already exists.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to get an inclusive tag
@bot.command(name='m_info', help='Get the message associated with an inclusive tag')
async def inclusive_get_tag_info(ctx, tag):
    if ctx.author.id not in bot_bans:
        if tag in inclusive_tags:
            tag_info = inclusive_tags[tag]
            message = f'Tag `{tag}`: {tag_info["message"]}\nCreated by: {tag_info["creator"]}\nType: {tag_info["type"]}'
            try:
                if tag_info['embed']:
                    embed = discord.Embed(description=tag_info['embed'], color=discord.Color.blue())
                    await ctx.send(content=message, embed=embed)
                else:
                    await ctx.send(message)
            except KeyError:
                await ctx.send(message)
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to delete an inclusive tag
@bot.command(name='m_deltag', help='Delete an inclusive tag (can be deleted by the original creator or bot admins)')
async def inclusive_delete_tag(ctx, tag):
    if ctx.author.id not in bot_bans:
        if tag in inclusive_tags:
            tag_info = inclusive_tags[tag]
            if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
                del inclusive_tags[tag]
                save_inclusive_tags(inclusive_tags)
                await ctx.send(f'Tag `{tag}` deleted successfully!')
            else:
                await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to edit an inclusive tag (bot admin or tag owner only)
@bot.command(name='m_edittag', help='Edit an inclusive tag (bot admin or tag owner only)')
async def inclusive_edit_tag(ctx, tag, *, new_message):
    if ctx.author.id not in bot_bans:
        if tag in inclusive_tags:
            tag_info = inclusive_tags[tag]
            if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
                inclusive_tags[tag]['message'] = new_message
                save_inclusive_tags(inclusive_tags)
                await ctx.send(f'Tag `{tag}` edited successfully!')
            else:
                await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to see the list of inclusive tags the user owns
@bot.command(name='m_mytags', help='See the list of inclusive tags you own')
async def inclusive_my_tags(ctx):
    if ctx.author.id not in bot_bans:
        user_id = ctx.author.id
        user_tags = {tag: tag_info for tag, tag_info in inclusive_tags.items() if tag_info['creator'] == user_id}
        
        if user_tags:
            tag_list = '\n'.join([f'`{tag}`' for tag in user_tags])
            await ctx.send(f'Your inclusive tags:\n{tag_list}')
        else:
            await ctx.send('You do not own any inclusive tags.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to search for similar inclusive tags
@bot.command(name='m_searchtags', help='Search for similar inclusive tags')
async def inclusive_search_tags(ctx, keyword):
    if ctx.author.id not in bot_bans:
        similar_tags = find_similar_tags(inclusive_tags, keyword)
        
        if similar_tags:
            tag_list = '\n'.join([f'`{tag}`' for tag in similar_tags])
            await ctx.send(f'Similar inclusive tags for "{keyword}":\n{tag_list}')
        else:
            await ctx.send(f'No similar inclusive tags found for "{keyword}".')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to embed or edit a message onto an inclusive tag
@bot.command(name='m_embedtag', help='Embed a message onto an inclusive tag or create a new tag with an embed')
async def inclusive_embed_tag(ctx, tag, *, embed_content):
    if ctx.author.id not in bot_bans:
        if tag in inclusive_tags and (ctx.author.id == inclusive_tags[tag]['creator'] or ctx.author.id in bot_admins):
            inclusive_tags[tag]['embed'] = embed_content
            save_inclusive_tags(inclusive_tags)
            await ctx.send(f'Message embedded onto tag `{tag}` successfully!')
        else:
            inclusive_tags[tag] = {'message': '', 'creator': ctx.author.id, 'type': 'inclusive', 'embed': embed_content}
            save_inclusive_tags(inclusive_tags)
            await ctx.send(f'New tag `{tag}` created with embedded message successfully!')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to edit the embedded content of an inclusive tag
@bot.command(name='m_editembed', help='Edit the embedded content of an inclusive tag')
async def inclusive_edit_embed_tag(ctx, tag, *, embed_content):
    if ctx.author.id not in bot_bans:
        if tag in inclusive_tags and (ctx.author.id == inclusive_tags[tag]['creator'] or ctx.author.id in bot_admins):
            if 'embed' in inclusive_tags[tag]:
                inclusive_tags[tag]['embed'] = embed_content
                save_inclusive_tags(inclusive_tags)
                await ctx.send(f'Embedded content of tag `{tag}` edited successfully!')
            else:
                await ctx.send(f'Tag `{tag}` does not have embedded content. Use `%m_embedtag` to create a new tag with embedded content.')
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

#
# EXCLUSIVE TAG SYSTEM THAT REQUIRES A TAG CREATOR ROLE
#

# Command to get an exclusive tag
@bot.command(name='o', help='Get the message associated with an exclusive tag')
async def exclusive_get_tag(ctx, tag):
    if ctx.author.id not in bot_bans:
        if tag in exclusive_tags:
            tag_info = exclusive_tags[tag]
            message = f'{tag_info["message"]}'
            try:
                if tag_info['embed']:
                    embed = discord.Embed(description=tag_info['embed'], color=discord.Color.red())
                    await ctx.send(content=message, embed=embed)
                else:
                    await ctx.send(message)
            except KeyError:
                await ctx.send(message)
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to add an exclusive tag
@bot.command(name='o_addtag', help='Add an exclusive tag with a message')
async def exclusive_add_tag(ctx, tag, *, message):
    if ctx.author.id not in bot_bans:
        if tag_creator_role_id in [role.id for role in ctx.author.roles]:
            if tag not in exclusive_tags:
                exclusive_tags[tag] = {'message': message, 'creator': ctx.author.id, 'type': 'exclusive'}
                save_exclusive_tags(exclusive_tags)
                await ctx.send(f'Tag `{tag}` added successfully!')
            else:
                await ctx.send(f'Tag `{tag}` already exists.')
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to get an exclusive tag
@bot.command(name='o_info', help='Get the message associated with an exclusive tag')
async def exclusive_get_tag_info(ctx, tag):
    if ctx.author.id not in bot_bans:
        if tag in exclusive_tags:
            tag_info = exclusive_tags[tag]
            message = f'Tag `{tag}`: {tag_info["message"]}\nCreated by: {tag_info["creator"]}\nType: {tag_info["type"]}'
            try:
                if tag_info['embed']:
                    embed = discord.Embed(description=tag_info['embed'], color=discord.Color.red())
                    await ctx.send(content=message, embed=embed)
                else:
                    await ctx.send(message)
            except KeyError:
                await ctx.send(message)
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to delete an exclusive tag
@bot.command(name='o_deltag', help='Delete an exclusive tag (can be deleted by the original creator or bot admins)')
async def exclusive_delete_tag(ctx, tag):
    if ctx.author.id not in bot_bans:
        if tag in exclusive_tags:
            tag_info = exclusive_tags[tag]
            if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
                del exclusive_tags[tag]
                save_exclusive_tags(exclusive_tags)
                await ctx.send(f'Tag `{tag}` deleted successfully!')
            else:
                await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to edit an exclusive tag (bot admin or tag owner only)
@bot.command(name='o_edittag', help='Edit an exclusive tag (bot admin or tag owner only)')
async def exclusive_edit_tag(ctx, tag, *, new_message):
    if ctx.author.id not in bot_bans:
        if tag in exclusive_tags:
            tag_info = exclusive_tags[tag]
            if ctx.author.id == tag_info['creator'] or ctx.author.id in bot_admins:
                exclusive_tags[tag]['message'] = new_message
                save_exclusive_tags(exclusive_tags)
                await ctx.send(f'Tag `{tag}` edited successfully!')
            else:
                await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
        else:
            await ctx.send(f'Tag `{tag}` not found.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to see the list of exclusive tags the user owns
@bot.command(name='o_mytags', help='See the list of exclusive tags you own')
async def exclusive_my_tags(ctx):
    if ctx.author.id not in bot_bans:
        user_id = ctx.author.id
        user_tags = {tag: tag_info for tag, tag_info in exclusive_tags.items() if tag_info['creator'] == user_id}
        
        if user_tags:
            tag_list = '\n'.join([f'`{tag}`' for tag in user_tags])
            await ctx.send(f'Your exclusive tags:\n{tag_list}')
        else:
            await ctx.send('You do not own any exclusive tags.')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to search for similar exclusive tags
@bot.command(name='o_searchtags', help='Search for similar exclusive tags')
async def exclusive_search_tags(ctx, keyword):
    if ctx.author.id not in bot_bans:
        similar_tags = find_similar_tags(exclusive_tags, keyword)
        
        if similar_tags:
            tag_list = '\n'.join([f'`{tag}`' for tag in similar_tags])
            await ctx.send(f'Similar exclusive tags for "{keyword}":\n{tag_list}')
        else:
            await ctx.send(f'No similar exclusive tags found for "{keyword}".')
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to embed or edit a message onto an exclusive tag
@bot.command(name='o_embedtag', help='Embed a message onto an exclusive tag or create a new tag with an embed')
async def exclusive_embed_tag(ctx, tag, *, embed_content):
    if ctx.author.id not in bot_bans:
        if tag_creator_role_id in [role.id for role in ctx.author.roles]:
            if tag in exclusive_tags:
                if ctx.author.id == exclusive_tags[tag]['creator'] or ctx.author.id in bot_admins:
                    exclusive_tags[tag]['embed'] = embed_content
                    save_exclusive_tags(exclusive_tags)
                    await ctx.send(f'Message embedded onto tag `{tag}` successfully!')
                else:
                    await ctx.send("Embed already exists and cannot be overriden")
            else:
                exclusive_tags[tag] = {'message': '', 'creator': ctx.author.id, 'type': 'exclusive', 'embed': embed_content}
                save_exclusive_tags(exclusive_tags)
                await ctx.send(f'New tag `{tag}` created with embedded message successfully!')
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

# Command to edit the embedded content of an exclusive tag
@bot.command(name='o_editembed', help='Edit the embedded content of an exclusive tag')
async def exclusive_edit_embed_tag(ctx, tag, *, embed_content):
    if ctx.author.id not in bot_bans:
        if tag in exclusive_tags:
            if ctx.author.id == exclusive_tags[tag]['creator'] or ctx.author.id in bot_admins:
                if 'embed' in exclusive_tags[tag]:
                    exclusive_tags[tag]['embed'] = embed_content
                    save_exclusive_tags(exclusive_tags)
                    await ctx.send(f'Embedded content of tag `{tag}` edited successfully!')
                else:
                    await ctx.send(f'Tag `{tag}` does not have embedded content. Use `%o_embedtag` to create a new tag with embedded content.')
            else:
                await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
        else:
            await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")
    else:
        await ctx.send("You are not allowed! https://media.discordapp.net/attachments/1184470853304459284/1184494309609836544/New_Microsoft_PowerPoint_Presentation_5.mp4")

#
# Chemistry
#

### STOICHEMISTRY
import re

async def stoik_command(ctx):
    try:
        def add_elements(elements, count, element, multiplier):
            if not count:
                count = "1"

            amount = int(count) * int(multiplier)

            if amount > 2**24:
                raise ValueError(f"{amount} is too large of a number")

            elements.extend([element] * amount)

        def multiply_elements(elements, multiplier):
            return [(symbol, count * int(multiplier)) for symbol, count in elements]

        def parse_chemical(formula, multiplier="1"):
            formula = formula.replace(" ", "")
            elements = []
            count = ""
            symbol = ""
            i = 0

            while i < len(formula):
                char = formula[i]

                if char.isnumeric():
                    count += char
                elif char.isupper():
                    if count:
                        elements.append((symbol, int(count) * int(multiplier)))
                        count = ""
                    symbol = char

                    if i + 1 < len(formula) and formula[i + 1].islower():
                        symbol += formula[i + 1]
                        i += 1
                elif char == "(":
                    j = i - 1
                    while j >= 0 and formula[j].isdigit():
                        count = formula[j] + count
                        j -= 1

                    left_number = int(count) if count else 1

                    count = ""
                    j = i + 1
                    while j < len(formula) and formula[j].isdigit():
                        count += formula[j]
                        j += 1

                    paren_coefficient = int(count) if count else 1

                    subchem_end = formula.find(")", j)
                    if subchem_end == -1:
                        raise ValueError("Unmatched parentheses in the formula")

                    subchem = formula[j:subchem_end]
                    subchem_parsed = parse_chemical(subchem, str(left_number * paren_coefficient))
                    elements.extend(multiply_elements(subchem_parsed, multiplier))

                    i = subchem_end + 1

                    # Check for a number following ")"
                    count = ""
                    while i < len(formula) and formula[i].isdigit():
                        count += formula[i]
                        i += 1

                    post_paren_number = int(count) if count else 1
                    multiplier = int(multiplier) * post_paren_number

                    continue

                i += 1

            if count:
                elements.append((symbol, int(count) * int(multiplier)))

            return elements

        formula_str = None
        try:
            split_formula = ctx.message.content.split(" ")
            formula_str = " ".join(split_formula[1:])
        except Exception as e:
            return f"No formula supplied {str(e)}"

        formula_str = formula_str.replace("`", "")
        formula_str = formula_str.replace("=", "->")
        formula_str = formula_str.replace(" ", "")

        formula_sides = formula_str.split("->")
        if len(formula_sides) != 2:
            return """
                    Error, malformed expression
                    Please format equation as `Reactant1 + Reactant2 -> Product1 + Product2`
                    E.g. `6CO2 + 6H2O -> C6H12O6 + 6O2`
                    FYI spaces are stripped
                    """

        reactants = []
        for formula in formula_sides[0].split("+"):
            try:
                reactants.extend(parse_chemical(formula))
            except ValueError as e:
                return f"Formula `{formula}` has an error: {str(e)}"

        products = []
        for formula in formula_sides[1].split("+"):
            try:
                products.extend(parse_chemical(formula))
            except ValueError as e:
                return f"Formula `{formula}` has an error: {str(e)}"

        reactants = [elem for elem in reactants if elem]
        products = [elem for elem in products if elem]

        reactants_map = {}
        products_map = {}

        for element in reactants:
            reactants_map[element] = reactants_map.get(element, 0) + 1

        for element in products:
            products_map[element] = products_map.get(element, 0) + 1

        reactants_str_builder = ["```"]
        products_str_builder = ["```"]
        clay_str_builder = ["```"]
        balanced = True

        element_keys = sorted(set(products_map.keys()).union(reactants_map.keys()))
        for element in element_keys:
            if products_map.get(element, -1) == reactants_map.get(element, -1):
                clay_str_builder.append("✅✅")
            else:
                clay_str_builder.append("❌❌")
                balanced = False

            products_str_builder.append(f"{element}:  {products_map.get(element, 0)}\n")
            reactants_str_builder.append(f"{element}:  {reactants_map.get(element, 0)}\n")

            clay_str_builder.append("\n")

        clay_str_builder.append("```")
        reactants_str_builder.append("```")
        products_str_builder.append("```")
        balanced_msg = "\u2705 Your reaction is balanced \u2705" if balanced else "\u274C Your reaction is unbalanced \u274C"

        return {
            "Reactants": "".join(reactants_str_builder),
            "Products": "".join(products_str_builder),
            "Balanced": "".join(clay_str_builder),
            "Status": balanced_msg,
        }

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Define the stoik command
@bot.command(name='stoik', help='Check whether a chemical equation is balanced')
async def stoik(ctx):
    try:
        result = await stoik_command(ctx)
        embed = discord.Embed(title="Chemical Equation Balancer", color=0x00ff00)
        embed.add_field(name="Reactants", value="".join(result["Reactants"]), inline=True)
        embed.add_field(name="Products", value="".join(result["Products"]), inline=True)
        embed.add_field(name="Balanced", value="".join(result["Balanced"]), inline=True)
        embed.add_field(name="Status", value=result["Status"], inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

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
        inclusive_dump_content = json.dumps(inclusive_tags, indent=4)
        with open('inclusive_tags_dump.json', 'w') as file:
            file.write(inclusive_dump_content)

        exclusive_dump_content = json.dumps(exclusive_tags, indent=4)
        with open('exclusive_tags_dump.json', 'w') as file:
            file.write(exclusive_dump_content)

        await ctx.send(files=[
            discord.File('inclusive_tags_dump.json', 'inclusive_tags_dump.json'),
            discord.File('exclusive_tags_dump.json', 'exclusive_tags_dump.json')
        ])
    else:
        await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")


# Command for emergency shutdown (bot owner only)
@bot.command(name='emergency_shutdown', help='Emergency shutdown (bot owner only)')
async def emergency_shutdown(ctx):
    if ctx.author.id == bot_owner_id:
        await ctx.send('Emergency shutdown initiated. Goodbye!')
        sys.exit()
    else:
        await ctx.send("https://cdn.discordapp.com/attachments/708645871994273803/944593955872469052/Z.png")

# Event when the bot is ready
@bot.event
async def on_ready():
    global inclusive_tags, exclusive_tags
    inclusive_tags = load_inclusive_tags()
    exclusive_tags = load_exclusive_tags()
    print(f'Logged on as {bot.user}!')

# Event when a message is received
@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    bot_prefix = '%'
    if any(char in message.content for char in bot_prefix):
        # Check if the message content contains characters that might break JSON code formatting
        invalid_characters = ['{', '[', ']', '}', '"', "'", '\\', '...']  # Add more if needed

        if any(char in message.content for char in invalid_characters):
            await message.channel.send("Invalid characters detected. The command contains characters that might break JSON code formatting.")
            return

        await bot.process_commands(message)  # Process commands in on_message
        return

bot.run(bot_token)

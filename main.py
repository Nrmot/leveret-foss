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
from chempy import Substance
import re

import re
from chempy import Substance


class StoikFormulaParser:
    def __init__(self, equation):
        self.equation = equation
        self.reactants, self.products = self.equation.split('->')
        self.reactant_components = []
        self.product_components = []

    def parse_formula(self, formula):
        composition = {}
        regex = re.compile(r'(?P<element>[A-Z][a-z]*)(?P<count>\d*)')

        # Iterate over matches in the formula
        for match in regex.finditer(formula):
            element = match.group('element')
            count = match.group('count')
            count = int(count) if count else 1  # If count is not specified, assume 1
            composition[element] = count

        # Check for parentheses and '^' symbol
        if '(' in formula and ')' in formula:
            # Extract the content inside the parentheses
            inside_parentheses = re.search(r'\(([^)]+)\)', formula).group(1)
            inside_parentheses_count = 1

            # Check for '^' symbol and get the count
            if '^' in formula:
                inside_parentheses_count = int(formula.split('^')[-1])

            # Parse the content inside parentheses and multiply by the count
            inside_parentheses_substance = self.parse_formula(inside_parentheses)
            for element, count in inside_parentheses_substance.composition.items():
                composition[element] = count * inside_parentheses_count

        # Create a Substance object and set its composition
        chempy_substance = Substance(formula)
        chempy_substance.composition = composition

        return chempy_substance

    def parse_equation(self):
        reactants_list = [self.parse_formula(compound.strip()) for compound in self.reactants.split('+')]
        products_list = [self.parse_formula(compound.strip()) for compound in self.products.split('+')]

        return reactants_list, products_list

    def display_components(self, components, part_name):
        print(f"{part_name} Components:")
        for component_dict in components:
            print(component_dict)

    def process_components(self, components, component_list, level=0):
        part_components = {}
        for element, count in components.items():
            if element in part_components:
                part_components[element] += count
            else:
                part_components[element] = count

        # Add the components to the list at the corresponding level
        if len(component_list) <= level:
            component_list.append([])
        component_list[level].append(part_components)

        # Check for parentheses multiplication within the current level
        for element, count in part_components.items():
            if isinstance(count, dict):
                self.process_components(count, component_list, level + 1)

    def calculate_components(self):
        reactants_list, products_list = self.parse_equation()

        # Process reactants components
        for reactant in reactants_list:
            self.process_components(reactant.composition, self.reactant_components)

        # Process products components
        for product in products_list:
            self.process_components(product.composition, self.product_components)

        # Display the final components
        self.display_components(self.reactant_components, "Reactant")
        self.display_components(self.product_components, "Product")

        # Calculate and display the total sum of reactants and products
        total_reactant_sum = {}
        total_product_sum = {}

        for level_components in self.reactant_components:
            for components in level_components:
                for element, count in components.items():
                    if element in total_reactant_sum:
                        total_reactant_sum[element] += count
                    else:
                        total_reactant_sum[element] = count

        for level_components in self.product_components:
            for components in level_components:
                for element, count in components.items():
                    if element in total_product_sum:
                        total_product_sum[element] += count
                    else:
                        total_product_sum[element] = count

        # Return the calculated sums instead of printing
        return total_reactant_sum, total_product_sum

@bot.command(name='stoik', help=
             """Check if your equation is balanced.

                Examples:
                %stoik (C4E5)^4 + C6E13 -> (C2E3)^11
                In here we use ^ to seperate (C4E5)^4
                Note that %chem_stoik (C4E5)^4C6E13 -> (C2E3)^11 does not work
                Incase an error is thrown""")
async def stoik_command(ctx, *, chemical_equation):
    try:
        stoik_formula_parser = StoikFormulaParser(chemical_equation)
        total_reactant_sum, total_product_sum = stoik_formula_parser.calculate_components()

        # Check if the equation is balanced
        equation_balanced = total_reactant_sum == total_product_sum

        # Format the results as a Discord message
        result_message = (
            f"## Your Results:\n"
            f"```Total Sum of Reactants:\n{total_reactant_sum}\n\nTotal Sum of Products:\n{total_product_sum}```\n"
            f"{'Your Equation Was Balanced.' if equation_balanced else 'Your Equation is not balanced, or it may be too complicated.'}\n"
            f"You can also try checking https://www.webqc.org/balance.php incase this simple stoik command does not satisfy your query.\n"
            f"Try %stoik (C4E5)^4 + C6E13 -> (C2E3)^11"
        )

        # Send the results back to the Discord channel
        await ctx.send(result_message)

    except Exception as e:
        result_message = (
            f"!!! ERROR ALERT !!!\n"
            f"Try reformatting your query, do %help stoik\n"
            f"!!! REPORT ALL ISSUES TO THE BOT DEVELOPER.\n"
            f"Error: {e}\n"
            f"Try checking https://www.webqc.org/balance.php if your equation is very advanced."
        )
        await ctx.send(result_message)

# Gas Laws
# Define commands for each gas law
@bot.command(name='cgl_boyle', help='Calculate Boyle\'s Law. Provide any two of the three variables (P, V, k).')
async def boyle(ctx, p: float = None, v: float = None, k: float = None):
    if p is not None and v is not None:
        k = p * v
        await ctx.send(f'Boyle\'s Law: PV = {k}')
    elif p is not None and k is not None:
        v = k / p
        await ctx.send(f'Boyle\'s Law: V = {v}')
    elif v is not None and k is not None:
        p = k / v
        await ctx.send(f'Boyle\'s Law: P = {p}')
    else:
        await ctx.send('Invalid input. Provide at least two variables.')

@bot.command(name='cgl_charles', help='Calculate Charles\'s Law. Provide any two of the three variables (V, T, k).')
async def charles(ctx, v: float = None, t: float = None, k: float = None):
    if v is not None and t is not None:
        k = v * t
        await ctx.send(f'Charles\'s Law: VT = {k}')
    elif v is not None and k is not None:
        t = k / v
        await ctx.send(f'Charles\'s Law: T = {t}')
    elif t is not None and k is not None:
        v = k / t
        await ctx.send(f'Charles\'s Law: V = {v}')
    else:
        await ctx.send('Invalid input. Provide at least two variables.')

@bot.command(name='cgl_gaylussac', help='Calculate Gay-Lussac\'s Law. Provide any two of the three variables (P, T, k).')
async def gaylussac(ctx, p: float = None, t: float = None, k: float = None):
    if p is not None and t is not None:
        k = p * t
        await ctx.send(f'Gay-Lussac\'s Law: PT = {k}')
    elif p is not None and k is not None:
        t = k / p
        await ctx.send(f'Gay-Lussac\'s Law: T = {t}')
    elif t is not None and k is not None:
        p = k / t
        await ctx.send(f'Gay-Lussac\'s Law: P = {p}')
    else:
        await ctx.send('Invalid input. Provide at least two variables.')

@bot.command(name='cgl_avogadro', help='Calculate Avogadro\'s Law. Provide any two of the three variables (V, N, k).')
async def avogadro(ctx, v: float = None, n: float = None, k: float = None):
    if v is not None and n is not None:
        k = v * n
        await ctx.send(f'Avogadro\'s Law: VN = {k}')
    elif v is not None and k is not None:
        n = k / v
        await ctx.send(f'Avogadro\'s Law: N = {n}')
    elif n is not None and k is not None:
        v = k / n
        await ctx.send(f'Avogadro\'s Law: V = {v}')
    else:
        await ctx.send('Invalid input. Provide at least two variables.')

@bot.command(name='cgl_idealgas', help='Calculate Ideal Gas Law. Provide all four variables (P, V, n, T).')
async def idealgas(ctx, p: float = None, v: float = None, n: float = None, t: float = None, r: float = 8.314):
    if p is not None and v is not None and n is not None and t is not None:
        k = p * v / (n * r * t)
        await ctx.send(f'Ideal Gas Law: PV = nRT, k = {k}')
    else:
        await ctx.send('Invalid input. Provide all variables (P, V, n, T).')

@bot.command(name='cgl_dalton', help='Calculate Dalton\'s Law. Provide pressures for each gas.')
async def dalton(ctx, *pressures: float):
    total_pressure = sum(pressures)
    await ctx.send(f'Dalton\'s Law: P_total = {total_pressure}')

# Physics

# Define a function to calculate Schrödinger's equation
def calculate_schrodingers_equation(equation):
    t, x, psi = sp.symbols('t x Psi', real=True)
    i = sp.I  # imaginary unit
    h_bar = sp.symbols('h_bar', positive=True, real=True)  # Planck's reduced constant

    # Define the time-dependent Schrödinger's equation
    schrodingers_equation = sp.Eq(sp.I * h_bar * sp.diff(psi, t), -h_bar**2 / (2 * sp.pi**2 * sp.m**2) * sp.diff(psi, x, x))

    # Solve the equation
    solution = sp.dsolve(schrodingers_equation, psi)

    return solution

# Define a command to calculate time-dependent Schrödinger's equation
@bot.command()
async def time_dependent(ctx):
    equation = calculate_schrodingers_equation("time-dependent")
    await ctx.send(f"Time-dependent Schrödinger's equation solution:\n```{equation}```")

# Define a command to calculate time-independent Schrödinger's equation
@bot.command()
async def time_independent(ctx):
    equation = calculate_schrodingers_equation("time-independent")
    await ctx.send(f"Time-independent Schrödinger's equation solution:\n```{equation}```")
    
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
    # Check if the message contains the :Greg: emoji
    # Define the emojis
    greg_emoji = '<:Greg:1142725256897904651>'
    fear_of_god_emoji = '<:fearofgod:1147324806337937448>'

    # Check if the message contains specific keywords
    # Define the emojis
    greg_emoji = '<:Greg:1142725256897904651>'
    fear_of_god_emoji = '<:fearofgod:1147324806337937448>'

    # Check if the message contains specific keywords
    keywords = [":Greg:", "Greg", "greg", "GT"]
    reaction_emoji = greg_emoji if any(keyword in message.content for keyword in keywords) else None

    keywords2 = ["Ungreggy", "Acidic", "Bullshit", ":tci:"]
    reaction_emoji2 = fear_of_god_emoji if any(keyword in message.content for keyword in keywords2) else None

    if reaction_emoji:
        channel = message.channel
        await message.add_reaction(reaction_emoji)
    elif reaction_emoji2:
        channel = message.channel
        await message.add_reaction(reaction_emoji2)

    print(f'Message from {message.author}: {message.content}')
    bot_prefix = '%'
    await bot.process_commands(message)  # Process commands in on_message
    """
    if any(char in message.content for char in bot_prefix):
        # Check if the message content contains characters that might break JSON code formatting
        invalid_characters = ['{', '[', ']', '}', '"', "'", '\\', '...']  # Add more if needed

        if any(char in message.content for char in invalid_characters):
            await message.channel.send("Invalid characters detected. The command contains characters that might break JSON code formatting.")
            return
        await bot.process_commands(message)  # Process commands in on_message
        return
    """
    
bot.run(bot_token)

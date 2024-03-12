import asyncio
import nsverify
import discord
import os
import sqlite3
import aiohttp
import backuping
import welcoming
import recruitment
import nsstats
from discord.ext import commands
from discord.ext.commands import has_permissions, has_role, is_owner
from discord.ui import Button, View
from dotenv import load_dotenv
import time


#################### BOT SETUP ####################

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class Bot(commands.Bot):
    def __init__(self, intents:discord.Intents):
        super().__init__(command_prefix="!", intents=intents, case_sensitive=True)

    async def on_ready(self):
        print("ready")

intents = discord.Intents.all()
bot = Bot(intents=intents)

#################### REGULAR - ADMIN - COMMANDS ####################
@bot.command(name="sync", description="syncs the server with the bot's slash commands")
async def regular_command(ctx: commands.Context):
    await ctx.reply("Syncing...")
    await bot.tree.sync()
    print("Bot synced with server")
    await ctx.send("Synced")

@bot.command(name="sleep", description="Shuts down the bot")
async def regular_command(ctx: commands.Context):
    await ctx.reply("Shutting down...")
    print("Command: Shutting down")
    await bot.close()

# Temp deprecated following move to sqlite3 databases
# @bot.command(name="backup", description="Backup the JSON files")
# async def regular_command(ctx: commands.Context):
#     backuping.backup()
#     await ctx.reply("Backup done")

@bot.event
async def on_disconnect():
    # Close the aiohttp session when the bot disconnects
    connector = bot.http.connector
    if connector:
        await connector.close()
        print("Closed aiohttp connector.")

#################### SLASH - ADMIN - COMMANDS ####################
# Temp deprecated following move to sqlite3 databases
# @bot.tree.command(name="empty_region_file", description="Empty the JSON file of a region")
# async def empty_region_file(ctx, region: str):
#     nsverify.empty_json(region)
#     await ctx.response.send_message(f"Emptied the JSON file of {region}")

#################### REGULAR - HELP - COMMANDS ####################
@bot.command(name="help_noslash", description="Get help")
async def help_noslash(ctx):
    embed = discord.Embed(
        title="Help Menu",
        description="Lists all of Léman's commands",
        color=0xeda7c8
    )
    embed.add_field(
        name="Sync",
        value="Used one time when adding the bot to the server, necessary to make slash commands work. You **must** use the '!' prefix with it."
    )
    embed.add_field(
        name="Verify",
        value="Verify if you are the owner of the specified nation"
    )
    embed.add_field(
        name="Verify_auto",
        value="Same command as /verify but for regions with an autorole system linked to a user's nationstates nation."
    )
    embed.add_field(
        name="Stv_calculate",
        value="Calculate the results of an election using the single transferrable vote system, requires a [TBD] in input."
    )
    embed.set_footer(text="Bot made by @Altys")
    await ctx.reply(embed=embed)

#################### SLASH - HELP - COMMANDS ####################
@bot.tree.command(name="help", description="Get help")
async def help(ctx):
    embed = discord.Embed(
        title="Help Menu",
        description="Lists all of Léman's commands",
        color=0xeda7c8
    )
    embed.add_field(
        name="Sync",
        value="Used one time when adding the bot to the server, necessary to make slash commands work. You **must** use the '!' prefix with it."
    )
    embed.add_field(
        name="Verify",
        value="Verify if you are the owner of the specified nation"
    )
    embed.add_field(
        name="Verify_auto",
        value="Same command as /verify but for regions with an autorole system linked to a user's nationstates nation."
    )
    embed.add_field(
        name="Stv_calculate",
        value="Calculate the results of an election using the single transferrable vote system, requires a [TBD] in input."
    )
    embed.set_footer(text="Bot made by @Altys")
    await ctx.response.send_message(embed=embed)

#################### SLASH - Verify - COMMANDS ####################
@bot.tree.command(name="verify", description="Verify your nation")
async def verify(ctx, nation: str, key: str):
    if nsverify.verify_nation(nation, key):
        await ctx.response.send_message("Verified")
    else:
        await ctx.response.send_message("Not verified")

@bot.tree.command(name="verify_auto", description="Verify your nation to automatically get roled in the server")
async def verify_auto(interaction, nation: str):
    user = interaction.user  # Get the discord.User object from the interaction
    if discord.utils.get(user.roles, name="Verified"):
        await interaction.response.send_message("You are already verified on this server. Please contact a moderator if you need help.")
    else:
        await interaction.response.send_message("I have sent you a DM! If you have not received any, make sure you have enabled DMs from server members.")

        await user.send("Please enter your nation verification key which can be found here: https://www.nationstates.net/page=verify_login")
        key = await bot.wait_for('message', check=lambda message: message.author == user and isinstance(message.channel, discord.DMChannel))

        if key.content == "cancel":
            await user.send("Cancelled")
            return
        print(f"nation:{nation} key:{key.content} are being tested")

        if nsverify.verify_nation(nation, key.content):
            await user.send("Verified")
            region = nsverify.nation_in_region(user, nation, None)
            server = interaction.guild  # Assuming you have the server (guild) available
            role = discord.utils.get(server.roles, name=region)
            if role:
                await interaction.user.add_roles(role)
        else:
            await user.send("Not verified")

        print("done")

@bot.tree.command(name="change_nation", description="Change the nation of an already verified user")
async def change_nation(ctx, user: str, nation: str, region: str):
    nsverify.change_user_nation(user, nation, region)
    await ctx.response.send_message(f"Changed the nation of {user} to {nation}")

@bot.tree.command(name="checkup", description="Updates the list of nations in a region")
async def checkup(ctx, region: str):
    removed_nations, removed_count = nsverify.region_checkup(region)
    message = f"Removed {removed_count} nations: {removed_nations}\n"

    server = ctx.guild
    role = discord.utils.get(server.roles, name=region)
    db_path = "./Regions/Regions.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute("SELECT nations_list FROM regions WHERE region = ?", (region,))
        result = c.fetchone()
        if result:
            nations_list = result[0]
        else:
            nations_list = {}
    except sqlite3.Error:
        nations_list = {}
    finally:
        conn.close()

    members_with_role = [member.id for member in ctx.guild.members if role in member.roles]

    for member_id in members_with_role:
        if str(member_id) not in nations_list:
            member = ctx.guild.get_member(member_id)
            if member:
                await member.remove_roles(role)
                print(f"Removed role '{role.name}' from user {member}")

    message += "\nUpdate completed."
    await ctx.response.send_message(message)

#################### SLASH - Government - COMMANDS ####################
@bot.tree.command(name="stv_calculate", description="Calculate the results of an STV election")
async def stv_calculate(ctx, election: str):
    member = ctx.user # Use ctx.user to get the user who triggered the interaction
    if ctx.guild.get_role(605880071936278568) in member.roles:
        await ctx.response.send_message("Calculating...")
    else:
        await ctx.response.send_message("You do not have the required role")

#################### SLASH - Welcome - COMMANDS ####################
@bot.tree.command(name="welcome", description="Generate your region's welcome message")
async def welcome(ctx, region: str):
    message = welcoming.create_welcome_message(region)
    if message:
        await ctx.response.send_message(message)
    else:
        await ctx.response.send_message("No new nations to welcome!")
        print("Error: Empty message")

@bot.tree.command(name="set_welcome_message", description="Set the welcome message for a region")
async def set_region_welcome_message(ctx, region: str, message: str):
    try:
        await ctx.response.send_message("I will ask you in DMs to prove you are a nation holding communications authority in your region.")
        await ctx.user.send("Please send your nation name here")
        
        nation = await bot.wait_for('message', check=lambda m: m.author == ctx.user and isinstance(m.channel, discord.DMChannel), timeout=60)
        nation_name = nation.content.strip()

        await ctx.user.send("Please enter your nation verification key which can be found here: https://www.nationstates.net/page=verify_login")
        key = await bot.wait_for('message', check=lambda m: m.author == ctx.user and isinstance(m.channel, discord.DMChannel), timeout=60)
        verification_key = key.content.strip()

        if nsverify.is_member(region, nation):
            await set_region_welcome_message_bis(ctx, region, message, nation_name)
        elif nsverify.verify_nation(nation_name, verification_key):
            await set_region_welcome_message_bis(ctx, region, message, nation_name)
        else:
            await ctx.channel.send("Not verified, you cannot set the welcome message")
    
    except asyncio.TimeoutError:
        await ctx.channel.send(f"<@{ctx.user.id}> Time ran out. Please run the command again.")


async def set_region_welcome_message_bis(ctx, region: str, message: str, nation_name: str):
    if welcoming.verify_communications_authority(region, nation_name):
        await ctx.channel.send("Verified, setting the welcome message...")
        if welcoming.set_welcome_message(region, message):
            await ctx.channel.send("Welcome message set")
        else:
            await ctx.channel.send("Your welcome message does not possess the '[NATIONS]' operator. Please only use this command if you wish to automate welcome message generation, not store messages.")
    else:
        await ctx.channel.send(f"<@{ctx.user.id}> You are not an officer with Communications Authority, you cannot set the welcome message")

#################### SLASH - Recruitment - COMMANDS ####################
@bot.tree.command(name="exclude_region", description="Exclude a region from the recruitment process")
async def exclude_region(ctx, your_region: str, region_to_exclude: str):
    if recruitment.exclude_regions(your_region, region_to_exclude) == False:
        await ctx.response.send_message(f"Excluded {region_to_exclude} from the recruitment process")
    else:
        await ctx.response.send_message(f"{region_to_exclude} is already excluded from the recruitment process")

@bot.tree.command(name="recruit", description="Recruit new nations")
async def recruit(ctx, region: str):
    new_nations = recruitment.recruit_new_nations(region, ctx.user.id)
    new_nations_str = ""
    if new_nations != "NOTEMPLATE" and new_nations != None:
        for i in range (len(new_nations)):
            new_nations_str += new_nations[i]
            new_nations_str += '\n\n'
        if len(new_nations_str) > 2000:
            await ctx.channel.send("Too many new nations to recruit, separating into multiple messages...")
            new_nations_list = new_nations_str.split('\n\n')
            for i in range(len(new_nations_list)):
                if (new_nations_list[i] != ""):
                    await ctx.channel.send(new_nations_list[i])
        await ctx.response.send_message(new_nations_str)
    elif new_nations == "NOTEMPLATE":
        await ctx.response.send_message("You did not set a telegram template. Please use the ``/set_template`` function to do so.")
    else:
        await ctx.response.send_message("No new nations to recruit.")

@bot.tree.command(name="recruit_session", description="Start a recruitment session for a region")
async def recruit_session(ctx, region: str, call_wait: int):
    start_time = time.perf_counter()
    await ctx.response.send_message(f"Recruitment session started for {region}.")
    while True:
        elapsed_time = time.perf_counter() - start_time
        remaining_time = call_wait * 60 - elapsed_time

        if elapsed_time >= call_wait * 60:
            new_nations = recruitment.recruit_new_nations(region, ctx.user.id)
            print(new_nations)
            new_nations_str = ""
            if new_nations != "NOTEMPLATE" and new_nations != None:
                for i in range(len(new_nations)):
                    new_nations_str += new_nations[i]
                    new_nations_str += '\n\n'
                if len(new_nations_str) > 2000:
                    await ctx.channel.send("Too many new nations to recruit, separating into multiple messages...")
                    new_nations_list = new_nations_str.split('\n\n')
                    for i in range(len(new_nations_list)):
                        await ctx.channel.send(new_nations_list[i])
                await ctx.channel.send(new_nations_str)
            elif new_nations == "NOTEMPLATE":
                await ctx.channel.send("You did not set a telegram template. Please use the ``/set_template`` function to do so.")
            else:
                await ctx.channel.send("No new nations to recruit.")
            start_time = time.perf_counter()
            remaining_time = call_wait * 60

        await asyncio.sleep(min(remaining_time, 1))

@bot.tree.command(name="set_template", description="Set the telegram template for the recruitment process")
async def set_template(ctx, template: str):
    recruitment.store_template(template, ctx.user.id)
    await ctx.response.send_message("Template set")

#################### SLASH - NSStats - COMMANDS ####################
@bot.tree.command(name="lausanne_votes", description="Get the power of the delegates in the Lausanne Alliance")
async def lausanne_votes(ctx):
    await ctx.response.send_message("Getting the power of the delegates in the Lausanne Alliance...")
    try:
        votes = nsstats.get_lausanne_delegates_power()
        await ctx.channel.send(votes)
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.channel.send("An error occurred, please check console logs")


# @bot.tree.command(name="update_govt_overview", description="Update the government overview")
# async def update_govt_overview(ctx, prime_minister: str, world_assembly_delegate: str, domestic_affairs_minister: str, foreign_affairs_minister: str, legal_affairs_minister: str, cultural_affairs_minister: str, defence_minister: str, secretary_of_integration: str, secretary_of_gameside: str, secretary_of_media: str, secretary_of_roleplay: str, deputy_prime_minister: str, vice_delegate: str, deputy_domestic_affairs_minister: str, deputy_foreign_affairs_minister: str, deputy_legal_affairs_minister: str, deputy_cultural_affairs_minister: str, deputy_defence_minister: str):
#     member = ctx.user
#     print("Updating government overview...")

bot.run(TOKEN)
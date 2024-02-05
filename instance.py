import nsverify
import discord
import os
import json
import aiohttp
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import has_role
from discord.ext.commands import is_owner
from dotenv import load_dotenv


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
@has_permissions(administrator=True)
async def regular_command(ctx: commands.Context):
    await ctx.reply("Syncing...")
    await bot.tree.sync()
    print("Bot synced with server")
    await ctx.send("Synced")

@bot.command(name="sleep", description="Shuts down the bot")
@has_permissions(administrator=True)
async def regular_command(ctx: commands.Context):
    await ctx.reply("Shutting down...")
    print("Command: Shutting down")
    await bot.close()

@bot.event
async def on_disconnect():
    # Close the aiohttp session when the bot disconnects
    connector = bot.http.connector
    if connector:
        await connector.close()
        print("Closed aiohttp connector.")

#################### SLASH - ADMIN - COMMANDS ####################
@bot.tree.command(name="empty_region_file", description="Empty the JSON file of a region")
@is_owner()
async def empty_region_file(ctx, region: str):
    nsverify.empty_json(region)
    await ctx.response.send_message(f"Emptied the JSON file of {region}")

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

@bot.tree.command(name="checkup", description="Updates the list of nations in a region")
@has_permissions(administrator=True)
async def checkup(ctx, region: str):
    removed_nations, removed_count = nsverify.checkup(region)
    await ctx.response.send_message(f"Removed {removed_count} nations: {removed_nations}")
    await ctx.response.send_message(f"Updating the amount of people holding the role for {region}...")

    server = ctx.guild
    role = discord.utils.get(server.roles, name=region)
    superregion = nsverify.get_superregion(region)

    if superregion is not None:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{superregion}/{region}.json"
    else:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{region}.json"

    try:
        with open(filepath, "r") as json_file:
            nations_list = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        nations_list = {}

    members_with_role = [member.id for member in ctx.guild.members if role in member.roles]

    for member_id in members_with_role:
        if str(member_id) not in nations_list:
            member = ctx.guild.get_member(member_id)
            if member:
                await member.remove_roles(role)
                print(f"Removed role '{role.name}' from user {member}")

    await ctx.response.send_message(f"Update completed.")

#################### SLASH - Government - COMMANDS ####################
@bot.tree.command(name="stv_calculate", description="Calculate the results of an STV election")
@has_role(605880071936278568)
async def stv_calculate(ctx, election: str):
    member = ctx.user # Use ctx.user to get the user who triggered the interaction
    if ctx.guild.get_role(605880071936278568) in member.roles:
        await ctx.response.send_message("Calculating...")
    else:
        await ctx.response.send_message("You do not have the required role")

# @bot.tree.command(name="update_govt_overview", description="Update the government overview")
# async def update_govt_overview(ctx, prime_minister: str, world_assembly_delegate: str, domestic_affairs_minister: str, foreign_affairs_minister: str, legal_affairs_minister: str, cultural_affairs_minister: str, defence_minister: str, secretary_of_integration: str, secretary_of_gameside: str, secretary_of_media: str, secretary_of_roleplay: str, deputy_prime_minister: str, vice_delegate: str, deputy_domestic_affairs_minister: str, deputy_foreign_affairs_minister: str, deputy_legal_affairs_minister: str, deputy_cultural_affairs_minister: str, deputy_defence_minister: str):
#     member = ctx.user
#     print("Updating government overview...")

bot.run(TOKEN)
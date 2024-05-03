# Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
  - [Programming Language](#programming-language)
  - [Discord Libraries](#discord-libraries)
  - [External Libraries](#external-libraries)
  - [Time Handling](#time-handling)
  - [NationStates API](#nationstates-api)
  - [Web Requests](#web-requests)
  - [XML Parsing](#xml-parsing)
  - [Other](#other)
- [Usage](#usage)
  - [Owner/Admin Commands](#owneradmin-commands)
  - [Regular Commands](#regular-commands)
  - [NationStates Verify](#nationstates-verify)
  - [Government Commands](#government-commands)
  - [Welcome Commands](#welcome-commands)
  - [Recruitment Commands](#recruitment-commands)
  - [Lausanne Commands](#lausanne-commands)

# Léman
## _Discord Bot for Nationstates_

Léamn is a Discord Bot coded in Python whose primary aim is to facilitate everyday tasks carried out by communities present on the [NationStates](https://www.nationstates.net) site.

This is a side project to those done during my Epitech curriculum.

## Features

- Information commands related to NationStates (checking a nation, region, etc.)
- Welcome message automatically adding newly arrived nations to a region
- Nation Verification with an optional autorole system
- Manual recruitment assistance (fetching newly founded nations and creating a telegram link)
- Election calculator (single-transferable vote and instant run-off voting systems)
- [World Assembly](https://www.nationstates.net/page=un) tools to empower your region's WA Culture

## Technologies Used

### Programming Language
- Python

### Discord Libraries
- [discord.py](https://discordpy.readthedocs.io/) - A Python library for interacting with the Discord API.

### External Libraries
- [aiohttp](https://docs.aiohttp.org/) - An asynchronous HTTP client/server framework for asyncio.
- [python-dotenv](https://github.com/theskumar/python-dotenv) - For loading environment variables from a .env file so as to hide secret information related to the Bot.

### Time Handling
- [datetime](https://docs.python.org/3/library/datetime.html) - Python's built-in library for date and time handling.

### NationStates API
- [NationStates API](https://www.nationstates.net/pages/api.html) - Used to retrieve informationr relative to NationStates.

### Web Requests
- [requests](https://docs.python-requests.org/) - A popular HTTP library for making requests, needed to interact with o the NationStates API.

### XML Parsing
- [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html) - Python's built-in library for parsing XML, which is the format NationStates' API responses use.

### SQLite Database
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) - Python's built-in library for interacting with SQLite databases.

### Other
- [asyncio](https://docs.python.org/3/library/asyncio.html) - For handling asynchronous code, necessary when coding bots in Python.

## Usage

### Owner/Admin Commands

- **Sync**
  - Description: Syncs the server with the bot's slash commands in case they do not appear.
  - Permissions: Administrator
  - Usage: `!sync`

- **Sleep**
  - Description: Shuts down the bot.
  - Owner Only
  - Usage: `!sleep`

- **Backup**
  - Description: Backup the SQLite databases.
  - Owner Only
  - Usage: `!backup`

- **Empty Region File**
  - Description: Empty the SQLite database of a region.
  - Owner Only
  - Usage: `/empty_region_file [region]`

### Regular Commands

- **Help**
  - Description: Display the bot's help menu.
  - Usage: `/help`

### NationStates Verify

- **Verify**
  - Description: Verify your nation.
  - Usage: `/verify [nation] [key]`

- **Verify Auto**
  - Description: Verify your nation to automatically get roled in the server.
  - Usage: `/verify_auto [nation]`

- **Change Nation**
  - Description: Change the nation of an already verified user.
  - Permissions: Manage Roles
  - Usage: `/change_nation [user] [nation] [region]`

- **Checkup**
  - Description: Updates the list of nations in a region.
  - Permissions: Administrator
  - Usage: `/checkup [region]`

### Government Commands

- **STV Calculate**
  - Description: Calculate the results of an STV election.
  - Requires Role: "Government"
  - Usage: `/stv_calculate [election]`

### Welcome Commands

- **Welcome**
  - Description: Generate your region's welcome message.
  - Usage: `/welcome [region]`

- **Set Welcome Message**
  - Description: Set the welcome message for a region.
  - Usage: `/set_welcome_message [region] [message]`
  - Note: DM interactions required for Communications Authority (in a NationStates region) verification.

### Recruitment Commands

- **Exclude Region**
  - Description: Exclude a region from the recruitment process of your region.
  - Permissions: Recruiter role
  - Usage: `/exclude_region [your_region] [region_to_exclude]`

- **Recruit**
  - Description: Recruit new nations for your region.
  - Permissions: Recruiter role
  - Usage: `/recruit [region]`

- **Recruit Session**
  - Description: Start a recruitment session for a region.
  - Permissions: Recruiter role
  - Usage: `/recruit_session [region] [call_wait]`

- **Set Template**
  - Description: Set the telegram template for the recruitment process.
  - Permissions: Recruiter role
  - Usage: `/set_template [template]`

### Lausanne Comands

- **Lausanne Votes**
  - Description: Get the power of the delegates in the [Second Convention of Lausanne](https://forum.theeastpacific.com/t/the-second-convention-of-lausanne/16883).
  - Usage: `/lausanne_votes`
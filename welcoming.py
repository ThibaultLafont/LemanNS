import requests
import sqlite3
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

# Connect to SQLite database or create a new one if it doesn't exist
db_path = "./Welcome/last_checks.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_checks (
        region TEXT PRIMARY KEY,
        timestamp INTEGER
    )
''')

# Fetch existing last checks from the database
last_checks = dict(cursor.execute('SELECT * FROM last_checks').fetchall())

##################### FETCH NEW NATIONS #####################

def add_to_checks(region: str, timestamp: int):
    """
    Adds a timestamp to the last_checks dictionary.

    Args:
        region (str): The name of the region.
        timestamp (int): The timestamp to add.

    Returns:
        None
    """
    if (region not in last_checks) or (timestamp > last_checks[region]):
        last_checks[region] = timestamp
        cursor.execute('INSERT OR REPLACE INTO last_checks (region, timestamp) VALUES (?, ?)', (region, timestamp))
        conn.commit()
        return True
    return False

def fetch_new_nations(region: str):
    """
    Fetches new nations from the given region.

    Args:
        region (str): The name of the region.

    Returns:
        list: A list of new nation names.

    Raises:
        None
    """
    new_nations = []
    if region not in last_checks:
        print("region was not in last_checks")
        last_checks[region] = int(datetime.now(timezone.utc).timestamp()) - 86400
        cursor.execute('INSERT OR REPLACE INTO last_checks (region, timestamp) VALUES (?, ?)', (region, last_checks[region]))
        conn.commit()

    url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=happenings;filter=move;sinceid={last_checks[region]};"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(response.text)
        last_previous_check = last_checks[region]
        data = ET.fromstring(response.text)
        events = data.find("HAPPENINGS").findall("EVENT")

        for event in events:
            if "arrived from" in event.find("TEXT").text or "was founded" in event.find("TEXT").text:
                timestamp = int(event.find("TIMESTAMP").text)
                add_to_checks(region, timestamp)
                if int(event.find("TIMESTAMP").text) > last_previous_check:
                    new_nations.append(event.find("TEXT").text.split(" ")[0])

        for nation in new_nations:
            for event in events:
                if event.find("TEXT").text.__contains__("departed this region for"):
                    if event.find("TEXT").text.split(" ")[0] == nation and int(event.find("TIMESTAMP").text) > last_checks[region]:
                        new_nations.remove(nation)
        return format_new_nations(new_nations)
    else:
        print("Error:", response.status_code)
        return None

def format_new_nations(nations: list):
    formatted_str = ""
    for nation in nations:
        nation = nation.replace("@@", "")
        formatted_str += f"[nation]{nation}[/nation],"
    formatted_str = formatted_str[:-1]
    return formatted_str

##################### WELCOME MESSAGE FUNCTIONS #####################

def set_welcome_message(region: str, message: str):
    """
    Sets the welcome message for a region.

    Args:
        region (str): The name of the region.
        message (str): The welcome message. It should contain the '[NATIONS]' operator for automated welcome message generation.

    Returns:
        None
    """
    if "[NATIONS]" not in message:
        return False
    filepath = f"/home/thibault/delivery/INN/LemanNS/Welcome/{region}.txt"
    if not os.path.exists(filepath):
        with open(filepath, "w") as file:
            file.write("")
    with open(filepath, "w") as file:
        file.write(message)
    return True

def verify_communications_authority(region: str, nation: str):
    """
    Verifies if the given nation is a regional officer with communications authority.

    Args:
        region (str): The name of the region.
        nation (str): The name of the nation.

    Returns:
        bool: True if the nation is a RO with Comms authority, False otherwise.
    """
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=officers"
    response = requests.get(url, headers=headers)
    data = ET.fromstring(response.text)
    officers = data.find("OFFICERS").findall("OFFICER")

    nation = nation.lower()
    for officer in officers:
        officer_nation = officer.find("NATION").text
        authority = officer.find("AUTHORITY").text

        print(officer_nation)
        print(authority)
        if officer_nation == nation and 'C' in authority:
            return True

    return False

def create_welcome_message(region: str):
    """
    Creates a welcome message for the specified region.

    Args:
        region (str): The region for which to create the welcome message.

    Returns:
        str: The welcome message for the specified region, or None if there are no new nations.

    """
    with open(f"./Welcome/{region}.txt") as msg_file:
        welcome_msg = msg_file.read()

    new_nations = fetch_new_nations(region)
    if new_nations is None or not new_nations:
        return None
    else:
        welcome_msg = welcome_msg.replace("[NATIONS]", f"{new_nations}")
    
    return welcome_msg

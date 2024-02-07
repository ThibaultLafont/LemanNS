import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

last_checks = {}

with open("/home/thibault/delivery/INN/LemanNS/Welcome/last_checks.json", "r") as json_file:
    last_checks = json.load(json_file)

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
        with open("/home/thibault/delivery/INN/LemanNS/Welcome/last_checks.json", "w") as json_file:
            json.dump(last_checks, json_file)
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
        last_checks[region] = int(datetime.now(timezone.utc).timestamp()) - 86400
        with open("/home/thibault/delivery/INN/LemanNS/Welcome/last_checks.json", "w") as json_file:
            json.dump(last_checks, json_file)
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=happenings;filter=move;sinceid={last_checks[region]};"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(response.text)
        data = ET.fromstring(response.text)
        events = data.find("HAPPENINGS").findall("EVENT")

        for event in events:
            if event.find("TEXT").text.__contains__("arrived from") or event.find("TEXT").text.__contains__("was founded in"):
                timestamp = int(event.find("TIMESTAMP").text)
                if add_to_checks(region, timestamp):
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
    format = ""
    for nation in nations:
        nation = nation.replace("@@", "")
        format += f"[nation]{nation}[/nation],"
    format = format[:-1]
    return format

##################### WELCOME MESSAGE FUNCTIONS #####################

def set_welcome_message(region: str, message: str):
    """
    Sets the welcome message for a region.

    Args:
        region (str): The name of the region.
        message (str): The welcome message.

    Returns:
        None
    """
    filepath = f"/home/thibault/delivery/INN/LemanNS/Welcome/{region}.txt"
    if not os.path.exists(filepath):
        with open(filepath, "w") as file:
            file.write("")
    with open(filepath, "w") as file:
        file.write(message)

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

    for officer in officers:
        officer_nation = officer.find("NATION").text
        authority = officer.find("AUTHORITY").text

        if officer_nation == nation and 'C' in authority:
            return True

    return False

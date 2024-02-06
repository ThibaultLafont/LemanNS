import requests
from datetime import datetime, timezone, timedelta

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

last_checks = {"Thaecia": 0, "The East Pacific": 0}

##################### FETCH NEW NATIONS #####################

def add_to_checks(region: str, timestamp: int):
    global last_checks
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

import xml.etree.ElementTree as ET

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
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=happenings;filter=move;sinceid={last_checks[region]}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print (response.text)
        data = ET.fromstring(response.text)
        events = data.find("HAPPENINGS").findall("EVENT")

        for event in events:
            if event.find("TEXT").text.__contains__("arrived from") or event.find("TEXT").text.__contains__("was founded in"):
                timestamp = int(event.find("TIMESTAMP").text)
                add_to_checks(region, timestamp)
                new_nations.append(event.find("TEXT").text.split(" ")[0])

        for nation in new_nations:
            print(f"checking {nation}")
            for event in events:
                print(f"versus {event.find('TEXT').text}")
                if event.find("TEXT").text.__contains__("departed this region for"):
                    if event.find("TEXT").text.split(" ")[0] == nation:
                        new_nations.remove(nation)
                        print("removing nation")

    else:
        print("Error:", response.status_code)
        return None

def format_new_nations(nations: list):
    format = ""
    for nation in nations:
        format += f"[nation]{nation}[/nation],"
    format = format[:-1]
    format.replace("@", "")
    return format
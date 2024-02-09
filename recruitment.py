import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from json.decoder import JSONDecodeError

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

with open("/home/thibault/delivery/INN/LemanNS/Recruitment/last_recruitment_checks.json", "r") as json_file:
    last_checks = json.load(json_file)

##################### INCREMENT TIMESTAMP CHECKS #####################

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
        with open("/home/thibault/delivery/INN/LemanNS/Recruitment/last_recruitment_checks.json", "w") as json_file:
            json.dump(last_checks, json_file)
        return True
    return False

##################### EXCLUDE FOUND TARGETS #####################

import os

def exclude_regions(region: str, to_exclude: str):
    """
    Excludes regions from the recruitment process.

    Args:
        region (str): The name of the region.

    Returns:
        bool: True if the region is excluded, False otherwise.
    """
    region = region.replace(" ", "_")
    region = region.lower()

    file_path = f"/home/thibault/delivery/INN/LemanNS/Recruitment/Excluded/{region}.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            excluded_regions = json.load(json_file)
    else:
        excluded_regions = []

    if to_exclude in excluded_regions:
        return True

    excluded_regions.append(to_exclude)

    with open(file_path, "w") as json_file:
        json.dump(excluded_regions, json_file)

    return False


##################### FETCH NEW NATIONS #####################

def retrieve_excluded_regions(region: str):
    """
    Retrieves the list of excluded regions from the recruitment process.

    Args:
        region (str): The name of the region.

    Returns:
        list: A list of excluded regions.
    """
    region = region.replace(" ", "_")
    region = region.lower()

    file_path = f"/home/thibault/delivery/INN/LemanNS/Recruitment/Excluded/{region}.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            excluded_regions = json.load(json_file)
    else:
        excluded_regions = []

    return excluded_regions

def fetch_new_to_recruit(region: str):
    timestamp = last_checks[region]
    url=f"https://www.nationstates.net/cgi-bin/api.cgi?q=happenings;filter=founding;sincetime={timestamp}"
    response = requests.get(url, headers=headers)

    new_nations = []
    if response.status_code == 200:
        last_previous_check = last_checks[region]
        print(response.text)
        data = ET.fromstring(response.text)
        events = data.find("HAPPENINGS").findall("EVENT")
        excluded_regions = retrieve_excluded_regions(region)

        for event in events:
            if event.find("TEXT").text.__contains__("was founded in"):
                for excluded in excluded_regions:
                    if event.find("TEXT").text.__contains__(excluded):
                        break
                timestamp = int(event.find("TIMESTAMP").text)
                add_to_checks(region, timestamp)
                if timestamp > last_previous_check:
                    new_nations.append(event.find("TEXT").text.split(" ")[0])

        return new_nations

    else:
        print("Error:", response.status_code)
        return None

##################### FORMAT FUNCTIONS #####################

def format_telegrams(new_nations: list, template: str):
    """
    Formats the telegrams to send to new nations.

    Args:
        new_nations (list): A list of new nations.
        template (str): The telegram template.

    Returns:
        list: A list of formatted telegrams.
    """
    i = 0
    for i in range (len(new_nations)):
        new_nations[i] = new_nations[i].replace("@@", "")
        if new_nations[i] != new_nations[-1]:
            new_nations[i] += ","
    tgto_list = []
    i = 0
    while i < len(new_nations):
        tgto_list.append(new_nations[i:i+8])
        i += 8
    telegrams = []
    tgto_str = ""
    for tgto in tgto_list:
        j = 0
        while j < len(tgto):
            if (j == 7):
                tgto[j] = tgto[j][:-1]
            tgto_str += tgto[j]
            j += 1
        telegrams.append(f"https://www.nationstates.net/page=compose_telegram?tgto={tgto_str}&message={template}")
        tgto_str = ""
    return telegrams 

def recruit_new_nations(region: str, uid: int):
    """
    Recruits new nations based on the given region and user ID.

    Args:
        region (str): The region to recruit new nations from.
        uid (int): The user ID.

    Returns:
        str: The formatted telegrams for the new nations, or "NOTEMPLATE" if no template is found. Will also return None if no new nations are found.
    """
    file_path = f"/home/thibault/delivery/INN/LemanNS/Recruitment/template.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            templates = json.load(json_file)
    else:
        templates = {}
    if templates[str(uid)] is None:
        return "NOTEMPLATE"
    new_nations = fetch_new_to_recruit(region)
    if new_nations is None:
        return
    new_nations = format_telegrams(new_nations, templates[str(uid)])
    return new_nations

def format_new_nations(nations: list):
    format = ""
    for nation in nations:
        nation = nation.replace("@@", "")
        format += f"[nation]{nation}[/nation],"
    format = format[:-1]
    return format

##################### TELEGRAM TEMPLATES FUNCTION #####################

import os
import json
from json.decoder import JSONDecodeError

def store_template(template: str, uid: int):
    """
    Stores a telegram template for a user.

    Args:
        template (str): The template to store.
        uid (int): The user ID.

    Returns:
        None
    """
    file_path = f"/home/thibault/delivery/INN/LemanNS/Recruitment/template.json"

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as json_file:
                templates = json.load(json_file)
        else:
            templates = {}
    except JSONDecodeError:
        templates = {}

    reversed_templates = {v: k for k, v in templates.items()}
    reversed_templates[template] = uid

    with open(file_path, "w") as json_file:
        json.dump(reversed_templates, json_file)

import requests
import time
import json
import xml.etree.ElementTree as ET

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

SUPERREGIONS = ["Alstroemerian Commonwealths", "The Free Nations Federation", "Augustin Alliance"]

AC = ["Japan", "Alstroemeria", "The Glorious Nations of Iwaku", "Eientei Gensokyo", "Yggdrasil", "Hetalia", "Slavija"]
FNF = ["The Free Nations Region", "Hive", "Equiterra"]
AA = ["Conch Kingdom", "Cape of Good Hope", "Lands End", "Dawn", "Anteria", "Narnia", "Ridgefield"]

##################### EMPTY JSON FILE #####################

def empty_json(region: str):
    superregion = None
    if region in AC:
        superregion = "AC"
    if region in FNF:
        superregion = "FNR"
    if region in AA:
        superregion = "AA"
    if superregion is not None:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{superregion}/{region}.json"
    else:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{region}.json"
    empty_data = {}
    with open(filepath, "w") as json_file:
        json.dump(empty_data, json_file)

##################### USER LIST FUNCTIONS #####################

def get_superregion(region: str):
    """
    Returns the superregion of the given region.

    Args:
        region (str): The name of the region.

    Returns:
        str: The superregion of the given region.
    """
    if region in AC:
        return "Alstroemerian Commonwealths"
    if region in FNF:
        return "The Free Nations Federation"
    if region in AA:
        return "Augustin Alliance"
    return None

##################### REGION LIST FUNCTIONS #####################
def nation_json(user: str, nation: str, region:str, superregion: str):
    """
    Add a nation to a JSON file based on the user, nation, region, and superregion parameters.

    Args:
        user (str): The user identifier.
        nation (str): The nation to be added.
        region (str): The region where the nation belongs.
        superregion (str): The superregion where the region belongs (optional).

    Returns:
        None
    """
    if superregion is not None:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{superregion}/{region}.json"
    else:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{region}.json"
    try:
        with open(filepath, "r") as json_file:
            nations_list = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        nations_list = {}
    key = str(user.id)
    if key in nations_list:
        print(f"User '{user}' already exists in the list.")
        return
    if nation in nations_list.values():
        print(f"Nation '{nation}' already exists in the list.")
        return
    nations_list[key] = nation
    with open(filepath, "w") as json_file:
        json.dump(nations_list, json_file)

def region_checkup(region: str):
    """
    Performs a checkup on the given region by retrieving a list of nations associated with the region,
    and removing any nations that are no longer part of the region.

    Args:
        region (str): The name of the region to perform the checkup on.

    Returns:
        None
    """
    i = 0
    superregion = get_superregion(region)
    if superregion is not None:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{superregion}/{region}.json"
    else:
        filepath = f"/home/thibault/delivery/INN/Leman/Regions/{region}.json"

    try:
        with open(filepath, "r") as json_file:
            nations_list = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        nations_list = {}

    for key in nations_list:
        nation = nations_list[key]
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nation}&q=region"
        response = requests.get(url, headers=headers)
        i += 1
        root = ET.fromstring(response.text)
        response = root.find('REGION').text
        print(response)
        if response != region:
            print(f"Removing '{nation}' from the list.")
            del nations_list[key]
        if (i == 30):
            i = 0
            time.sleep(30)

    with open(filepath, "w") as json_file:
        json.dump(nations_list, json_file)

##################### NATION VERIFICATION FUNCTIONS #####################
def verify_nation(nation: str, key: str):
    """
    Verifies a nation using the NationStates API.

    Args:
        nation (str): The name of the nation to verify.
        key (str): The verification key.

    Returns:
        bool: True if the nation is verified, False otherwise.
    """
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?a=verify&nation={nation}&checksum={key}"
    response = requests.get(url, headers=headers)
    response = response.text
    print(response, end="")
    if response[0] == "1":
        return True
    return False

##################### REGION VERIFICATION FUNCTIONS #####################
def simplify_region(region: str):
    """
    Simplifies the given region name to its corresponding abbreviation.

    Args:
        region (str): The name of the region.

    Returns:
        str: The abbreviation of the region.

    """
    match(region):
        case "The East Pacific":
            return "TEP"
        case 'The Glorious Nations of Iwaku':
            return "Iwaku"
        case 'Eientei Gensokyo':
            return "EG"
        case 'Conch Kingdom':
            return "CK"
        case 'Cape of Good Hope':
            return "CGH"
        case 'Lands End':
            return "LE"
    return region

def nation_in_region(user: str, nation: str, region: str):
    """
    Retrieves information about a nation in a specific region.

    Args:
        user (str): The user making the request.
        nation (str): The name of the nation to retrieve information for.
        region (str): The name of the region to check the nation's affiliation with.

    Returns:
        str: The name of the region the nation is affiliated with.
    """
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nation}&q=region"
    response = requests.get(url, headers=headers)
    root = ET.fromstring(response.text)
    response = root.find('REGION').text
    print(response)
    if region == None:
        region = response
    if response == region:
        superregion = get_superregion(region)
        region = simplify_region(region)
        nation_json(user, nation, region, superregion)
    return response
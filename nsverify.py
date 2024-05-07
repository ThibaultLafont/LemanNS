import requests
import time
import sqlite3
import xml.etree.ElementTree as ET

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

SUPERREGIONS = ["Alstroemerian Commonwealths", "The Free Nations Federation", "Augustin Alliance"]

AC = ["Japan", "Alstroemeria", "The Glorious Nations of Iwaku", "Eientei Gensokyo", "Yggdrasil", "Hetalia", "Slavija"]
FNF = ["The Free Nations Region", "Hive", "Equiterra"]
AA = ["Conch Kingdom", "Cape of Good Hope", "Lands End", "Dawn", "Anteria", "Narnia", "Ridgefield"]

db_path = "./Regions/Regions.sqlite"

##################### EMPTY DATABASE #####################

# def empty_db(region: str):
#     """
#     Empties the database of the given region.

#     Args:
#         region (str): The name of the region to empty the database of.

#     Returns:
#         None
#     """
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute(f"DROP TABLE IF EXISTS {region}")
#     conn.commit()

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
def add_nation_to_database(user: str, nation: str, region:str):
    """
    Add a nation to a SQL Database on the user, nation, and region parameters.

    Args:
        user (str): The user identifier.
        nation (str): The nation to be added.
        region (str): The region where the nation belongs.

    Returns:
        None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {region} (
        nation TEXT PRIMARY KEY,
        discordid INTEGER
        )
    ''')

    try:
        cursor.execute(f"SELECT * FROM {region} WHERE nation = ?", (nation,))
        existing_nation = cursor.fetchone()
    except sqlite3.Error:
        existing_nation = None

    key = str(user.id)
    if existing_nation:
        print(f"Nation '{nation}' already exists in the list.")
        return
    else:
        cursor.execute(f"INSERT INTO {region} (nation, discordid) VALUES (?, ?)", (nation, key))
        conn.commit()


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
    removed_nations = []
    removed_count = 0
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT * FROM {region}")
        rows = cursor.fetchall()
        nations_list = {row[0]: row[1] for row in rows}
    except sqlite3.Error:
        nations_list = {}

    for key in nations_list:
        nation = nations_list[key]
        print(f"Checking '{nation}'...")
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nation}&q=region"
        response = requests.get(url, headers=headers)
        i += 1
        root = ET.fromstring(response.text)
        response = root.find('REGION').text
        response = response.rstrip('\n')  # Remove '\n' at the end of the response
        if response != region:
            print(f"Removing '{nation}' from the list.")
            del nations_list[key]
            removed_nations.append(nation)
            removed_count += 1
        if (i == 30):
            i = 0
            time.sleep(30)

    for nation in removed_nations:
        cursor.execute(f"DELETE FROM {region} WHERE nation = ?", (nation,))
        conn.commit()

    print("removed nations == ", removed_nations)
    return removed_nations, removed_count

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

def change_user_nation(user: str, nation, region: str):
    """
    Changes the nation of a user in the JSON file.

    Args:
        user (str): The user identifier.
        nation (str): The nation to change to.

    Returns:
        None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {region} (
        nation TEXT PRIMARY KEY,
        discordid INTEGER
        )
    ''')

    try:
        cursor.execute(f"SELECT * FROM {region}")
        rows = cursor.fetchall()
    except sqlite3.Error:
        return False

    key = str(user.id)
    cursor.execute(f"INSERT INTO {region} (nation, discordid) VALUES (?, ?)", (nation, key))
    conn.commit()
    return True

def is_member(region: str, nation:str):
    """
    Check if a nation is a member of a region.

    Args:
        region (str): The name of the region.
        nation (str): The name of the nation.

    Returns:
        bool: True if the nation is a member of the region, False otherwise.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {region} (
        nation TEXT PRIMARY KEY,
        discordid INTEGER
        )
    ''')

    try:
        cursor.execute(f"SELECT * FROM {region}")
        rows = cursor.fetchall()
        nations_list = {row[0]: row[1] for row in rows}
    except sqlite3.Error:
        nations_list = {}
    
    if nation not in nations_list:
        return False
    return True

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
        region = simplify_region(region)
        add_nation_to_database(user, nation, region)
    return response
import requests
import sqlite3
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from json.decoder import JSONDecodeError

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

db_path = "/home/thibault/delivery/INN/LemanNS/Recruitment/last_recruitment_checks.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_recruitment_checks (
        region TEXT PRIMARY KEY,
        timestamp INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        uid INTEGER PRIMARY KEY,
        template TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS excluded_regions (
        region TEXT PRIMARY KEY,
        to_exclude TEXT
    )
''')

# Fetch existing last recruitment checks from the database
last_checks = dict(cursor.execute('SELECT * FROM last_recruitment_checks').fetchall())

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
        # Update the SQLite database
        cursor.execute('INSERT OR REPLACE INTO last_recruitment_checks (region, timestamp) VALUES (?, ?)', (region, timestamp))
        conn.commit()
        return True
    return False

##################### EXCLUDE FOUND TARGETS #####################

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

    # Update the SQLite database
    cursor.execute('INSERT OR IGNORE INTO excluded_regions (region, to_exclude) VALUES (?, ?)', (region, to_exclude))
    conn.commit()

    return False

##################### FETCH NEW NATIONS #####################

def retrieve_excluded_regions(region: str):
    """
    Retrieves the list of excluded regions from the recruitment process.

    Args:
        region (str): The name of the region.
        cursor: SQLite cursor object.

    Returns:
        list: A list of excluded regions.
    """
    region = region.replace(" ", "_")
    region = region.lower()

    try:
        excluded_regions = [row[0] for row in cursor.execute('SELECT to_exclude FROM excluded_regions WHERE region = ?', (region,)).fetchall()]
        return excluded_regions
    except sqlite3.OperationalError:
        print(f"Error: The region {region} does not exist in the database.")
        return []


def fetch_new_to_recruit(region: str):
    try:
        timestamp = last_checks[region]
    except KeyError:
        print("Region not found in last_checks")
        timestamp = int(datetime.now(timezone.utc).timestamp()) - 86400
        cursor.execute('INSERT INTO last_recruitment_checks (region, timestamp) VALUES (?, ?)', (region, timestamp))
        conn.commit()

    url = f"https://www.nationstates.net/cgi-bin/api.cgi?q=happenings;filter=founding;sincetime={timestamp}"
    response = requests.get(url, headers=headers)

    new_nations = []
    if response.status_code == 200:
        last_previous_check = last_checks[region]
        print(response.text)
        data = ET.fromstring(response.text)
        events = data.find("HAPPENINGS").findall("EVENT")
        excluded_regions = retrieve_excluded_regions(region)

        for event in events:
            if "was founded in" in event.find("TEXT").text:
                for excluded in excluded_regions:
                    if excluded in event.find("TEXT").text:
                        break
                else:
                    timestamp = int(event.find("TIMESTAMP").text)
                    print("timestamp:", timestamp)
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
    # Fetch the template from the database
    template = cursor.execute('SELECT template FROM templates WHERE uid = ?', (uid,)).fetchone()
    if template is None:
        return "NOTEMPLATE"
    template = template[0]
    
    new_nations = fetch_new_to_recruit(region)
    if new_nations is None:
        return None
    if not new_nations:
        return None

    formatted_telegrams = format_telegrams(new_nations, template)
    return formatted_telegrams

def format_new_nations(nations: list):
    formatted_str = ""
    for nation in nations:
        nation = nation.replace("@@", "")
        formatted_str += f"[nation]{nation}[/nation],"
    formatted_str = formatted_str[:-1]
    return formatted_str

##################### TELEGRAM TEMPLATES FUNCTION #####################

def store_template(template: str, uid: str):
    """
    Stores a telegram template for a user.

    Args:
        template (str): The template to store.
        uid (str): The user ID.
    """
    # Explicitly convert template to string if needed
    template_str = str(template)
    int_uid = int(uid)

    print(f'Type of uid: {type(uid)}')
    print(f'Type of template_str: {type(template_str)}')

    cursor.execute('INSERT OR REPLACE INTO templates (uid, template) VALUES (?, ?)', (int_uid, template_str))
    conn.commit()

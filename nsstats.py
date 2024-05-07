import requests
import xml.etree.ElementTree as ET

headers = {
    "User-Agent": "Discord: Altys, Nation: Altys or Islonia"
}

##################### LAUSANNE STATS #####################

def get_lausanne_delegates_power():
    """
    Gets the power of the delegates in the Lausanne Alliance (onsite).

    Returns:
        int: The power of the delegates in Lausanne.
    """
    regions = ['the_east_pacific', 'the_glorious_nations_of_iwaku', 'eientei_gensokyo', 'yggdrasil', 'hetalia', 'slavija', 'japan', 'the free nations region', 'hive', 'equiterra', 'thaecia']
    votes = {region: get_delegate_voting_power(region) for region in regions}

    fnf_votes = votes['the free nations region'] + votes['hive'] + votes['equiterra']
    ac_votes = votes['the_glorious_nations_of_iwaku'] + votes['eientei_gensokyo'] + votes['yggdrasil'] + votes['hetalia'] + votes['slavija'] + votes['japan']
    lausanne_votes = ac_votes + fnf_votes + votes['thaecia'] + votes['the_east_pacific']
    lausanne_str = f"""
# Lausanne Voting Power Breakdown
## The East Pacific
{votes['the_east_pacific']}
## The Alstroemerian Comonwealths
**he Glorious Nations of Iwaku**
{votes['the_glorious_nations_of_iwaku']}
**Eientei Gensokyo**
{votes['eientei_gensokyo']}
**Yggdrasil**
{votes['yggdrasil']}
**Hetalia**
{votes['hetalia']}
**Slavija**
{votes['slavija']}
**Japan**
{votes['japan']}
**Total**
{ac_votes}
## The Free Nations Federation
**The Free Nations Region**
{votes['the free nations region']}
**Hive**
{votes['hive']}
**Equiterra**
{votes['equiterra']}
**Total**
{fnf_votes}
## Thaecia
{votes['thaecia']}
## Total
{lausanne_votes}
"""
    return lausanne_str

##################### STAT FUNCTIONS #####################

def get_delegate_voting_power(region: str):
    """
    Gets the voting power of the delegate in the region.

    Args:
        region (str): The name of the region.

    Returns:
        int: The voting power of the delegate.
    """
    url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=delegatevotes"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    return int(root.find("DELEGATEVOTES").text)
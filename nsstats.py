import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from json.decoder import JSONDecodeError

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
    lausanne_votes = "# Lausanne Voting Power Breakdown\n\n**The East Pacific**\n"
    lausanne_votes += f"{get_delegate_voting_power('the_east_pacific')}\n"
    lausanne_votes += "**The Alstroemerian Comonwealths**\n"
    ac_votes = (
        get_delegate_voting_power('the_glorious_nations_of_iwaku') +
        get_delegate_voting_power('eientei_gensokyo') +
        get_delegate_voting_power('yggdrasil') +
        get_delegate_voting_power('hetalia') +
        get_delegate_voting_power('slavija') +
        get_delegate_voting_power('japan')
    )
    lausanne_votes += f"{ac_votes}\n"
    lausanne_votes += "**The Free Nations Federation**\n"
    fnf_votes = (get_delegate_voting_power('the free nations region') + get_delegate_voting_power('hive') + get_delegate_voting_power('equiterra'))
    lausanne_votes += f"{fnf_votes}\n"
    lausanne_votes += "**Thaecia**\n"
    lausanne_votes += f"{get_delegate_voting_power('thaecia')}\n"
    lausanne_votes += "**Total**\n"
    lausanne_votes += f"{ac_votes + fnf_votes + get_delegate_voting_power('thaecia') + get_delegate_voting_power('the_east_pacific')}\n"
    return lausanne_votes

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
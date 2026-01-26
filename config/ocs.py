import random

from .aesthetic import Emojis

OCS_RARITY_MAP = {
    "Common": {
        "rate": 0.5,
        "emoji": Emojis.Common,
        "color": 0x21CCB7,
    },
    "Rare": {
        # 15% rate
        "rate": 0.15,
        "emoji": Emojis.Rare,
        "color": 0x4B69FF,
    },
    "Epic": {
        # epic rate 1%
        "rate": 0.01,
        "emoji": Emojis.Epic,
        "color": 0xAA00FF,
    },
    "Legendary": {
        # legendary rate 1/7000 ~0.000142857
        "rate": 0.000142857,
        "emoji": Emojis.Legendary,
        "color": 0xFF8C00,
    },
}


OC_NAMES = ["Kae", "Cherry", "Kiara", "Lyra", "Melissa", "Mika", "Skye", "Dolly", "Nyx"]


def determine_is_skin(name: str) -> bool:
    stripped = name.strip()
    for oc in OC_NAMES:
        if oc in stripped and stripped != oc:
            return True
    return False

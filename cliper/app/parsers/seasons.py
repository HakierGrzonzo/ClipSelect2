import xml.etree.ElementTree as ET
from .utils import get_unique_id


def parse_season_from_nfo(content: str):
    xml = ET.fromstring(content)
    try:
        return {
            "name": xml.find("title").text,
            "order": int(xml.find("seasonnumber").text),
            "id": get_unique_id(xml),
        }
    except Exception:
        raise Exception(content)

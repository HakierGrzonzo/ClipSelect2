import xml.etree.ElementTree as ET


def parse_season_from_nfo(content: str):
    xml = ET.fromstring(content)
    try:
        return {
            "name": xml.find("title").text,
            "order": int(xml.find("seasonnumber").text),
        }
    except:
        raise Exception(content)

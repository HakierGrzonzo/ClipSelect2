import xml.etree.ElementTree as ET


def get_unique_id(tree: ET) -> int:
    for e in tree.findall("uniqueid"):
        if e.get("type") == "tvdb":
            return int(e.text)
    return int(tree.find("tvdbid").text)

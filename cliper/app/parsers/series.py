import xml.etree.ElementTree as ET


def parse_series_from_nfo(content: str):
    xml = ET.fromstring(content)
    title = xml.find("originaltitle")
    if title is None:
        title = xml.find("title")
    return {
        "name": title.text,
    }

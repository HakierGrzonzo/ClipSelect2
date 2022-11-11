import xml.etree.ElementTree as ET
from .utils import get_unique_id


def parse_series_from_nfo(content: str):
    xml = ET.fromstring(content)
    title = xml.find("title")
    if title is None:
        title = xml.find("originaltitle")
    return {
        "name": title.text,
        "id": get_unique_id(xml),
    }

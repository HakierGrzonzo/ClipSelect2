from typing import Tuple


def parse_timestamp_format(subtitle_timestamp: str) -> Tuple[int, int, float]:
    hours, minutes, seconds = subtitle_timestamp.split(":")
    return int(hours), int(minutes), float(seconds.replace(",", "."))


def unformat_timestamp(subtitle_timestamp: Tuple[int, int, float]) -> float:
    hours, minutes, seconds = subtitle_timestamp
    return 60 * ((60 * hours) + minutes) + seconds

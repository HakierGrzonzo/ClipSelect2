from pydantic import BaseModel
from .utils import parse_timestamp_format, unformat_timestamp
from .cleaner import extract_text


class Subtitle(BaseModel):
    start: float
    stop: float
    text: str


def parse_srt_string(subs: str):
    # Split the whole file into specific subtitles
    last_subtitle = None

    for subtitle in subs.strip().split("\n\n"):
        # We don't care about the order, we assume that all subs are ordered
        # correctly
        _, timestamps, text = subtitle.split("\n", 2)

        # Parse timestamps
        start_timestamp, stop_timestamp = [
            unformat_timestamp(parse_timestamp_format(x.strip()))
            for x in timestamps.split("-->")
        ]
        clean_text = extract_text(text)
        if clean_text is not None:
            if (
                len(clean_text) > 256
                or len(clean_text) < 2
                or stop_timestamp - start_timestamp < 0.1
            ):
                print(f"Wierd subtitle: '{clean_text}'")
                continue
            if last_subtitle:
                if last_subtitle.stop > start_timestamp:
                    print(f"Wierd overlap subtitle: '{clean_text}'")
                    continue
            last_subtitle = Subtitle(
                start=start_timestamp, stop=stop_timestamp, text=clean_text
            )
            yield last_subtitle


def main():
    pass
    import sys

    raw_subs = sys.stdin.read()
    for sub in parse_srt_string(raw_subs):
        print(sub)


if __name__ == "__main__":
    main()

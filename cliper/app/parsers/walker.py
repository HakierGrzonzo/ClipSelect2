from collections import defaultdict
from os import path, listdir
from aiofiles import open
from asyncio import gather, Task

from app.database import Episode, Series, SubSeries
from .episode import parse_episode_from_nfo, parse_episode_into_clips

from .seasons import parse_season_from_nfo

from .series import parse_series_from_nfo


async def walk_subseries(folder_path: str) -> SubSeries:
    episodes = defaultdict(lambda: {})
    meta = None
    for element in listdir(folder_path):
        if element.endswith(".nfo"):
            if element.startswith("season"):
                async with open(path.join(folder_path, element)) as f:
                    meta = parse_season_from_nfo(await f.read())
            else:
                async with open(path.join(folder_path, element)) as f:
                    key = element.removesuffix(".nfo")
                    episodes[key] = {
                        **parse_episode_from_nfo(await f.read()),
                        **episodes[key],
                    }
                # parse episode nfo
        elif any(element.endswith(x) for x in [".mkv", ".mp4"]):
            print(element)
            suffix = element.split(".")[-1]
            episodes[element.removesuffix(f".{suffix}")]["path"] = path.join(
                folder_path, element
            )
    if meta is None:
        raise Exception(f"Failed to find meta in {folder_path}")
    episodes = await gather(
        *[parse_episode_into_clips(v) for v in episodes.values()]
    )
    subseries = SubSeries(
        name=meta["name"],
        order=meta["order"],
        episodes=list(episodes),
    )
    return subseries


async def walk_series(folder_path: str) -> Series:
    subseries_walkers = []
    meta = None
    poster = None
    for element in listdir(folder_path):
        if element.endswith(".nfo"):
            async with open(path.join(folder_path, element)) as f:
                meta = parse_series_from_nfo(await f.read())
        elif element.startswith("Season "):
            subseries_walkers.append(
                Task(walk_subseries(path.join(folder_path, element)))
            )
        elif element.startswith("poster"):
            poster = path.join(folder_path, element)

    if meta is None:
        raise Exception(f"Failed to find meta in {folder_path}")
    subseries = await gather(*subseries_walkers)
    series = Series(name=meta["name"], subseries=subseries, poster_path=poster)
    return series

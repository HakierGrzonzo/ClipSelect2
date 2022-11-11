from datetime import timedelta
from functools import wraps
from json import dumps
from base64 import b64encode
from typing import Dict, Iterable
from os import path, mkdir, environ
import pickle
import aiofiles
from fastapi import Response
from fastapi.responses import StreamingResponse

CACHE_DIR = environ.get("CACHE", "./cache")


def create_cache_dir():
    try:
        mkdir(CACHE_DIR)
    except:
        pass


def generate_identifier(args: Iterable, kwargs: Dict):
    serialized = []
    for a in args:
        try:
            serialized.append(dumps(a))
        except:
            pass
    for a in kwargs.values():
        try:
            serialized.append(dumps(a))
        except:
            pass
    return ":".join(list(b64encode(s.encode()).decode() for s in serialized))


def cache_headers(expire: timedelta = timedelta(days=365)):
    def outer_wrapper(func):
        @wraps(func)
        async def inner_wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            if response.status_code == 200:
                response.headers[
                    "Cache-Control"
                ] = f"max-age={expire.total_seconds()}, public"
            return response

        return inner_wrapper

    return outer_wrapper


def cache(*, expire: timedelta = timedelta(days=365)):
    def outer_wrapper(func):
        prefix = func.__name__

        @wraps(func)
        async def inner_wrapper(*args, **kwargs):
            identifier = prefix + generate_identifier(args, kwargs)
            try:
                async with aiofiles.open(
                    path.join(CACHE_DIR, identifier), "rb"
                ) as f:
                    response = pickle.loads(await f.read())
                    print(f"Responding from CACHE with {identifier}")
                    return response
            except:
                response = await func(*args, **kwargs)
                response.headers[
                    "Cache-Control"
                ] = f"max-age={expire.total_seconds()}, public"
                async with aiofiles.open(
                    path.join(CACHE_DIR, identifier), "wb+"
                ) as f:
                    await f.write(pickle.dumps(response))
                return response

        return inner_wrapper

    return outer_wrapper


def cache_streaming(*, expire: timedelta = timedelta(days=365)):
    def outer_wrapper(func):
        prefix = func.__name__

        @wraps(func)
        async def inner_wrapper(*args, **kwargs):
            identifier = prefix + generate_identifier(args, kwargs)
            try:
                async with aiofiles.open(
                    path.join(CACHE_DIR, identifier), "rb"
                ) as f:
                    response = pickle.loads(await f.read())
                    print(f"Responding from CACHE with {identifier}")
                    return response
            except:
                res = await func(*args, **kwargs)
                if not isinstance(res, tuple):
                    return res
                headers, content_generator = res
                headers[
                    "Cache-Control"
                ] = f"max-age={expire.total_seconds()}, public"

                async def iterate_over_content():
                    content = bytes()
                    async for data in content_generator:
                        content += data
                        yield data
                    cached_response = Response(content, headers=headers)
                    async with aiofiles.open(
                        path.join(CACHE_DIR, identifier), "wb+"
                    ) as f:
                        await f.write(pickle.dumps(cached_response))

                return StreamingResponse(
                    iterate_over_content(), headers=headers
                )

        return inner_wrapper

    return outer_wrapper

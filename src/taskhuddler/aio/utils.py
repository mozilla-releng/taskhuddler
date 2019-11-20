"""Common utilities for understanding task graphs, async version."""

import asyncio
from urllib.parse import urlparse

import aiobotocore
import aiofiles


async def _fetch_s3_file(filename):
    """Read a file's contents from AWS S3."""
    session = aiobotocore.get_session(loop=asyncio.get_event_loop())
    url = urlparse(filename)
    async with session.create_client('s3') as client:
        response = await client.get_object(Bucket=url.netloc, Key=url.path.lstrip('/'))
        async with response['Body'] as stream:
            return await stream.read()


async def _fetch_local_file(filename):
    """Fetch a local file asynchronously."""
    async with aiofiles.open(filename, mode='r') as f:
        return await f.read()


async def fetch_file(filename):
    """Retrieve a file's contents from either local or remote.

    Args:
        filename (str): The file to load. If prefixed with s3:// it will
            attempt to load the file from s3 using the environment's credentials.
    Returns:
        str: The contents of the file.

    """
    if filename.startswith('s3://'):
        return await _fetch_s3_file(filename)
    else:
        return await _fetch_local_file(filename)


async def _store_s3_file(filename, contents):
    """Store a file on s3."""
    session = aiobotocore.get_session(loop=asyncio.get_event_loop())
    url = urlparse(filename)
    async with session.create_client('s3') as client:
        resp = await client.put_object(Bucket=url.netloc,
                                       Key=url.path.lstrip('/'),
                                       Body=contents)
        return resp


async def _store_local_file(filename, contents):
    """Store a file locally."""
    async with aiofiles.open(filename, mode='w') as f:
        await f.write(contents)


async def store_file(filename, contents):
    """Store a file either locally or remotely."""
    if filename.startswith('s3://'):
        await _store_s3_file(filename, contents)
    else:
        await _store_local_file(filename, contents)

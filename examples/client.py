# This file provides functions to make HTTP requests to the TAMS API.
# The functions include a retry on authentication failures when using renewable credentials.

from typing import AsyncGenerator
from contextlib import asynccontextmanager

import aiohttp

from credentials import Credentials, RenewableCredentials


@asynccontextmanager
async def request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    method: str,
    url: str,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a request and retry once if there is a credentials failure"""
    # Extract the 'headers' as they need to be extended with the auth credentials
    in_headers = {}
    if "headers" in kwargs:
        in_headers = kwargs.pop("headers")

    if isinstance(credentials, RenewableCredentials):
        await credentials.ensure_credentials()

    have_retried = False
    while True:
        async with session.request(method, url, headers=in_headers | credentials.header(), **kwargs) as resp:
            if resp.status != 401 or not isinstance(credentials, RenewableCredentials) or have_retried:
                yield resp
                break

        # Renew the credentials and retry
        await credentials.renew_credentials()
        have_retried = True


@asynccontextmanager
async def get_request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    url: str,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a GET request and retry once if there is a credentials failure"""
    async with request(session, credentials, "GET", url, **kwargs) as resp:
        yield resp


@asynccontextmanager
async def put_request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    url: str,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a PUT request and retry once if there is a credentials failure"""
    async with request(session, credentials, "PUT", url, **kwargs) as resp:
        yield resp


@asynccontextmanager
async def post_request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    url: str,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a POST request and retry once if there is a credentials failure"""
    async with request(session, credentials, "POST", url, **kwargs) as resp:
        yield resp


@asynccontextmanager
async def delete_request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    url: str,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a DELETE request and retry once if there is a credentials failure"""
    async with request(session, credentials, "DELETE", url, **kwargs) as resp:
        yield resp

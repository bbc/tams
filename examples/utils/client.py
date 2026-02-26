# This file provides functions to make HTTP requests to the TAMS API.
# The functions include a retry on authentication failures when using renewable credentials.

import dataclasses
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

import aiohttp
import aiohttp.client_exceptions

from .credentials import Credentials, RenewableCredentials


@dataclasses.dataclass
class TAMSClientException(Exception):
    error: aiohttp.client_exceptions.ClientResponseError
    body: Optional[str]

    def __str__(self) -> str:
        return f"{str(self.error)}, body={self.body}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.error.__repr__}, body={self.body})"


@asynccontextmanager
async def request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    method: str,
    url: str,
    raise_on_error: bool = True,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a request and retry once if there is a credentials failure"""
    # Extract the 'headers' as they need to be extended with the auth credentials
    in_headers = {
        "Content-Type": "application/json"
    }
    if "headers" in kwargs:
        in_headers = kwargs.pop("headers")

    if isinstance(credentials, RenewableCredentials):
        await credentials.ensure_credentials()

    have_retried = False
    while True:
        async with session.request(method, url, headers=in_headers | credentials.header(), **kwargs) as resp:
            if resp.status != 401 or not isinstance(credentials, RenewableCredentials) or have_retried:
                if raise_on_error:
                    try:
                        resp.raise_for_status()
                    except aiohttp.client_exceptions.ClientResponseError as e:
                        raise TAMSClientException(e, await resp.text())
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
    raise_on_error: bool = True,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a GET request and retry once if there is a credentials failure"""
    async with request(session, credentials, "GET", url, raise_on_error=raise_on_error, **kwargs) as resp:
        yield resp


@asynccontextmanager
async def put_request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    url: str,
    raise_on_error: bool = True,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a PUT request and retry once if there is a credentials failure"""
    async with request(session, credentials, "PUT", url, raise_on_error=raise_on_error, **kwargs) as resp:
        yield resp


@asynccontextmanager
async def post_request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    url: str,
    json: dict = {},
    raise_on_error: bool = True,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a POST request and retry once if there is a credentials failure"""
    async with request(session, credentials, "POST", url, json=json, raise_on_error=raise_on_error, **kwargs) as resp:
        yield resp


@asynccontextmanager
async def delete_request(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    url: str,
    raise_on_error: bool = True,
    **kwargs
) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    """Execute a DELETE request and retry once if there is a credentials failure"""
    async with request(session, credentials, "DELETE", url, raise_on_error=raise_on_error, **kwargs) as resp:
        yield resp

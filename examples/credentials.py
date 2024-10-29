# This file provides functions to handle TAMS API credentials

from abc import ABCMeta, abstractmethod
import base64

import aiohttp


def get_basic_auth_header(name: str, secret: str) -> dict[str, str]:
    creds = base64.b64encode(f"{name}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {creds}"}


class Credentials(metaclass=ABCMeta):
    """Base class for TAMS API credentials"""
    @abstractmethod
    def header(self) -> dict[str, str]:
        """Returns the Authorization HTTP header"""
        return {}


class BasicCredentials(Credentials):
    """Basic username/password credentials"""
    def __init__(self, username: str, password: str) -> None:
        self._header = get_basic_auth_header(username, password)

    def header(self) -> dict[str, str]:
        return self._header


class RenewableCredentials(Credentials):
    """Base class for credentials that need to be renewed"""
    @abstractmethod
    async def ensure_credentials(self) -> None:
        pass

    @abstractmethod
    async def renew_credentials(self) -> None:
        pass


class OAuth2ClientCredentials(RenewableCredentials):
    """OAuth2 Client Credentials Grant credentials"""
    def __init__(
        self,
        authorization_url: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        self.authorization_url = authorization_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ""
        self.expires_in = 0.0

    async def ensure_credentials(self) -> None:
        if not self.access_token:
            await self.renew_credentials()

    async def renew_credentials(self) -> None:
        form_data = {
            "grant_type": "client_credentials",
            "scope": "openid"
        }
        headers = get_basic_auth_header(self.client_id, self.client_secret)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.authorization_url, data=form_data, headers=headers) as resp:
                resp.raise_for_status()

                token_response = await resp.json()
                self.access_token = token_response["access_token"]
                self.expires_in = token_response["expires_in"]

    def header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

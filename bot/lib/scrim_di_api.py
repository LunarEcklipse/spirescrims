import asyncio, json, aiohttp
from datetime import datetime, timedelta, timezone
from typing import Union, List
from lib.DI_API_Obj.sweet_user import SweetUserPartial, SweetUser

oauth_url: str = "https://community-auth.auth.us-east-1.amazoncognito.com/oauth2/token"
api_base_url: str = "https://1gy5zni8ll.execute-api.us-east-1.amazonaws.com/community/game/deceiveinc"

class DeceiveIncApiResponseError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"DeceiveInc API returned status {status}: {message}")

class ScrimDiAPI:
    _session: aiohttp.ClientSession
    _access_token: str
    _token_expiration_time: datetime
    _client_id: str
    _client_secret: str

    def __init__(self, client_id: str, client_secret: str, session: aiohttp.ClientSession = None):
        self._session = session if session is not None else aiohttp.ClientSession()
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = None
        self._token_expiration_time = None

    def __del__(self):
        if self._session is not None:
            try:
                loop = asyncio.get_event_loop()
                asyncio.create_task(self._session.close())
            except:
                asyncio.run(self._session.close())

    # Authorization functions

    def _get_token_expiration_time(self) -> datetime:
        return self._token_expiration_time

    def _is_token_expired(self) -> bool:
        return self._get_token_expiration_time() is None or datetime.now(timezone.utc) >= self._token_expiration_time
    
    async def _refresh_access_token(self) -> None:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        async with self._session.post(oauth_url, data={
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret
        }) as response:
            response.raise_for_status()
            data = await response.json()
            self._access_token = data["access_token"]
            self._token_expiration_time = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])

    async def _get_access_token(self) -> str:
        if self._access_token is None or self._is_token_expired():
            await self._refresh_access_token()
        return self._access_token
    
    # API functions

    @staticmethod
    async def initialize(client_id: str, client_secret: str) -> "ScrimDiAPI":
        out = ScrimDiAPI(client_id, client_secret)
        await out._refresh_access_token()
        return out
    
    async def search_users(self, query: str, retry: bool = False) -> List[SweetUserPartial]:
        search_url: str = f"{api_base_url}/search/user"
        async with self._session.get(search_url, headers={
            "Authorization": f"Bearer {await self._get_access_token()}"
        }, params={
            "query": query
        }) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                if e.status == 401: # The token needs to be refreshed and tried again
                    if retry: # If we've already tried refreshing the token, raise the error
                        raise DeceiveIncApiResponseError(e.status, "The access token is invalid.")
                    await self._refresh_access_token()
                    return await self.search_users(query, True)
            data = await response.json()
            return [SweetUserPartial(user["sweetId"], user["displayName"]) for user in data]
    
    async def get_user(self, sweet_id: str, retry: bool = False) -> SweetUser:
        user_url: str = f"{api_base_url}/user/{sweet_id}/profile"
        async with self._session.get(user_url, headers={
            "Authorization": f"Bearer {await self._get_access_token()}"
        }) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                if e.status == 400: # Invalid sweet ID
                    raise DeceiveIncApiResponseError(e.status, f"The provided Sweet ID {sweet_id} is invalid.")
                elif e.status == 401: # The token needs to be refreshed and tried again
                    if retry: # If we've already tried refreshing the token, throw error
                        raise DeceiveIncApiResponseError(e.status, "The access token is invalid.")
                    await self._refresh_access_token()
                    return await self.get_user(sweet_id, True)
                elif e.status == 404: # User not found
                    raise DeceiveIncApiResponseError(e.status, f"The user with Sweet ID {sweet_id} was not found.")
            data = await response.json()
            print(json.dumps(data))
            return SweetUser(sweet_id, data["displayName"],
                             data["notASkillRank"],
                             data["progression"]["Account"]["level"] if not None else None)
    
    async def upgrade_user_partial(self, user_partial: SweetUserPartial) -> SweetUser:
        return await self.get_user(user_partial.sweet_id)
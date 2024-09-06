import asyncio, json, aiohttp
from datetime import datetime, timedelta, timezone
from typing import Union, List, Optional
from lib.DI_API_Obj.sweet_user import SweetUserPartial, SweetUser
from lib.scrim_sqlite import DeceiveAPIAuthData, SweetUserCache

oauth_url: str = "https://community-auth.auth.us-east-1.amazoncognito.com/oauth2/token"
api_base_url: str = "https://1gy5zni8ll.execute-api.us-east-1.amazonaws.com/community/game/deceiveinc"

class DeceiveIncAPIResponseError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"DeceiveInc API returned status {status}: {message}")

class DeceiveIncAPINotFoundError(Exception):
    def __init__(self, user_id: str):
        super().__init__(f"DeceiveInc API was unable to find the user ID: {user_id}")

class DeceiveIncInvalidAPICredentialsError(Exception):
    def __init__(self):
        super().__init("Invalid API credentials were provided to the DeceiveInc API client.")

class DeceiveIncAPIClient:
    _session: Optional[aiohttp.ClientSession]
    _access_token: Optional[str]
    _token_expiration_time: Optional[datetime]
    _client_id: str
    _client_secret: str

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 session: Optional[aiohttp.ClientSession] = None):
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

    def _get_token_expiration_time(self) -> Optional[datetime]:
        return self._token_expiration_time

    def _is_token_expired(self) -> bool:
        return self._get_token_expiration_time() is None or datetime.now(timezone.utc) >= self._token_expiration_time # type: ignore
    
    async def _refresh_access_token(self) -> None:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        async with self._session.post(oauth_url, data={
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret
        }) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                if e.status == 401:
                    raise DeceiveIncInvalidAPICredentialsError()
                else:
                    raise DeceiveIncAPIResponseError(e.status, "An error occurred while refreshing the access token.")
            data = await response.json()
            self._access_token = data["access_token"]
            self._token_expiration_time = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])
            DeceiveAPIAuthData.set_auth_token(self._access_token, self._token_expiration_time)

    async def _get_access_token(self) -> Optional[str]:
        db_token_data = DeceiveAPIAuthData.get_auth_token()
        if db_token_data is not None and not DeceiveAPIAuthData.is_token_expired(db_token_data[1]):
            return db_token_data[0]
        if self._access_token is None or self._is_token_expired():
            await self._refresh_access_token()
        return self._access_token
    
    # API functions

    @staticmethod
    async def initialize(client_id: str, client_secret: str) -> "DeceiveIncAPIClient":
        out = DeceiveIncAPIClient(client_id, client_secret)
        await out._refresh_access_token()
        return out
    
    async def search_users(self, query: str, retry: bool = False, force: bool = False) -> List[SweetUserPartial]:
        '''Searches for users by name, returning a list of SweetUserPartial objects.
        ### Parameters:
        * `query` (`str`): The username to search for.
        * `retry` (`bool`, optional): Whether or not to retry the request if the access token is invalid. Defaults to `False`. By default, requests will retry once before failing.
        * `force` (`bool`, optional): Whether or not to force a refresh of the cache. Defaults to `False`.
        ### Returns:
        * `List[SweetUserPartial]`: A list of SweetUserPartial objects representing the users found.'''
        potential_users: List[SweetUserPartial] = SweetUserCache.get_user_partials_by_name(query)
        search_results_expired: bool = False
        if len(potential_users) > 0:
            for i in potential_users:
                if SweetUserCache.has_user_partial_expired(i.sweet_id):
                    search_results_expired = True
                    break
            if not search_results_expired and not force:
                return potential_users
        if self._session is None:
            self._session = aiohttp.ClientSession()
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
                        raise DeceiveIncInvalidAPICredentialsError()
                    await self._refresh_access_token()
                    return await self.search_users(query, True)
            data = await response.json()
            out = [SweetUserPartial(user["sweetId"], user["displayName"]) for user in data]
            for i in out:
                SweetUserCache.set_user_partial(i)
            return out
    
    async def get_user(self, sweet_id: str, retry: bool = False, force: bool = False) -> Optional[SweetUser]:
        # Check to see if a version of the user is in the cache and not expired.
        cached_user = SweetUserCache.get_user(sweet_id)
        if cached_user is not None and force == False:
            return cached_user
        user_url: str = f"{api_base_url}/user/{sweet_id}/profile"
        if self._session is None:
            self._session = aiohttp.ClientSession()
        async with self._session.get(user_url, headers={
            "Authorization": f"Bearer {await self._get_access_token()}"
        }) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                if e.status == 400: # Invalid sweet ID
                    raise DeceiveIncAPIResponseError(e.status, f"The provided Sweet ID {sweet_id} is invalid.")
                elif e.status == 401: # The token needs to be refreshed and tried again
                    if retry: # If we've already tried refreshing the token, throw error
                        raise DeceiveIncAPIResponseError(e.status, "The access token is invalid.")
                    await self._refresh_access_token()
                    return await self.get_user(sweet_id, True)
                elif e.status == 404: # User not found
                    raise DeceiveIncAPIResponseError(e.status, f"The user with Sweet ID {sweet_id} was not found.")
            data = await response.json()
            sw = SweetUser.from_api_response(sweet_id, data)
            SweetUserCache.set_user(sw)
            return sw
    
    async def upgrade_user_partial(self, user_partial: SweetUserPartial) -> Optional[SweetUser]:
        return await self.get_user(user_partial.sweet_id)
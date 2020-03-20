import typing
import yarl
import aiohttp


class Client:
    auth: typing.Optional[dict]
    base_url: yarl.URL
    _session = None

    def __init__(self, *,
                 base_url: str,
                 auth: typing.Optional[dict] = None):
        self.auth = auth
        self.base_url = yarl.URL(base_url)

    def url_for(self, route) -> yarl.URL:
        if self.base_url.path.endswith('/'):
            if route.startswith('/'):
                new_path = self.base_url.path + route[1:]
            else:
                new_path = self.base_url.path + route
        elif route.startswith('/'):
            new_path = self.base_url.path + route
        else:
            new_path = self.base_url.path + '/' + route
        return self.base_url.with_path(new_path)

    @property
    def session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        await self.session.close()

    async def request(self, method, route, json=typing.Any):
        url = self.url_for(route)

        if method.lower() == 'get':
            async with self.session.get(url, **self.use_auth()) as res:
                return await res.json()

        if not isinstance(json, (list, dict, tuple)):
            raise ValueError('json function attribute required')

        async with self.session.post(url, **self.use_auth(), json=json) as res:
            return await res.json()

    def use_auth(self):  # pylint: disable=no-self-use
        return {}

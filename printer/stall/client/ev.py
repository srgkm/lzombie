from .base import Client


class EvClient(Client):

    def __init__(self,
                 base_url: str,
                 *,
                 timeout: float = 25):
        self.state = ''
        self.timeout = timeout
        super().__init__(base_url=base_url)

    async def ping(self):
        return await self.request('get', '/ping')

    async def take(self, keys):
        res = await self.request('post',
                                 '/take',
                                 json={
                                     'keys': keys,
                                     'timeout': self.timeout,
                                     'state': self.state})
        self.state = res['state']
        return res

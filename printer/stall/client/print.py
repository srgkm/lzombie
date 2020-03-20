from .base import Client


class PrintClient(Client):
    def use_auth(self):
        res = super().use_auth()

        if 'headers' not in res:
            res['headers'] = {}

        if self.auth:
            res['headers']['Authorization'] = 'token ' + self.auth
        return res

    async def ping(self):
        return await self.request('get', '/ping')

    async def task_list(self):
        return await self.request('post', '/task/list', json={})

    async def task_raw(self, task_id):
        return await self.request('post',
                                  '/task/raw',
                                  json={'task_id': task_id})

    async def task_rm(self, task_id):
        return await self.request('post',
                                  '/task/rm',
                                  json={'task_id': task_id})

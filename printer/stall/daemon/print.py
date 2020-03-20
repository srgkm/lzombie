import asyncio
import logging
import base64
import subprocess

from stall.client.ev import EvClient
from stall.client.print import PrintClient

logging.basicConfig(
    level='DEBUG',
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


class PrintDaemon:
    def __init__(self,
                 *,
                 event_url: str,
                 event_timeout: float = 25,
                 print_client_url: str,
                 print_client_token: str,
                 store_id: str):

        self.event_url = event_url
        self.event_timeout = event_timeout
        self.print_client_url = print_client_url
        self.print_client_token = print_client_token
        self.is_run = False
        self.store_id = store_id

        self.ev = EvClient(base_url=self.event_url,
                           timeout=self.event_timeout)
        self.pc = PrintClient(base_url=self.print_client_url,
                              auth=self.print_client_token)
        self.atexit = None

    # pylint: disable=unused-argument
    async def print(self, target, file_type, document):
        """
            Функция выполняет собственно печать на принтере
        """
        if isinstance(document, str):
            document = document.encode()

        raw_document = base64.b64decode(document)
        proc = subprocess.Popen(('lpr', '-P', target), stdin=subprocess.PIPE)
        try:
            outs, errs = proc.communicate(timeout=15, input=raw_document)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        if proc.returncode:
            log.error(f'невозможно напечтать {target}')
            for line in outs.split('\n') + errs.split('\n'):
                log.error('#  %s', line)
        else:
            log.debug(f'На принтер {target} отправлено задание на печать')

    async def ping(self):
        if not self.is_run:
            return False

        pc = await self.pc.ping()
        if not pc:
            return False
        if pc['code'] != 'OK':
            return False

        ev = await self.ev.ping()
        if not ev:
            return False
        return ev['code'] == 'OK'

    async def run(self, atrun=None, atexit=None):
        self.is_run = True
        self.atexit = asyncio.get_event_loop().create_future()

        while self.is_run:
            log.debug('цикл')
            events = await self.ev.take([['print', 'store', self.store_id]])

            log.info(events)

            if events['code'] == 'INIT':
                if atrun:
                    atrun.set_result(True)

            if events['events']:
                log.debug('Получены события о печати %s', events['events'])
                await self._check_tasks()
                continue

            if events['code'] in ('INIT', 'MAYBE_DATA_LOST'):
                await self._check_tasks()
                continue
        if self.atexit:
            self.atexit.set_result(True)
        if atexit:
            atexit.set_result(True)

    async def stop(self):
        log.debug('Останавливаем демон')
        self.is_run = False
        if self.atexit:
            log.debug('Ожидаем завершения демона')
            await self.atexit
        self.atexit = None

    async def _check_tasks(self):
        while True:
            log.debug('Получаем задания на печать')
            tasks = await self.pc.task_list()

            log.info('Tasks: ', tasks)

            if tasks['code'] != 'OK':
                if tasks['code'] == 'ROUTE_NOT_FOUND':
                    log.error('не найден роут на printer-client')
                    break
                continue
            if not tasks['tasks']:
                break
            for task_id in tasks['tasks']:

                raw = await self.pc.task_raw(task_id)

                if raw['code'] != 'OK':
                    continue

                task = raw['task']
                log.debug('Печатаем задачу %s (.%s -> %s)',
                          task_id,
                          task['type'],
                          task['target'])

                try:
                    await self.print(
                        task['target'],
                        task['type'],
                        task['document']
                    )
                except Exception as exc:
                    log.error('Print task failed: %s: %s', exc, task)
                await self.pc.task_rm(task_id)

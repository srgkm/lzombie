#!/usr/bin/env python3

import asyncio
import argparse
import logging
import sys
import yaml

from stall.daemon.print import PrintDaemon

logging.basicConfig(
    level='DEBUG',
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        type=str,
        help='Конфигурация клиента'
    )

    args = parser.parse_args()

    if not args.config:
        print('usage printer.py --config file.yaml')
        sys.exit(0)

    with open(args.config, 'r') as fh:
        cfg = yaml.load(fh, Loader=yaml.FullLoader)

    cfg = cfg['client']

    daemon = PrintDaemon(
        event_url=cfg['event_url'],
        print_client_url=cfg['url'],
        print_client_token=cfg['token'],
        store_id=cfg['store_id'],
    )

    await daemon.run()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

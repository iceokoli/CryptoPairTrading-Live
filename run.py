import asyncio
import json
import logging
import datetime
import os
import sys
from pathlib import Path
from argparse import ArgumentParser

from account import Account
from strategy import PairsStrategy
from engine import Engine


def configure_logger(dir) -> logging.Logger:

    if sys.platform == "darwin":
        logging.basicConfig(
            format="%(asctime)s:%(levelname)s: - %(message)s",
            level=logging.INFO,
        )
    else:
        logging.basicConfig(
            format="%(asctime)s:%(levelname)s: - %(message)s",
            level=logging.INFO,
            filemode="a",
            filename=f"{dir}/logging/logging-{datetime.datetime.now().date()}.txt",
        )

    return logging.getLogger(__name__)


def handle_input() -> str:

    parser = ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["DEV", "PROD"])
    args = parser.parse_args()

    return args.mode


def get_prerequesite_data(dir) -> dict:

    with open(f"{dir}/aggregates.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":

    dir = str(Path(__file__).parent)

    logger = configure_logger(dir)
    mode = handle_input()

    client_id = os.getenv("BSID")
    auth = {
        "secret": bytes(os.getenv("BSSECRET"), "utf-8"),
        "key": os.getenv("BSKEY"),
    }
    data_feed = "wss://ws.bitstamp.net/"

    agg = get_prerequesite_data(dir)

    acc = Account(auth, client_id, logger, mode)
    strat = PairsStrategy(
        account=acc, enter_trigger=1, exit_trigger=0.1, agg_data=agg, logger=logger
    )
    eng = Engine(data_feed, strat, logger)

    loop = asyncio.get_event_loop()
    loop.create_task(eng.run())
    loop.run_forever()

import asyncio
import json
import logging
import datetime
import os
import sys
from pathlib import Path
from argparse import ArgumentParser

from live.accounts import BitstampAccount, BinanceAccount
from live.feeds import BitstampDataFeed
from live import PairsStrategy, Engine


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
    parser.add_argument("--exchange", required=True, choices=["Bitstamp", "Binance"])
    args = parser.parse_args()

    return args.mode, args.exchange


def get_prerequesite_data(dir) -> dict:

    with open(f"{dir}/pretrade/aggregates.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":

    dir = str(Path(__file__).parent)

    logger = configure_logger(dir)
    mode, exchange = handle_input()

    agg = get_prerequesite_data(dir)

    if exchange == "Bitstamp":
        client_id = os.getenv("BSID")
        auth = {
            "secret": bytes(os.getenv("BSSECRET"), "utf-8"),
            "key": os.getenv("BSKEY"),
        }
        data_feed = BitstampDataFeed(logger)
        acc = BitstampAccount(auth, client_id, logger, mode)
    elif exchange == "Binance":
        logger.info("Binance exchange not set up yet")
        auth = {
            "secret": os.getenv(f"BSECRET"),
            "key": os.getenv(f"BKEY"),
        }
        acc = BinanceAccount(auth, mode, logger)
        txt = asyncio.run(acc.balance)
        quit()

    strat = PairsStrategy(
        account=acc, enter_trigger=1, exit_trigger=0.1, agg_data=agg, logger=logger
    )
    eng = Engine(data_feed, strat, logger)
    loop = asyncio.get_event_loop()
    loop.create_task(eng.run())
    loop.run_forever()

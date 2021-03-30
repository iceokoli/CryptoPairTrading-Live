import asyncio
import json
import logging
import datetime
import os
import sys
from pathlib import Path
from argparse import ArgumentParser

import aiohttp

from account import Account
from strategy import PairsStrategy
from utility import estimate_mid_price

dir = str(Path(__file__).parent)

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


logger = logging.getLogger(__name__)

btc_mid, eth_mid = float(), float()


def handle_input():

    parser = ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["DEV", "PROD"])
    args = parser.parse_args()

    return args.mode


def store_data(mid, channel):

    global btc_mid, eth_mid

    if channel == "order_book_btcgbp":
        btc_mid = mid
    elif channel == "order_book_ethgbp":
        eth_mid = mid


async def on_open(ws):
    btc_sub = json.dumps(
        {"event": "bts:subscribe", "data": {"channel": "order_book_btcgbp"}}
    )
    eth_sub = json.dumps(
        {"event": "bts:subscribe", "data": {"channel": "order_book_ethgbp"}}
    )
    await ws.send_str(btc_sub)
    await ws.send_str(eth_sub)
    logger.info("### subscribed ###")


async def on_message(ws, message, strat):

    global btc_mid, eth_mid

    try:
        data = json.loads(message.data)
        event = data["event"]
        channel = data["channel"]
        logger.info(f"### received message: {event}, {channel} ###")

        if event != "data":
            return

        mid = estimate_mid_price(data["data"])
        store_data(mid, channel)

        if eth_mid and btc_mid:
            s = strat.calc_spread(btc_mid, eth_mid)
            await strat.evaluate_action(s)
            btc_mid, eth_mid = float(), float()

    except Exception as error:
        logger.info(error)
        ws.close()


async def main():

    mode = handle_input()

    client_id = os.getenv("BSID")
    auth = {
        "secret": bytes(os.getenv("BSSECRET"), "utf-8"),
        "key": os.getenv("BSKEY"),
    }

    with open(f"{dir}/aggregates.json", "r") as f:
        agg = json.load(f)

    acc = Account(auth, client_id, logger, mode)

    strat = PairsStrategy(
        account=acc, enter_trigger=1, exit_trigger=0.1, agg_data=agg, logger=logger
    )

    data_feed = "wss://ws.bitstamp.net/"

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(data_feed) as ws:
            await on_open(ws)
            async for msg in ws:
                await on_message(ws, msg, strat)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

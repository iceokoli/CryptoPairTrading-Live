import json
import time
import ssl
import logging
import datetime
import os
from pathlib import Path

import websocket

from account import Account
from strategy import PairsStrategy
from utility import estimate_mid_price

dir = str(Path(__file__).parent)

logging.basicConfig(
    format="%(asctime)s:%(levelname)s: - %(message)s",
    level=logging.INFO,
    # filemode="a",
    # filename=f"{dir}/logging/logging-{datetime.datetime.now().date()}.txt",
)

logger = logging.getLogger(__name__)

btc_mid, eth_mid = float(), float()

client_id = os.getenv("BISID")
auth = {
    "secret": bytes(os.getenv("BSSECRET"), "utf-8"),
    "key": os.getenv("BSKEY"),
}

with open(f"{dir}/aggregates.json", "r") as f:
    agg = json.load(f)

acc = Account(auth, client_id, logger)

strat = PairsStrategy(
    account=acc, enter_trigger=1, exit_trigger=0.1, agg_data=agg, logger=logger
)


def store_data(mid, channel):

    global btc_mid, eth_mid

    if channel == "order_book_btcgbp":
        btc_mid = mid
    elif channel == "order_book_ethgbp":
        eth_mid = mid
    # elif channel == "order_book_ethbtc":
    #     cross_mid = mid


def on_open(ws):
    btc_sub = json.dumps(
        {"event": "bts:subscribe", "data": {"channel": "order_book_btcgbp"}}
    )
    eth_sub = json.dumps(
        {"event": "bts:subscribe", "data": {"channel": "order_book_ethgbp"}}
    )
    # cross_sub = json.dumps(
    #     {"event": "bts:subscribe", "data": {"channel": "order_book_ethbtc"}}
    # )
    ws.send(btc_sub)
    ws.send(eth_sub)
    logger.info("### subscribed ###")


def on_close(ws):

    logger.info("### closed ###")


def on_message(ws, message):

    global btc_mid, eth_mid

    try:
        data = json.loads(message)
        event = data["event"]
        channel = data["channel"]
        logger.info(f"### received message: {event}, {channel} ###")

        if event != "data":
            return

        mid = estimate_mid_price(data["data"])
        store_data(mid, channel)

        if eth_mid and btc_mid:
            s = strat.calc_spread(btc_mid, eth_mid)
            strat.evaluate_action(s)
            btc_mid, eth_mid = float(), float()

    except Exception as error:
        logger.info(error)
        ws.close()


def on_error(ws, error):
    logger.info(error)


if __name__ == "__main__":

    data_feed = "wss://ws.bitstamp.net/"
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        data_feed,
        on_close=on_close,
        on_error=on_error,
        on_open=on_open,
        on_message=on_message,
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

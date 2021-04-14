import json


class BitstampDataFeed:

    url = "wss://ws.bitstamp.net/"

    def __init__(self, logger) -> None:
        self.logger = logger

    async def on_open(self, ws) -> None:
        btc_sub = json.dumps(
            {"event": "bts:subscribe", "data": {"channel": "order_book_btcgbp"}}
        )
        eth_sub = json.dumps(
            {"event": "bts:subscribe", "data": {"channel": "order_book_ethgbp"}}
        )
        await ws.send_str(btc_sub)
        await ws.send_str(eth_sub)
        self.logger.info("### subscribed ###")
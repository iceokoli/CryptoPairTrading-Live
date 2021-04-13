import json

import aiohttp


class Engine:
    def __init__(self, feed, strategy, logger) -> None:

        self.strategy = strategy
        self.logger = logger
        self.feed = feed
        self.cache = {"btc_mid": float(), "eth_mid": float()}

    @staticmethod
    def estimate_mid_price(data) -> float:

        highest_bid = float(data["bids"][0][0])
        lowest_ask = float(data["asks"][0][0])
        mid = (lowest_ask + highest_bid) / 2

        return mid

    def store_data(self, mid, channel) -> None:

        if channel == "order_book_btcgbp":
            self.cache["btc_mid"] = mid
        elif channel == "order_book_ethgbp":
            self.cache["eth_mid"] = mid

    async def on_message(self, ws, message) -> None:

        try:
            data = json.loads(message.data)
            event = data["event"]
            channel = data["channel"]
            self.logger.info(f"### received message: {event}, {channel} ###")

            if event != "data":
                return

            mid = self.estimate_mid_price(data["data"])
            self.store_data(mid, channel)

            btc_mid = self.cache["btc_mid"]
            eth_mid = self.cache["eth_mid"]
            strat = self.strategy

            if eth_mid and btc_mid:
                s = strat.calc_spread(btc_mid, eth_mid)
                await strat.evaluate_action(s)
                self.cache = {"btc_mid": float(), "eth_mid": float()}

        except Exception as error:
            self.logger.info(error)
            ws.close()

    async def run(self) -> None:

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.feed.url) as ws:
                await self.feed.on_open(ws)
                async for msg in ws:
                    await self.on_message(ws, msg)

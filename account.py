import aiohttp
import hmac
import hashlib
import time


class Account:
    def __init__(self, auth, customer_id, logger, mode):
        self.auth = auth
        self.customer_id = customer_id
        self.logger = logger
        self.mode = mode

    @property
    async def balance(self):
        _url = "https://www.bitstamp.net/api/v2/balance/"

        nonce = int(time.time() * 1000)
        message = str(nonce) + self.customer_id + self.auth["key"]
        signature = (
            hmac.new(
                self.auth["secret"],
                msg=message.encode("utf-8"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper(),
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _url,
                data={"key": self.auth["key"], "signature": signature, "nonce": nonce},
            ) as responce:
                return await responce.json()

    async def order(self, side, currency_pair, amount):

        if self.mode == "DEV":
            return f"{side} {amount} {currency_pair}"

        _url = f"https://www.bitstamp.net/api/v2/{side}/instant/{currency_pair}/"

        nonce = int(time.time() * 1000)
        message = str(nonce) + self.customer_id + self.auth["key"]
        signature = (
            hmac.new(
                self.auth["secret"],
                msg=message.encode("utf-8"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper(),
        )
        if side == "buy":
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    _url,
                    data={
                        "key": self.auth["key"],
                        "signature": signature,
                        "nonce": nonce,
                        "amount": amount,
                    },
                ) as responce:
                    result = await responce.json()
        elif side == "sell":
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    _url,
                    data={
                        "key": self.auth["key"],
                        "signature": signature,
                        "nonce": nonce,
                        "amount": amount,
                        "amount_in_counter": False,
                    },
                ) as responce:
                    result = await responce.json()

        return result

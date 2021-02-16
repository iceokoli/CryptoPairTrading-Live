import requests
import hmac
import hashlib
import time


class Account:
    def __init__(self, auth, customer_id, logger):
        self.auth = auth
        self.customer_id = customer_id
        self.logger = logger

    @property
    def balance(self):
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

        r = requests.post(
            _url, data={"key": self.auth["key"], "signature": signature, "nonce": nonce}
        )
        return r.json()

    def order(self, side, currency_pair, amount):
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
            r = requests.post(
                _url,
                data={
                    "key": self.auth["key"],
                    "signature": signature,
                    "nonce": nonce,
                    "amount": amount,
                },
            )
        elif side == "sell":
            r = requests.post(
                _url,
                data={
                    "key": self.auth["key"],
                    "signature": signature,
                    "nonce": nonce,
                    "amount": amount,
                    "amount_in_counter": False,
                },
            )

        return r.json()

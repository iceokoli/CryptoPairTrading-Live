import aiohttp
import time
import hmac
import hashlib
import urllib


class BinanceAccount:
    def __init__(self, auth, mode, logger) -> None:
        self.auth = auth
        self.logger = logger
        self.balance_cache = None
        self.balance_last_checked = None
        self.base_url = "https://api.binance.com"
        self.mode = mode

    @property
    async def balance(self) -> dict:

        _ctime = time.time()

        if self.balance_last_checked and (_ctime - self.balance_last_checked) < 10:
            self.logger.info("Returning cached balance")
            return self.balance_cache

        _endpoint = "/sapi/v1/margin/account?"
        _params = {"timestamp": int(_ctime * 1000)}
        _secret = bytes(self.auth["secret"].encode("utf-8"))
        _message = urllib.parse.urlencode(_params)
        _signature = (
            hmac.new(
                _secret,
                msg=_message.encode("utf-8"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )
        _url = self.base_url + _endpoint
        _url += _message
        _url += f"&signature={_signature}"

        async with aiohttp.ClientSession() as session:
            session.headers.update({"X-MBX-APIKEY": self.auth["key"]})

            async with session.get(_url) as r:
                self.balance_last_checked = _ctime
                result = await r.json()

        self.balance_cache = result

        return result

    def order(self):
        pass

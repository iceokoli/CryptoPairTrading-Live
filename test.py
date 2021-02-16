import logging

from account import Account


def get_balance(acc):
    balance = acc.balance
    return (balance["btc_balance"], balance["eth_balance"])


def test_buy_instant_order(acc):

    btc_balance = round(float(get_balance(acc)[0]) / 2, 8)
    txt = acc.order(
        "buy",
        "ethbtc",
        btc_balance,
    )

    return txt


def test_sell_instant_order(acc):

    eth_balance = get_balance(acc)[1]
    txt = acc.order(
        "sell",
        "ethbtc",
        eth_balance,
    )

    return txt


if __name__ == "__main__":

    client_id = "sczk3503"
    auth = {
        "secret": b"Zg3pJaQEWqUTA1uaHt4cBAWJE33zrD99",
        "key": "wzVleu1HEjVZH7F4IxbxWbfukCeU4KXA",
    }
    logger = logging.getLogger(__name__)
    acc = Account(auth, client_id, logger)

    print(test_buy_instant_order(acc))

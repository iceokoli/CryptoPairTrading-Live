import datetime
import json
import yfinance as yf
from pathlib import Path
from argparse import ArgumentParser
from statsmodels.regression.rolling import RollingOLS


def get_args():
    """ Handle Argument parsing"""

    parser = ArgumentParser()
    parser.add_argument("--days", required=True)

    args = parser.parse_args()

    return int(args.days)


def grab_data(ticker, start, end):

    t = yf.Ticker(ticker)

    return t.history(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
    )


def calc_aggregates(data, days):

    model = RollingOLS(data["BTC-GBP"].Close, data["ETH-GBP"].Close, window=days)
    result = model.fit()
    rolling_beta = result.params.Close
    rolling_beta.name = "beta"

    spread = data["BTC-GBP"].Close - rolling_beta * data["ETH-GBP"].Close

    return {
        "mean": spread.mean(),
        "std": spread.std(),
        "beta": rolling_beta.mean(),
    }


if __name__ == "__main__":

    pairs = ["BTC-GBP", "ETH-GBP"]

    days = get_args()

    end = datetime.datetime.now() - datetime.timedelta(1)
    start = end - datetime.timedelta(2 * days)

    data = {}
    for ticker in pairs:
        data[ticker] = grab_data(ticker, start, end)

    aggs = calc_aggregates(data, days)

    with open("aggregates.json", "w") as f:
        json.dump(aggs, f)

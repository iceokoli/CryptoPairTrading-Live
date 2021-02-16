def estimate_mid_price(data):

    highest_bid = float(data["bids"][0][0])
    lowest_ask = float(data["asks"][0][0])
    mid = (lowest_ask + highest_bid) / 2

    return mid

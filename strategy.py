class PairsStrategy:
    def __init__(self, account, enter_trigger, exit_trigger, agg_data, logger):
        self.account = account
        self.enter = enter_trigger
        self.exit = exit_trigger
        self.agg_data = agg_data
        self.spread_prev = 0
        self.cycle = 0
        self.logger = logger
        self.balance = 0
        self.execute = 0

    def calc_spread(self, btc_price, eth_price):

        self.cycle += 1
        spread = btc_price - self.agg_data["beta"] * eth_price
        norm_spread = (spread - self.agg_data["mean"]) / self.agg_data["std"]

        return norm_spread

    @property
    def in_position(self):
        if self.cycle == 1 or self.execute == 1:
            self.logger.info("Retrieving Balance ....")
            self.balance = self.account.balance
        self.logger.info(
            "checked balance, btc:{}, eth:{}".format(
                self.balance["btc_balance"], self.balance["eth_balance"]
            )
        )

        if (
            float(self.balance["btc_balance"]) < 1e-5
            or float(self.balance["eth_balance"]) < 1e-4
        ):
            return True
        else:
            return False

    def reversed(self, spread):

        if self.balance["eth_balance"] == 0 and spread > self.enter:

            return True

        elif self.balance["btc_balance"] == 0 and spread < -self.enter:

            return True

        else:

            return False

    def evaluate_action(self, spread):

        if self.in_position:
            if (abs(spread) < self.exit) or self.reversed(spread):
                if int(self.balance["btc_balance"]) == 0:
                    amount = round(float(self.balance["eth_balance"]) / 2, 8)
                    txt = self.account.order("sell", "ethbtc", amount)
                    self.logger.info(txt)
                    self.execute = 1
                elif int(self.balance["eth_balance"]) == 0:
                    amount = round(float(self.balance["btc_balance"]) / 2, 8)
                    txt = self.account.order("buy", "ethbtc", amount)
                    self.logger.info(txt)
                    self.execute = 1
            else:
                self.logger.info("Do nothing")
                self.execute = 0
        else:
            if spread > self.enter:
                amount = self.balance["btc_balance"]
                txt = self.account.order("buy", "ethbtc", amount)
                self.logger.info(txt)
                self.execute = 1
            elif spread < -self.enter:
                amount = self.balance["eth_balance"]
                txt = self.account.order("sell", "ethbtc", amount)
                self.logger.info(txt)
                self.execute = 1
            else:
                self.logger.info("Do nothing")
                self.execute = 0

class PairsStrategy:
    def __init__(
        self, account, enter_trigger, exit_trigger, agg_data, logger, margin
    ) -> None:
        self.account = account
        self.enter = enter_trigger
        self.exit = exit_trigger
        self.agg_data = agg_data
        self.spread_prev = 0
        self.cycle = 0
        self.logger = logger
        self.balance = 0
        self.execute = 0
        self.margin = margin

    def calc_spread(self, btc_price, eth_price) -> float:
        self.cycle += 1
        spread = btc_price - self.agg_data["beta"] * eth_price
        norm_spread = (spread - self.agg_data["mean"]) / self.agg_data["std"]

        return norm_spread

    @property
    async def in_position(self) -> bool:
        self.logger.info("Retrieving Balance ....")
        self.balance = await self.account.balance
        self.logger.info(
            "checked balance, btc:{}, eth:{}".format(
                self.balance["btc_balance"], self.balance["eth_balance"]
            )
        )

        if self.margin:
            return await self._in_position_margin()
        else:
            return await self._in_position_nomargin()

    async def _in_position_margin(self) -> bool:
        pass

    async def _in_position_nomargin(self) -> bool:
        if (
            float(self.balance["btc_balance"]) < 1e-5
            or float(self.balance["eth_balance"]) < 1e-4
        ):
            return True
        else:
            return False

    def reversed(self, spread) -> bool:
        if self.margin:
            return self._reversed_margin(spread)
        else:
            return self._reversed_nomargin(spread)

    def _reversed_nomargin(self, spread) -> bool:
        if float(self.balance["eth_balance"]) == 0 and spread >= self.enter:
            return True
        elif float(self.balance["btc_balance"]) == 0 and spread <= -self.enter:
            return True
        else:
            return False

    def _reversed_margin(self, spread) -> bool:
        pass

    async def trade(self, long, short) -> None:
        if self.margin:
            await self._trade_margin(long, short)
        else:
            await self._trade_nomargin(long, short)

    async def _trade_margin(self, long, short):
        pass

    async def _trade_nomargin(self, long, short) -> None:
        amount = self.balance["f{short}_balance"]
        direction = "buy" if long + short == "ethbtc" else "sell"
        txt = await self.account.order(direction, "ethbtc", amount)
        self.logger.info(txt)
        self.execute = 1

    async def close_position(self) -> None:
        if self.margin:
            await self._close_position_margin()
        else:
            await self._close_position_nomargin()

    async def _close_position_margin(self) -> None:
        pass

    async def _close_position_nomargin(self) -> None:
        if float(self.balance["btc_balance"]) == 0:
            amount = round(float(self.balance["eth_balance"]) / 2, 8)
            txt = await self.account.order("sell", "ethbtc", amount)
            self.logger.info(txt)
            self.execute = 1

        elif float(self.balance["eth_balance"]) == 0:
            amount = round(float(self.balance["btc_balance"]) / 2, 8)
            txt = await self.account.order("buy", "ethbtc", amount)
            self.logger.info(txt)
            self.execute = 1

    async def evaluate_action(self, spread) -> None:
        self.logger.info("Spread: {:.2f}".format(spread))

        if await self.in_position:
            if (abs(spread) < self.exit) or self.reversed(spread):
                await self.close_position()
            else:
                self.logger.info("Do nothing")
                self.execute = 0
        else:
            if spread >= self.enter:
                await self.trade(long="eth", short="btc")
            elif spread <= -self.enter:
                await self.trade(long="btc", short="eth")
            else:
                self.logger.info("Do nothing, spread: {:.2f}".format(spread))
                self.execute = 0

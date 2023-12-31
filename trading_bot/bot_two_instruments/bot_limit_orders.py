import typing as tp
import time
import asyncio

from dataclasses import dataclass

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
# from utils.error_checkers import check_grid_direction

from constants import *

from .base_bot_two_instruments import BaseTradingBotTwoInstruments
# from .grid_controller_two_instruments import GridControllerTwoInstruments

from .grid_controller_two_instruments import GridControllerTwoInstruments, GridEntry

import utils
from utils import trade_utils, InstrPrices

config = utils.load_config('config.yaml')


@dataclass
class ORDER_TYPES:
    LIMIT = 'limit'
    MARKET = 'market'


@dataclass
class BatchLimitOrderInputs:
    order1_id: str
    order2_id: str
    instr1_amount: float
    instr2_amount: float
    instr1_prices: InstrPrices
    instr2_prices: InstrPrices
    spread_price: float
    instr1_side: str
    instr2_side: str


@dataclass
class HandleBatchOrdersExecutionOutput:
    status: bool
    order1_id: tp.Union[str, None]
    order2_id: tp.Union[str, None]
    order1_type: tp.Union[ORDER_TYPES, None]
    order2_type: tp.Union[ORDER_TYPES, None]


class TradingBotTwoInstrumentsLimitOrders(BaseTradingBotTwoInstruments):
    def __init__(self,
                 conn: tp.Union[DeribitConnection,
                                dYdXConnection],
                 telegram_bot: TelegramNotifier):
        super().__init__(conn=conn, telegram_bot=telegram_bot)

        # we store here because here we create limit orders
        self.instr1_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr1_name]
        self.instr2_ndigits_rounding = NDIGITS_PRICES_ROUNDING[self.instr2_name]

        self.grid_controller = GridControllerTwoInstruments()

    async def check_batch_orders_fullfilled(self, order1_id, order2_id) -> bool:
        pass
        return False

    @staticmethod
    def calculate_spread_deviation(_spread_price: float, spread_price: float) -> float:
        return abs((_spread_price - spread_price) / _spread_price)

    async def handle_batch_orders_executions(self,
                                             batchLimitOrderInputs: BatchLimitOrderInputs) -> HandleBatchOrdersExecutionOutput:
        # TODO: add check() that order1.side == side(grid_direction)
        # currently we assume that order1.side == side(grid_direction) and order2.side == side(anti_grid_direction)
        handleBatchOrdersExecutionOutput = HandleBatchOrdersExecutionOutput(
            status=True, order1_id=None, order2_id=None, order1_type=None, order2_type=None)
        order1_done = False
        order2_done = False
        print('orders ids')
        print(batchLimitOrderInputs.order1_id, batchLimitOrderInputs.order2_id)
        # handleBatchOrdersExecutionOutput.order1_id = batchLimitOrderInputs.order1_id
        # handleBatchOrdersExecutionOutput.order2_id = batchLimitOrderInputs.order2_id
        try:
            while (order1_done != True) or (order2_done != True):
                order1 = await self.conn.get_order(order_id=batchLimitOrderInputs.order1_id)
                order2 = await self.conn.get_order(order_id=batchLimitOrderInputs.order2_id)

                order1_state = order1['order_state']
                order2_state = order2['order_state']
                (_, _, spread_price) = await self.get_instr_prices_and_spread()

                if order1_state == 'filled':
                    order1_done = True
                if order2_state == 'filled':
                    order2_done = True

                if order1_done:
                    handleBatchOrdersExecutionOutput.order1_type = ORDER_TYPES.LIMIT
                    handleBatchOrdersExecutionOutput.order1_id = batchLimitOrderInputs.order1_id
                    if order2_done:
                        handleBatchOrdersExecutionOutput.order2_type = ORDER_TYPES.LIMIT
                        handleBatchOrdersExecutionOutput.order2_id = batchLimitOrderInputs.order2_id
                    elif self.calculate_spread_deviation(_spread_price=batchLimitOrderInputs.spread_price,
                                                         spread_price=spread_price) > self.grid_step*self.two_instr_max_spread_price_deviation:
                        print('canceling one order and execute as market')
                        print(order1_done, order2_done)
                        # we should cancel limit order and only then execute market order
                        await self.conn.cancel_order(order_id=batchLimitOrderInputs.order2_id)
                        order2 = await self.conn.execute_market_order(
                            instrument_name=self.instr2_name,
                            amount=batchLimitOrderInputs.instr2_amount,
                            side=batchLimitOrderInputs.instr2_side
                        )
                        order2_done = True
                        handleBatchOrdersExecutionOutput.order2_type = ORDER_TYPES.MARKET
                        handleBatchOrdersExecutionOutput.order2_id = order2['order_id']
                elif order2_done:
                    handleBatchOrdersExecutionOutput.order2_type = ORDER_TYPES.LIMIT
                    handleBatchOrdersExecutionOutput.order2_id = batchLimitOrderInputs.order2_id
                    if self.calculate_spread_deviation(_spread_price=batchLimitOrderInputs.spread_price,
                                                       spread_price=spread_price) > self.grid_step*self.two_instr_max_spread_price_deviation:
                        print('canceling one order and execute as market')
                        print(order1_done, order2_done)
                        # we should cancel limit order and only then execute market order
                        await self.conn.cancel_order(order_id=batchLimitOrderInputs.order1_id)
                        order1 = await self.conn.execute_market_order(
                            instrument_name=self.instr2_name,
                            amount=batchLimitOrderInputs.instr2_amount,
                            side=batchLimitOrderInputs.instr2_side
                        )
                        order1_done = True
                        handleBatchOrdersExecutionOutput.order1_type = ORDER_TYPES.MARKET
                        handleBatchOrdersExecutionOutput.order1_id = order1['order_id']
                else:
                    # means order1_done == False and order2_done == False
                    if self.calculate_spread_deviation(_spread_price=batchLimitOrderInputs.spread_price,
                                                       spread_price=spread_price) > self.grid_step*self.two_instr_max_spread_price_deviation:
                        print('canceling two orders. Statuses:',
                              order1_done, order2_done)
                        await self.conn.cancel_order(order_id=batchLimitOrderInputs.order1_id)
                        await self.conn.cancel_order(order_id=batchLimitOrderInputs.order2_id)
                        handleBatchOrdersExecutionOutput.status = False
                        break
                await asyncio.sleep(0.5)

        except Exception as err:
            await self.telegram_bot.simple_send_message(f"{err}")
        print('finished while cycle', order1_done, order2_done)
        print(handleBatchOrdersExecutionOutput)

        return handleBatchOrdersExecutionOutput

    async def create_batch_limit_orders(self,
                                        prices_instr1: InstrPrices,
                                        prices_instr2: InstrPrices,
                                        grid_order_type: tp.Literal['limit', 'take_profit']) -> HandleBatchOrdersExecutionOutput:
        try:
            instr1_amount = trade_utils.get_size_to_trade(instr_name=self.instr1_name,
                                                          instr_prices=prices_instr1,
                                                          direction=self.grid_direction,
                                                          kind=self.kind1,
                                                          config_size=self.order_size)
            instr2_amount = trade_utils.get_size_to_trade(instr_name=self.instr2_name,
                                                          instr_prices=prices_instr2,
                                                          direction=self.anti_grid_direction,
                                                          kind=self.kind2,
                                                          config_size=self.order_size)
            spread_price = utils.calculate_spread_from_two_instr_prices(instr1_bid_ask=prices_instr1,
                                                                        instr2_bid_ask=prices_instr2,
                                                                        spread_operator=self.spread_operator,
                                                                        grid_direction=self.grid_direction)
            print('create_batch_limit_orders')
            print('instr 1 amount', instr1_amount)
            print('instr 2 amount', instr2_amount)

            # mean price because we want to increase probability that the orders will be executed
            price1 = (prices_instr1.best_bid + prices_instr1.best_ask) / 2
            price2 = (prices_instr2.best_bid + prices_instr2.best_ask) / 2
            price1 = utils.round_price(
                price=price1, instr_name=self.instr1_name)
            price2 = utils.round_price(
                price=price2, instr_name=self.instr2_name)
            print('prices')
            print('price1', price1)
            print('price2', price2)

            side1 = OrderSides.ORDER_SIDE_BUY if self.grid_direction == GridDirections.GRID_DIRECTION_LONG else OrderSides.ORDER_SIDE_SELL
            side2 = OrderSides.ORDER_SIDE_BUY if self.anti_grid_direction == GridDirections.GRID_DIRECTION_LONG else OrderSides.ORDER_SIDE_SELL

            if grid_order_type == 'take_profit':
                side1, side2 = side2, side1

            order1 = await self.conn.create_limit_order(instrument_name=self.instr1_name,
                                                        amount=instr1_amount,
                                                        price=price1,
                                                        action=side1)
            order2 = await self.conn.create_limit_order(instrument_name=self.instr2_name,
                                                        amount=instr2_amount,
                                                        price=price2,
                                                        action=side2)
            order1_id = order1['order_id']
            order2_id = order2['order_id']
            # these are possibly other orders, not the ones we just created
            handleBatchOrdersExecutionOutput = await self.handle_batch_orders_executions(
                batchLimitOrderInputs=BatchLimitOrderInputs(
                    order1_id=order1_id,
                    order2_id=order2_id,
                    instr1_amount=instr1_amount,
                    instr2_amount=instr2_amount,
                    instr1_prices=prices_instr1,
                    instr2_prices=prices_instr2,
                    spread_price=spread_price,
                    instr1_side=side1,
                    instr2_side=side2
                ))
            print('status', handleBatchOrdersExecutionOutput.status)
            print('order1_id', handleBatchOrdersExecutionOutput.order1_id)
            print('order2_id', handleBatchOrdersExecutionOutput.order2_id)
            return handleBatchOrdersExecutionOutput
        except Exception as err:
            await self.telegram_bot.simple_send_message(f"{err}")
            return HandleBatchOrdersExecutionOutput(status=False)

    async def get_instr_prices_and_spread(self) -> tp.Tuple[InstrPrices, InstrPrices, float]:
        prices_instr1 = InstrPrices(**(await self.conn.get_asset_price(instrument_name=self.instr1_name)))
        prices_instr2 = InstrPrices(**(await self.conn.get_asset_price(instrument_name=self.instr2_name)))

        spread_price = utils.calculate_spread_from_two_instr_prices(instr1_bid_ask=prices_instr1,
                                                                    instr2_bid_ask=prices_instr2,
                                                                    grid_direction=self.anti_grid_direction,
                                                                    spread_operator=self.spread_operator)
        return (prices_instr1, prices_instr2, spread_price)

    async def _prepare(self):
        # sleep until start
        await asyncio.sleep(await self.get_seconds_until_start())

        await self.conn.cancel_all_orders(instrument_name=self.instr1_name, kind=self.kind1)
        await self.conn.cancel_all_orders(instrument_name=self.instr2_name, kind=self.kind2)

        (_, _, spread_price) = await self.get_instr_prices_and_spread()

        print()
        print(spread_price)

        self.grid_controller.initialize_grid(
            spread_price=spread_price, grid_direction=self.grid_direction)

    async def run(self):
        await self._prepare()
        while True:
            async with self.lock:
                # check total take profit. If reached, then bot stops running
                # currently not working, because not clear halting condition for PERPETUALs
                # await self.check_total_take_profit()

                (instr1_bid_ask, instr2_bid_ask, spread_price) = await self.get_instr_prices_and_spread()
                # if self.grid_direction == GridDirections.GRID_DIRECTION_LONG:
                print('spread price', spread_price)
                for (level, level_info) in self.grid_controller.grid.items():
                    print(level, level_info)
                    if self.grid_direction == GridDirections.GRID_DIRECTION_LONG and (level_info.reached == False) and (level >= spread_price) or \
                            self.grid_direction == GridDirections.GRID_DIRECTION_SHORT and (level_info.reached == False) and (level <= spread_price):
                        print('creating limit orders...')
                        handleBatchOrdersExecutionOutput = await self.create_batch_limit_orders(prices_instr1=instr1_bid_ask,
                                                                                                prices_instr2=instr2_bid_ask,
                                                                                                grid_order_type='limit')
                        # if creation of batch limit orders was not successful, go to next level
                        # asyncio.sleep is not needed because it is 'for' loop
                        if handleBatchOrdersExecutionOutput.status == False:
                            continue

                        self.grid_controller.update_limit_order(level=level,
                                                                order1_id=handleBatchOrdersExecutionOutput.order1_id,
                                                                order2_id=handleBatchOrdersExecutionOutput.order2_id)
                        await self.telegram_bot.send_message(
                            f'Created limit orders for level {level}. \n\n'
                            f'Order1 type: {handleBatchOrdersExecutionOutput.order1_type}.\n'
                            f'Order2 type: {handleBatchOrdersExecutionOutput.order2_type}.\n'
                            f'Current spread price: {spread_price}. \n'
                            f'Order1 price: {instr1_bid_ask.best_ask}, order2 price: {instr2_bid_ask.best_ask}')

                    elif self.grid_direction == GridDirections.GRID_DIRECTION_LONG and (level_info.reached == True) and (level_info.take_profit_level <= spread_price) or \
                            self.grid_direction == GridDirections.GRID_DIRECTION_SHORT and (level_info.reached == True) and (level_info.take_profit_level >= spread_price):
                        # it's time to execute take profit limit order and clear grid level
                        handleBatchOrdersExecutionOutput = await self.create_batch_limit_orders(prices_instr1=instr1_bid_ask,
                                                                                                prices_instr2=instr2_bid_ask,
                                                                                                grid_order_type='take_profit')
                        # if creation of batch limit orders was not successful, go to next level
                        # asyncio.sleep is not needed because it is 'for' loop
                        if handleBatchOrdersExecutionOutput.status == False:
                            continue

                        self.grid_controller.update_take_profit_order(level=level,
                                                                      order1_id=handleBatchOrdersExecutionOutput.order1_id,
                                                                      order2_id=handleBatchOrdersExecutionOutput.order2_id)
                        await self.telegram_bot.send_message(
                            f'Executed take profit orders for level {level}. \n'
                            f'Take profit level: {level_info.take_profit_level}. \n'
                            f'Order1 type: {handleBatchOrdersExecutionOutput.order1_type}.\n'
                            f'Order2 type: {handleBatchOrdersExecutionOutput.order2_type}.\n'
                            f'Current spread price: {spread_price}. \n'
                            f'Order1 price: {instr1_bid_ask.best_bid}, order2 price: {instr2_bid_ask.best_ask}')
                        # clear level
                        self.grid_controller.clear_level(level=level)

            await asyncio.sleep(1)
            # break

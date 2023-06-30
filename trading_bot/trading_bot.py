from dydx3 import Client
# from dydx3.modules.private import AuthCredentials
from telegram import Bot
# from telegram.ext import Dispatcher, CommandHandler
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL


class TradingBot:
    def __init__(self, dydx_connection, telegram_bot, config):
        self.config = config
        self.dydx_connection = dydx_connection
        self.telegram_bot = telegram_bot
        # self.dispatcher = Dispatcher(self.bot, None, workers=0)
        # self.setup_handlers()

    # def setup_handlers(self):
    #     start_handler = CommandHandler('start', self.start)
    #     self.dispatcher.add_handler(start_handler)

    # def start(self, update, context):
    #     order = self.dydx_client.private.create_order(
    #         market='COMP-USD',
    #         side='BUY',
    #         type='MARKET',
    #         size='10',
    #         price=None,
    #         time_in_force='GTC',
    #         post_only=False,
    #         client_id=None
    #     )
    #     context.bot.send_message(chat_id=update.effective_chat.id, text=str(order))

    async def run(self):

        while True:
            result = self.dydx_connection.create_market_order(
                ORDER_SIDE_BUY, '0.01')

            # await self.telegram_bot.send_message(message="Hello, World!")
            await self.telegram_bot.send_message(message=str(result))

            break
        # self.dispatcher.start_polling()

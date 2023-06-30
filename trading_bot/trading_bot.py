from dydx3 import Client
# from dydx3.modules.private import AuthCredentials
from telegram import Bot
# from telegram.ext import Dispatcher, CommandHandler


class TradingBot:
    def __init__(self, dydx_connection, telegram_bot, config):
        self.config = config
        self.dydx_client = self.create_dydx_client()
        self.bot = telegram_bot
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

    # def run(self):
    #     self.dispatcher.start_polling()

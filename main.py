import requests
import json
import time
from datetime import datetime
# from python_telegram_bot import TelegramBot, Update
# from python_telegram_bot.dispatcher import Dispatcher
# from python_telegram_bot.commands import CommandHandler

from utils import load_config


config = load_config('config.yaml')

print(config)

# dydx_connection = dYdXConnection(
#     api_key_credentials=config['api_key_credentials'], 
#     stark_private_key=config.get('stark_private_key', None)
# )

# telegram_notifier = TelegramNotifier(
#     bot_token=config['telegram']['bot_token'], 
#     chat_id=config['telegram']['chat_id']
# )

# trading_bot = TradingBot(dydx_connection, telegram_notifier, config['config'])
# trading_bot.run()

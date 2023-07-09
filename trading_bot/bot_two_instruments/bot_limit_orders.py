import typing as tp
import time
import asyncio

from telegram_bot import TelegramNotifier
from connectors import dYdXConnection, DeribitConnection
from utils import load_config, to_utc_timestamp
from constants import *

from trading_bot.base_trading_bot import BaseTradingBot


config = load_config('config.yaml')


class TradingBotTwoInstrumentsLimitOrders(BaseTradingBot):
    pass

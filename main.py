import yaml

def load_config(filename):
    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

config = load_config('config.yaml')

dydx_connection = dYdXConnection(
    api_key_credentials=config['api_key_credentials'], 
    stark_private_key=config.get('stark_private_key', None)
)

telegram_notifier = TelegramNotifier(
    bot_token=config['telegram']['bot_token'], 
    chat_id=config['telegram']['chat_id']
)

trading_bot = TradingBot(dydx_connection, telegram_notifier, config['config'])
trading_bot.run()

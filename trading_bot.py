class TradingBot:
    def __init__(self, config):
        self.config = config
        self.bot = TelegramBot(config['api_keys']['telegram'])
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        self.setup_handlers()

    def setup_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

    def start(self, update: Update):
        # TODO: Implement the start function

import telegram

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot = telegram.Bot(token=bot_token)
        self.chat_id = chat_id

    def send_message(self, message):
        self.bot.send_message(chat_id=self.chat_id, text=message)

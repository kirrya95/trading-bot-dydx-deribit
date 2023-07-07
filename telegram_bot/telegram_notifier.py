import telegram

from utils import load_config, timedelta_to_str

config = load_config('config.yaml')


class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot = telegram.Bot(token=bot_token)
        self.chat_id = chat_id

    async def account_info_two_instruments(self, current_deposit,
                                           instr1_name, instr2_name,
                                           instr1_initial_amount, instr2_initial_amount,
                                           instr1_amount, instr2_amount,
                                           working_time):

        start_deposit = config['trading_parameters']['start_deposit']

        message = f'Start deposit: {start_deposit} USD \n' \
            f'Current deposit: {current_deposit} USD (PnL: {round((current_deposit/start_deposit - 1) * 100, 8)} %)\n' \
            f'Instrument 1: {instr1_name} \n' \
            f'Instrument 2: {instr2_name} \n' \
            f'Initial amount of instrument 1: {instr1_initial_amount} \n' \
            f'Initial amount of instrument 2: {instr2_initial_amount} \n' \
            f'Current amount of instrument 1: {instr1_amount} \n' \
            f'Current amount of instrument 2: {instr2_amount} \n' \
            f'Working time: {timedelta_to_str(working_time)} \n'

        await self.send_message(message)

    async def send_message(self, message):
        account_name = config['account_name']
        platform_name = config['trading_parameters']['platform']

        message_header = f'Account: {account_name} \n' \
                         f'Platform: {platform_name}'
        message = f'{message_header}\n \n{message}'
        await self.bot.send_message(chat_id=self.chat_id, text=message)

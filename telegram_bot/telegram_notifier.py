import telegram

from utils import load_config, timedelta_to_str

config = load_config('config.yaml')


class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot = telegram.Bot(token=bot_token)
        self.chat_id = chat_id

    async def send_message(self, message, parse_mode="Markdown"):
        account_name = config['account_name']
        platform_name = config['trading_parameters']['platform']

        message_header = f'*Account:* {account_name} \n' \
                         f'*Platform*: {platform_name}'
        message = f'{message_header}\n \n{message}'
        await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode=parse_mode)

    async def account_info_one_instrument(self, current_deposit,
                                          instr_name,
                                          # instr_initial_amount,
                                          instr_amount,
                                          working_time):
        start_deposit = config['trading_parameters']['start_deposit']
        message = f'*Start deposit:* {start_deposit} USD \n' \
                  f'*Current deposit:* {current_deposit} USD (PnL: {round((current_deposit/start_deposit - 1) * 100, 8)} %)\n' \
                  f'*Current amount* of {instr_name}: {instr_amount} \n' \
                  f'*Working time:* {timedelta_to_str(working_time)} \n'

        await self.send_message(message=message)

    async def account_info_two_instruments(self, current_deposit,
                                           instr1_name, instr2_name,
                                           instr1_amount, instr2_amount,
                                           working_time):

        start_deposit = config['trading_parameters']['start_deposit']

        message = f'*Start deposit:* {start_deposit} USD \n' \
            f'*Current deposit:* {current_deposit} USD (PnL: {round((current_deposit/start_deposit - 1) * 100, 8)} %)\n' \
            f'*Current amount* of {instr1_name}: {instr1_amount} \n' \
            f'*Current amount* of {instr2_name}: {instr2_amount} \n' \
            f'*Working time:* {timedelta_to_str(working_time)} \n'

        # f'Initial amount of instrument 1: {instr1_initial_amount} \n' \
        # f'Initial amount of instrument 2: {instr2_initial_amount} \n' \

        await self.send_message(message)

    async def notify_grid_level_one_instrument(self, grid_level, instr_price, order, order_type):
        message = f"Reached *grid level* \n" \
                  f"Grid level: {grid_level} \n" \
                  f"Current instrument price: {instr_price} \n" \
                  f"Executed order: \n" \
                  f"{order} \n" \
                  f"Order type: {order_type} \n"

        await self.send_message(message)

    async def notify_take_profit_one_instrument(self, take_profit_level, instr_price, order, order_type):
        message = f"Reached *take profit* level \n" \
                  f"Take profit level: {take_profit_level} \n" \
                  f"Current instrument price: {instr_price} \n" \
                  f"Executed order: \n" \
                  f"{order} \n" \
                  f"Order type: {order_type} \n"

        await self.send_message(message)

    async def notify_grid_level_two_instruments(self, grid_level, spread_price, order1, order2, order1_type, order2_type):
        if not (order1_type == 'market' and order2_type == 'market'):
            raise ValueError('Both orders should be market orders')

        message = f"Reached *grid level* \n" \
                  f"Grid level: {grid_level} \n" \
                  f"Current spread price: {spread_price} \n" \
                  f"Executed two orders: \n" \
                  f"{order1} \n" \
                  f"{order2} \n" \
                  f"Order1 type: {order1_type} \n" \
                  f"Order2 type: {order2_type} \n"

        await self.send_message(message)

    async def notify_take_profit_two_instruments(self, take_profit_level, spread_price, order1, order2, order1_type, order2_type):
        if not (order1_type == 'market' and order2_type == 'market'):
            raise ValueError('Both orders should be market orders')

        message = f"Reached *take profit* level \n" \
                  f"Take profit level: {take_profit_level} \n" \
                  f"Current spread price: {spread_price} \n" \
                  f"Executed two orders: \n" \
                  f"{order1} \n" \
                  f"{order2} \n" \
                  f"Order1 type: {order1_type} \n" \
                  f"Order2 type: {order2_type} \n"

        await self.send_message(message)

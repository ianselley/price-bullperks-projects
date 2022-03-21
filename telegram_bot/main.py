from telebot import TeleBot
import os

from sheets import SheetBot


BOT_TOKEN = os.getenv("TELEGRAM_BULLPERKS_TOKEN")
telegram_bot = TeleBot(BOT_TOKEN)

sheet_bot = SheetBot()

def try_to_update_prices():
    try:
        dict_of_prices = sheet_bot.update_sheet()
        sheet_bot.logger.log("Precios actualizados")
    except Exception as e:
        dict_of_prices = str(e)
        sheet_bot.logger.log(str(e))

    return dict_of_prices


def send_prices(chat_id, dict_of_prices):
    if type(dict_of_prices) == dict:
        for slug, price in dict_of_prices.items():
            response = f"{slug}: {price} USD"
            telegram_bot.send_message(chat_id, response)
            print(response)
    else:
        telegram_bot.send_message(chat_id, dict_of_prices)
        print(dict_of_prices)


@telegram_bot.message_handler(commands=['start'])
def start(message):
    telegram_bot.send_message(message.chat.id, 'Hola!')
    telegram_bot.send_message(message.chat.id, 'Este bot actualiza los precios de los projectos de BullPerks que están en las hojas de Cálculo de Google.')
    telegram_bot.send_message(message.chat.id, 'Escribe o toca en /updatePrices para actualizar los precios.')


@telegram_bot.message_handler(commands=['updatePrices'])
def update_prices(message):
    chat_id = message.chat.id
    dict_of_prices = try_to_update_prices()

    send_prices(chat_id, dict_of_prices)


telegram_bot.polling()

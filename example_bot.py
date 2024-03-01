import logging
import asyncio
import re
import sys
from datetime import datetime

import requests
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.markdown import hbold

API_TOKEN = '7199296374:AAEuOcaqAXOcApWKURdY4KLADsmsofld1q8'

# API_TOKEN = '' uncomment and insert your telegram bot API key here

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


# initialising keyboard, each button will be used to start a calendar with different initial settings
kb = [
    [   # 1 row of buttons for Navigation calendar
        # where user can go to next/previous year/month
        KeyboardButton(text="O'zbek"),
        KeyboardButton(text='Rus'),
    ],
]
start_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


# when user sends `/start` command, answering with inline calendar
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.reply(f"Salom, {hbold(message.from_user.full_name)}! O'zingizga mos tilni tanlang", reply_markup=start_kb)


@dp.message(F.text =="O'zbek")
async def dialog_uz_handler(message: Message):
    await message.answer(
        "Siz o'zbek tilini tanladingiz.Instagramdagi yuklamoqchi bo'lgan video linkini kiriting"
    )


@dp.message(F.text.startswith("https://www.instagram"))
async def dialog_link_handler(message: Message):
    instagram_link = F.text
    print(instagram_link)
    #slogging.info(instagram_link)

    try:
        # Make the request
        response = requests.get(instagram_link)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        match = re.findall(r'video_url\W\W\W([-\W\w]+)\W\W\Wvideo_view_count', response.text)
        logging.info(match)

        await message.answer("Instagram link kiritildi")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making request: {e}")
        await message.answer("Bir xatolik yuz berdi, iltimos qaytadan urinib ko'ring.")


@dp.message(F.text == "Rus 🇷🇺")
async def dialog_ru_handler(message: Message):
    await message.answer(
        "Вы выбрали русский. "
    )

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

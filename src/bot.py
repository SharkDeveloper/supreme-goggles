# src/bot.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
import json
from asyncio import wait
import os
from aggregate import aggregate_data

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(f"{BOT_TOKEN=}")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hi! Send me a JSON with the aggregation parameters.")


@dp.message_handler()
async def handle_message(message: types.Message):
    try:
        input_data = json.loads(message.text)
        dt_from = input_data["dt_from"]
        dt_upto = input_data["dt_upto"]
        group_type = input_data["group_type"]

        result = await aggregate_data(dt_from, dt_upto, group_type)
        await message.reply(json.dumps(result, indent=4), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"Error: {str(e)}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

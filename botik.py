# test_bot.py
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = "8292078558:AAGKdz9_lZ6t-uXkqStchYk2YsHExnVmpCA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот работает! Напиши /sliv")

@dp.message(Command("sliv"))
async def sliv(message: types.Message, state):
    await message.answer("Режим слива активирован! Отправь мне сообщение с фото")

@dp.message(F.text)
async def echo(message: types.Message):
    await message.answer(f"Я получил: {message.text}")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

asyncio.run(main())
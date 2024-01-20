from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
import sqlite3
import datetime
import os
import time
import pytz
from dotenv import load_dotenv

local_timezone = pytz.timezone('Europe/Moscow')

load_dotenv()

db_path = "db/pressure_diary.db"

db = sqlite3.connect(db_path, check_same_thread=False)

cursor = db.cursor()

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)


@dp.message_handler(commands=['show'])
async def show_result(message: types.Message):
  cursor.execute("SELECT date FROM pressure WHERE user = ? ORDER BY date", (message.from_user.id,))
  rows = cursor.fetchall()
  full_res = []
  dates = []

  for row in rows:
    dates.append(row[0])

  res_day = set(dates)
  sorted(res_day, key=lambda x: datetime.datetime.strptime(x, "%d.%m.%Y").strftime("%d.%m.%Y"))

  for day in res_day:
    full_res.append(day)
    full_res.append("""
    """)
    cursor.execute("SELECT up_pressure, down_pressure, pulse, time, user FROM pressure WHERE date = ? AND user = ?", (day, message.from_user.id))
    res_list = cursor.fetchall()

    for res in res_list:
      full_res.append(f"{res[3]} Давление: {res[0]} на {res[1]}. Пульс: {res[2]}")

    full_res.append("""-------------
    
    """)
    
  await bot.send_message(message.from_user.id, '\n'.join(map(str, full_res)))


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await bot.send_message(message.from_user.id, """Привет! 
        Этот бот поможет вам вести дневник вашего артериального давления.
        
        Для начала просто напишите боту значения измеренного давления - сначала верхнее, затем через пробел - нижнее, затем так же через пробел - пульс.
        
        Пример - 120 80 96.
        
        Бот примет значения и сохранит их.
        
        Для того, чтобы прсмотреть все сохраненные значения за всё время, воспользуйтесь командой /show.
        
        Для того, чтобы удалить все заданные ранее значения, воспользуйтесь командой /delete""")
    

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def add_pressure(message: types.Message):
    info = message.text
    res = info.split()
    up_pressure = res[0]
    down_pressure = res[1]
    pulse = res[2]
    username = message.from_user.username
    date = datetime.datetime.today()
    time = date.strftime('%H:%M')
    day = date.strftime('%d.%m.%Y')

    cursor.execute("INSERT INTO pressure(up_pressure, down_pressure, pulse, date, time, user) VALUES (?, ?, ?, ?, ?, ?)", (up_pressure, down_pressure, pulse, day, time, username))
    db.commit()

    await bot.send_message(message.chat.id, f'Успешно записано! Давление {up_pressure} на {down_pressure}, пульс {pulse}. Зафиксировано {day} в {time} для пользователя {username}')


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
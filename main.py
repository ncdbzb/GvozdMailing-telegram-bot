import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from db import Database

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
db = Database('database.db')

startMarkup = types.InlineKeyboardMarkup(row_width=1)
startButton = types.InlineKeyboardButton(text='Участвовать', callback_data='startBtn')

startMarkup.add(startButton)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет, чтобы подтвердить участие в конкурсе, нажми кнопку Участвовать",
                         reply_markup=startMarkup)


@dp.callback_query_handler(text='startBtn')
async def start(message: types.Message):
    if db.user_exists(message.from_user.id):
        db.set_active(message.from_user.id, 1)
        await bot.send_message(message.from_user.id, 'Вы участвуете в конкурсе!'
                                                     ' Чтобы отписаться от рассылки, используй команду /unsub')
    else:
        flag = message.from_user.username
        username = flag if flag else message.from_user.first_name
        db.add_user(message.from_user.id)
        db.set_username(message.from_user.id, username)
        await bot.send_message(message.from_user.id, "Поздравляю! Ты участвуешь в конкурсе! "
                                                     "Ты подписан на рассылку о новых видео на ютуб канале."
                                                     " Если ты отпишешься от рассылки или заблокируешь бота, "
                                                     "ты будешь автоматически исключен из списка участников конкурса."
                                                     " Чтобы отписаться от рассылки, используй команду /unsub")


@dp.message_handler(commands=['unsub'])
async def unsub(message: types.Message):
    if db.user_exists(message.from_user.id):
        db.set_active(message.from_user.id, 0)
        await message.reply('Теперь вы не участвуете в конкурсе')
    else:
        await message.reply('Вы и так не участвуете в конкурсе')


@dp.message_handler(commands=['sendall'])
async def sendall(message: types.Message):
    if message.from_user.id == 746671824:
        text = message.text[9:]
        for row in db.get_users():
            try:
                await bot.send_message(row[0], text)
                if int(row[1]) != 1:
                    db.set_active(row[0], 1)
            except:
                db.set_active(row[0], 0)

        await bot.send_message(message.from_user.id, "Рассылка завершена")


@dp.message_handler()
async def send_error(message: types.Message):
    await message.reply('Такой команды нету, напишите /start для перезапуска')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

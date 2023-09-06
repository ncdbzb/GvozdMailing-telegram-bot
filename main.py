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
tg1 = types.InlineKeyboardButton(text='Gvozd🔩 плагины и киты', url=config.urls[0])
tg2 = types.InlineKeyboardButton(text='Gvozd 🔩 VST Plugins', url=config.urls[1])

startMarkup.row(tg1, tg2)
startMarkup.add(startButton)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет, чтобы подтвердить участие в конкурсе, убедись, что ты подписан на 2 телеграм канала "
                         "и нажми кнопку <b>\"Участвовать\"</b>",
                         reply_markup=startMarkup, parse_mode='html')


async def check(channels, user_id):
    for channel in channels:
        user_channel_status = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if user_channel_status["status"] == 'left':
            return False
    return True


@dp.callback_query_handler(text='startBtn')
async def start(message: types.Message):
    if db.user_exists(message.from_user.id):
        if await check(config.channels, message.from_user.id):
            db.set_active(message.from_user.id, 1)
            await bot.send_message(message.from_user.id, 'Вы участвуете в конкурсе!'
                                                         ' Чтобы отписаться от рассылки, используй команду /unsub')
        else:
            db.set_active(message.from_user.id, 0)
            await bot.send_message(message.from_user.id, 'Проверь, что ты подписан на оба телеграм'
                                                         ' канала и нажми кнопку еще раз!', reply_markup=startMarkup)
    else:
        flag = message.from_user.username
        username = flag if flag else message.from_user.first_name
        db.add_user(message.from_user.id)
        db.set_username(message.from_user.id, username)
        if await check(config.channels, message.from_user.id):
            await bot.send_message(message.from_user.id, "Поздравляю! Ты участвуешь в конкурсе! "
                                                         " Если ты заблокируешь бота или отпишешься от каналов, ты "
                                                         "будешь автоматически исключен из списка участников конкурса."
                                                         " Чтобы отписаться от рассылки, используй команду /unsub")
        else:
            db.set_active(message.from_user.id, 0)
            await bot.send_message(message.from_user.id, 'Проверь, что ты подписан на оба телеграм'
                                                         ' канала и нажми кнопку еще раз!', reply_markup=startMarkup)


@dp.message_handler(commands=['unsub'])
async def unsub(message: types.Message):
    if db.user_exists(message.from_user.id):
        db.set_active(message.from_user.id, 0)
        await message.reply('Теперь вы не участвуете в конкурсе')
    else:
        await message.reply('Вы и так не участвуете в конкурсе')


@dp.message_handler(commands=['sendall'])
async def sendall(message: types.Message):
    if message.from_user.id == config.admin_id:
        text = message.text[9:]
        for row in db.get_users():
            if int(row[1]) == 1:
                try:
                    await bot.send_message(row[0], text)
                    # if int(row[1]) != 1:
                    #     db.set_active(row[0], 1)
                except:
                    db.set_active(row[0], 0)

        await bot.send_message(message.from_user.id, "Рассылка завершена")


@dp.message_handler(commands=['getxlsx'])
async def sendall(message: types.Message):
    if message.from_user.id == config.admin_id:
        db.get_xlsx()
        await message.reply_document(open('result.xlsx', 'rb'))


@dp.message_handler()
async def send_error(message: types.Message):
    await message.reply('Такой команды нету, напишите /start для перезапуска')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

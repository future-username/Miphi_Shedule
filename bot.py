import datetime

from aiogram import Bot, executor
from aiogram.types import Message, ParseMode, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import CommandStart

from app import get_group_url, normalize_lesson_day, normalize_week_lesson_days
from config import token, proxy

user_urls = {}
bot = Bot(token=token, proxy=proxy)
dp = Dispatcher(bot)


@dp.message_handler(CommandStart())
async def handle_start_help(message: Message):
    if user_urls.get(message.chat.id):
        user_urls.pop(message.chat.id)
    await message.answer('Привет. Напиши номер своей группы:', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['admin'])
async def admin(message: Message):
    if message.chat.id == 489951151:
        await message.answer(str(user_urls))


@dp.message_handler(content_types=['text'])
async def get_group_num(message: Message):
    if '-' in message.text and not user_urls.get(message.chat.id):
        text = f'Отлично, сейчас найдем твою группу <b>{message.text}</b>'
        found_group = await message.answer(text, parse_mode='HTML')
        user_urls[message.chat.id] = get_group_url(message.text.upper())
        if not user_urls[message.chat.id]:
            await message.answer(f'К сожалению твой номер группы не найден <b>{message.text}</b>', parse_mode='HTML')
            await found_group.delete()
            return
        keyboard_markup = ReplyKeyboardMarkup(row_width=2)
        buttons_text = ("Сегодня", "Завтра", 'Текущая неделя', 'Следующая неделя', 'Текущая неделя +2')
        keyboard_markup.add(*(KeyboardButton(text) for text in buttons_text))
        await found_group.delete()
        await message.reply(f'Отлично. Запроси расписание', reply_markup=keyboard_markup)

    elif message.text.title() == 'Сегодня' and user_urls.get(message.chat.id):
        await message.answer(normalize_lesson_day(user_urls.get(message.chat.id), message.text),
                             parse_mode=ParseMode.MARKDOWN)

    elif message.text.title() == 'Завтра' and user_urls.get(message.chat.id):
        date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        url_parts = f"{user_urls.get(message.chat.id).replace('/schedule', '/day?')}date={date}/"
        await message.answer(normalize_lesson_day(url_parts, message.text), parse_mode=ParseMode.MARKDOWN)

    elif message.text == 'Текущая неделя' and user_urls.get(message.chat.id):
        await message.answer(normalize_week_lesson_days(user_urls.get(message.chat.id), 0, message.text),
                             parse_mode=ParseMode.MARKDOWN)

    elif message.text == 'Следующая неделя' and user_urls.get(message.chat.id):
        await message.answer(normalize_week_lesson_days(user_urls.get(message.chat.id), 1, message.text),
                             parse_mode=ParseMode.MARKDOWN)

    elif message.text == 'Текущая неделя +2' and user_urls.get(message.chat.id):
        await message.answer(normalize_week_lesson_days(user_urls.get(message.chat.id), 2, message.text),
                             parse_mode=ParseMode.MARKDOWN)

    else:
        await message.answer('Напиши номер своей группы')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

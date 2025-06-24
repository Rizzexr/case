import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils.markdown import bold, italic

# Замените на свой токен
API_TOKEN = '8100626715:AAGN0jkJjW4njdDJX0lnprH5SwCAx1dFMJs'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения каналов пользователей: {user_id: channel_id}
user_channels = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Добавь свой канал командой /add @channelname\n"
                       "После этого отправляй мне контент, и я опубликую его в твой канал!")

# Добавление канала
@dp.message_handler(commands=['add'])
async def add_channel(message: types.Message):
    if len(message.text.split()) != 2:
        await message.reply("Используй: /add @channelname")
        return
    
    channel = message.text.split()[1]
    if not channel.startswith('@'):
        await message.reply("Канал должен начинаться с @")
        return
    
    user_channels[message.from_user.id] = channel
    await message.reply(f"Канал {channel} добавлен! Теперь отправляй мне контент для публикации.")

# Удаление канала
@dp.message_handler(commands=['remove'])
async def remove_channel(message: types.Message):
    if message.from_user.id in user_channels:
        del user_channels[message.from_user.id]
        await message.reply("Канал удален из списка!")
    else:
        await message.reply("У тебя нет добавленных каналов.")

# Обработка контента
@dp.message_handler(content_types=['text', 'photo', 'video', 'document'])
async def handle_content(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, есть ли у пользователя канал
    if user_id not in user_channels:
        await message.reply("Сначала добавь свой канал командой /add @channelname")
        return
    
    channel = user_channels[user_id]
    
    try:
        if message.text:
            formatted_text = message.text
            if message.text.startswith('**'):
                formatted_text = bold(message.text[2:])
            elif message.text.startswith('*'):
                formatted_text = italic(message.text[1:])
            await bot.send_message(channel, formatted_text, parse_mode=ParseMode.MARKDOWN)

        elif message.photo:
            caption = message.caption or ""
            if caption.startswith('**'):
                caption = bold(caption[2:])
            await bot.send_photo(channel, message.photo[-1].file_id, caption=caption, parse_mode=ParseMode.MARKDOWN)

        elif message.video:
            caption = message.caption or ""
            await bot.send_video(channel, message.video.file_id, caption=caption)

        elif message.document:
            caption = message.caption or ""
            await bot.send_document(channel, message.document.file_id, caption=caption)

        await message.reply(f"Опубликовано в {channel}!")

    except Exception as e:
        await message.reply(f"Ошибка при публикации в {channel}: {str(e)}\n"
                           "Убедись, что я добавлен в канал как администратор!")

# Запуск бота
async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
import os
from pathlib import Path
import glob
from aiogram import Bot, Dispatcher, executor, types
import shutil
from secrets import TOKEN
from converter import convert_to_pdf, convert_to_jpg


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(types.KeyboardButton('Старт'))


@dp.message_handler(content_types=['document', 'photo', 'text'])
async def handle_docs_photo(message):
    chat_id = message.chat.id
    from_user = 'from_users/' + str(chat_id) + '/'
    for_user = 'for_users/' + str(chat_id) + '/'
    if not os.path.exists(from_user):
        os.mkdir(from_user)

    if not os.path.exists(for_user):
        os.mkdir(for_user)

    try:

        if message.text == 'Старт' or message.text == '/start':
            await bot.send_message(chat_id, 'Привет, прикрепи фото или пдф документ как файл',
                                   reply_markup=start_keyboard)
        file_id = message.document.file_id
        print(file_id)
        file = await bot.get_file(file_id)
        print(file.file_path)
        if file.file_size <= 6291456:

            downloaded_file = await bot.download_file(file.file_path, from_user + message.document.file_name)
            await bot.send_message(chat_id, 'Файл успешно загружен', reply_markup=start_keyboard)
            downloaded_file.close()

            suffix = Path(from_user + message.document.file_name).suffix

            if suffix.lower() == '.jpg' or suffix == '.png' or suffix == '.jpeg':
                print('converting...')
                convert_to_pdf(from_user + message.document.file_name, for_user)

                for file in glob.glob(for_user + '*'):
                    with open(file, 'rb') as doc:
                        await message.reply_document(doc)

            elif suffix == '.pdf':
                print('converting...')
                convert_to_jpg(from_user + message.document.file_name, for_user)

                for file in glob.glob(for_user + '*'):
                    with open(file, 'rb') as doc:
                        await message.reply_document(doc)

            else:
                await bot.send_message(chat_id, 'Неверный формат файла')
        else:
            await bot.send_message(chat_id, 'Файл слишком большой, максимальный размер файла = 6MB')
            print('Файл слишком большой, максимальный размер файла = 6MB')

    except Exception as e:
        print(e)
    finally:
        shutil.rmtree(from_user)
        shutil.rmtree(for_user)


if __name__ == '__main__':
    executor.start_polling(dp)

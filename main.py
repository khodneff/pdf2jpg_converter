import os
from pathlib import Path
import glob
import img2pdf
from aiogram import Bot, Dispatcher, executor, types
from pdf2image import convert_from_path
import shutil

TOKEN = '5456172152:AAG2-z_6E9FzYjCe7atzoX-m1eqQ77fAK5k'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(types.KeyboardButton('Старт'))


def convert_to_jpg(path: str, user_dir: str):
    images = convert_from_path(path)

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(user_dir + 'page' + str(i) + '.jpg', 'JPEG')


def convert_to_pdf(path_to_file: str, user_dir: str):
    with open(user_dir + os.path.splitext(os.path.basename(path_to_file))[0] + '.pdf', 'wb') as f:
        f.write(img2pdf.convert(path_to_file))
        f.close()


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
                # convert_to_pdf('files/' + message.document.file_name)
                for file in glob.glob(for_user + '*'):
                    doc = open(file, 'rb')
                    await message.reply_document(doc)
                    doc.close()

            elif suffix == '.pdf':
                print('converting...')
                convert_to_jpg(from_user + message.document.file_name, for_user)
                for file in glob.glob(for_user + '*'):
                    doc = open(file, 'rb')
                    await message.reply_document(doc)
                    doc.close()

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

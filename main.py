import os
from pathlib import Path
import glob
import img2pdf
from aiogram import Bot, Dispatcher, executor, types
from pdf2image import convert_from_path


TOKEN = '5456172152:AAG2-z_6E9FzYjCe7atzoX-m1eqQ77fAK5k'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(types.KeyboardButton('Старт'))


def convert_to_jpg(path: str):
    images = convert_from_path(path, poppler_path=r'app\poppler-22.04.0\Library\bin')

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save('tmp/page' + str(i) + '.jpg', 'JPEG')

    for file in glob.glob('files/*'):
        os.remove(file)


def convert_to_pdf(path_to_file: str):

    with open('tmp/' + os.path.splitext(os.path.basename(path_to_file))[0] + '.pdf', 'wb') as f:
        f.write(img2pdf.convert(path_to_file))
        f.close()

    for file in glob.glob('files/*'):
        os.remove(file)


@dp.message_handler(content_types=['document', 'photo', 'text'])
async def handle_docs_photo(message):
    chat_id = message.chat.id
    try:

        if message.text == 'Старт' or message.text == '/start':
            await bot.send_message(chat_id, 'Привет, прикрепи фото или пдф документ как файл',
                                   reply_markup=start_keyboard)
        file_id = message.document.file_id
        print(file_id)
        file = await bot.get_file(file_id)
        print(file.file_path)
        downloaded_file = await bot.download_file(file.file_path, 'files/' + message.document.file_name)
        await bot.send_message(chat_id, 'Файл успешно загружен', reply_markup=start_keyboard)
        downloaded_file.close()

        suffix = Path(r'files/' + message.document.file_name).suffix

        if suffix.lower() == '.jpg' or suffix == '.png' or suffix == '.jpeg':
            print('converting...')
            convert_to_pdf('files/' + message.document.file_name)
            # convert_to_pdf('files/' + message.document.file_name)
            for file in glob.glob('tmp/*'):
                doc = open(file, 'rb')
                await message.reply_document(doc)
                doc.close()

            for file in glob.glob('tmp/*'):
                os.remove(file)

        elif suffix == '.pdf':
            print('converting...')
            convert_to_jpg('files/' + message.document.file_name)
            for file in glob.glob('tmp/*'):
                doc = open(file, 'rb')
                await message.reply_document(doc)
                doc.close()

            for file in glob.glob('tmp/*'):
                os.remove(file)
        else:
            await bot.send_message(chat_id, 'Неверный формат файла')
            for file in glob.glob('files/*'):
                os.remove(file)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    executor.start_polling(dp)

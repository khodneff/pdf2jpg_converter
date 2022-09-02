import img2pdf
import os
from pdf2image import convert_from_path


def convert_to_jpg(path: str, user_dir: str):
    images = convert_from_path(path)

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(user_dir + 'page' + str(i) + '.jpg', 'JPEG')


def convert_to_pdf(path_to_file: str, user_dir: str):
    with open(user_dir + os.path.splitext(os.path.basename(path_to_file))[0] + '.pdf', 'wb') as f:
        f.write(img2pdf.convert(path_to_file))
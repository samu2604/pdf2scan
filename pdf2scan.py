import os
from PIL import Image
from PIL import ImageFilter
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
import io
import random

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import tempfile

def add_image_as_page(image_stream, pdf_writer):
    # Save the BytesIO stream to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image_file:
        temp_image_file.write(image_stream.getvalue())
        temp_image_file_path = temp_image_file.name

    # Create a new PDF with reportlab using the temporary image file
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter
    c.drawImage(temp_image_file_path, 0, 0, width, height)
    c.save()

    # Move the packet's position to the start
    packet.seek(0)
    new_pdf = PdfReader(packet)
    page = new_pdf.pages[0]
    pdf_writer.add_page(page)

    # Cleanup: remove the temporary file
    os.remove(temp_image_file_path)

def blur_pdf(input_file, output_file, black_and_white=False):
    # Convert PDF pages to images
    images = convert_from_path(input_file)
    # Create a new PDF writer
    pdf_writer = PdfWriter()

    # Loop through each page
    for img in images:
        # Rotate the image by a small random angle
        angle = random.uniform(-0.2, 0.02)  # Rotate between -0.5 and 0.5 degrees
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True)

        # Convert to black and white if the option is set
        if black_and_white:
            img = img.convert('L')

        # Convert some pixels to black
        img = img.point(lambda p: p * 0.9)

        # Blur the image
        img = img.filter(ImageFilter.GaussianBlur(radius=0.8))  # Apply a less intense blur

        # Convert the blurred image back to a PDF page
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, 'JPEG')
        img_byte_arr.seek(0)

        # Add the blurred page to the new PDF
        add_image_as_page(img_byte_arr, pdf_writer)

    # Save the new PDF
    with open(output_file, 'wb') as file:
        pdf_writer.write(file)

# %%
# provide input and output file paths through command line arguments
import argparse
parser = argparse.ArgumentParser(description='Convert a PDF to a scanned-like PDF')
parser.add_argument('--input_file', help='The input PDF file')
parser.add_argument('--output_file', help='The output PDF file')
parser.add_argument('--black_and_white', action='store_true', help='Convert the PDF to black and white')
args = parser.parse_args()


# Blur the PDF in black and white
blur_pdf(args.input_file, args.output_file, black_and_white=args.black_and_white)


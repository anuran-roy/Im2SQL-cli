#!/usr/bin/env python
# coding: utf-8

# Import required packages
import cv2
import pytesseract
import numpy as np


def recognize(img_path, tesseract_path):  # Taken from GFG

    # Mention the installed location of Tesseract-OCR in your system
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Read image from which text needs to be extracted
    img = cv2.imread(img_path)

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

    # Finding contours
    contours, hierarchy = cv2.findContours(
        dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # Creating a copy of image
    im2 = img.copy()

    # A text file is created and flushed
    #     file = open(output_path, "w+")
    #     file.write("")
    #     file.close()

    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Drawing a rectangle on copied image
        # rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Cropping the text block for giving input to OCR
        cropped = im2[y : y + h, x : x + w]

        # Open the file in append mode
        #         file = open(output_path, "a")

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped)

        # Appending the text into file
    #         file.write(text)
    #         file.write("\n")

    # Close the file
    #         file.close

    return text


text = recognize("tests/tesseract/input/employee.png", "/usr/bin/tesseract")

# print(text.strip().replace("|", ", ").replace("[", ", "))


def typecast(text, decimals=1):
    if text.isnumeric():
        try:
            if decimals == 0:
                return int(text)
            else:
                return np.round(float(text), decimals)
        finally:
            pass
    elif text.lower() == "null":
        return text
    else:
        return f"'{text}'"


tx2 = str(text.strip().replace("|", "; ").replace("[", "; "))

lines = [[typecast(j.strip(" "), 0) for j in i.split(";")] for i in tx2.split("\n")]

# for i in lines:
#     print(i, end=",\n")


class TableNameException(Exception):
    def __init__(self):
        self.msg = """\nYour table name isn't in one word.
                    Consider using underscores (_) instead of spaces
                    and hyphens(-)\n
                    """
        super().__init__(self.msg)


table_name = input("Enter table name:")

if len(table_name.strip().split(" ")) != 1 or table_name == "":
    raise TableNameException

commands = list()
for i in lines:
    cmd = f"INSERT INTO {table_name} VALUES("
    for j in range(len(i)):
        cmd += f"{i[j]}"
        if j < len(i) - 1:
            cmd += ", "
    cmd += ");"
    commands.append(cmd)
    # print(cmd)

for i in commands:
    print(i)

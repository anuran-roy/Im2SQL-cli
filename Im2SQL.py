#!/usr/bin/env python
# coding: utf-8

# Import required packages
import cv2
import pytesseract
import numpy as np
from typing import Any, List, Tuple, Dict
import sys


class TableNameException(Exception):
    def __init__(self):
        self.msg = """\nYour table name isn't in one word.
                    Consider using underscores (_) instead of spaces
                    and hyphens(-)\n
                    """
        super().__init__(self.msg)


def recognize(img_path: str, tesseract_path: str) -> str:  # Taken from GFG

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
        cropped = im2[y:(y + h), x:(x + w)]

        # Open the file in append mode
        #         file = open(output_path, "a")

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(im2)  # cropped)

        # Appending the text into file
    #         file.write(text)
    #         file.write("\n")

    # Close the file
    #         file.close

    return text


def tokenize(text: str) -> List:
    tx2: str = str(text.strip().replace("|", "; ").replace("[", "; "))
    lines: List = [
        [
            typecast(j.strip(" "), 0) for j in i.split(";") if typecast(j.strip(" "), 0) != "''"
        ] for i in tx2.split("\n")
    ]

    return lines


def typecast(text: str, decimals: int = 1) -> Any:
    try:
        if decimals == 0:
            return int(text)
        else:
            return np.round(float(text), decimals)
    except Exception:
        if text.lower() == "null":
            return text
        else:
            return f"'{text}'"


# for i in lines:
#     print(i, end=",\n")


def to_insertion(table_name: str, lines: List) -> List:
    print("\nConverting to INSERT commands...\n")
    commands: List = list()

    # print("\nTo parse:\n")
    # for i in lines:
    #     print(i)
    print("\n\n")
    for i in lines:
        cmd: str = f"INSERT INTO {table_name} VALUES("
        if i != []:
            for j in range(len(i)):
                cmd += f"{i[j]}"
                if j < len(i) - 1:
                    cmd += ", "
            cmd += ");"
            commands.append(cmd)

    return commands


def typeEnforce(cmd: List) -> List:
    # checks: List = list()
    cmd2: List = list(cmd)
    # correct_col_len = list()

    print("\nChecking row contents...\n")
    for i in range(len(cmd2) - 1):
        if len(cmd2[i]) != len(cmd2[i + 1]):
            # checks.append(f" -> Entry {i+1} is different in length compared to entry {i+2}")
            print(
                f" -> Entry {i+1} (Length: {len(cmd2[i])}) is different in length compared to entry {i+2} (Length: {len(cmd2[i+1])})"
            )
        # else:
        #     correct_col_len.append(cmd2[i])

    lengths: List = [len(x) for x in cmd]
    unique_lengths: List = list(set(lengths))
    frequencies: Dict = dict()

    for i in unique_lengths:
        frequencies[i] = 0

    for i in lengths:
        frequencies[i] += 1

    most_common_column_no: Tuple = (sorted(list(frequencies.items()),
                                    key=lambda x: x[0]))[-1]
    print("Number of entries:", len(cmd))
    print("Most common number of columns: ", most_common_column_no[0])

    correct_length_columns: List = [
        (cmd[i], i + 1)
        for i in range(len(cmd))
        if len(cmd[i]) == most_common_column_no[0]
    ]

    # if len(checks) >= 1:
    #     return checks

    # for i in checks:
    #     print(i)

    # print(f"Columns with {most_common_column_no[0]} columns:\n")
    # for i in correct_length_columns:
    #     print(i[0])

    print("\nType checking column contents...\n")

    for i in range(len(correct_length_columns) - 1):
        for j in range(most_common_column_no[0]):
            if type(correct_length_columns[i][0][j]) == \
               type(correct_length_columns[i + 1][0][j]):
                print(f" -> Column {j+1} in entry", end=" ")
                print(f"{correct_length_columns[i][1]} is different", end=" ")
                print(
                    f"type compared to that in entry {correct_length_columns[i+1][1]}"
                )
                # checks.append(f" -> Column {j+1} in entry {correct_length_columns[i][1]} is different type compared to that in entry {correct_length_columns[i+1][1]}")
                # return False

    # return checks


def write(table_name: str, lines: List, path: str) -> None:
    try:
        f = open(path, "w")

        for i in lines:
            f.write(i)
            f.write("\n")

        f.close()
    except Exception as e:
        print(f"Error occured while writing to file. Details: {e}")


def driver(image_path: str, tesseract_path: str) -> None:
    text: str = recognize(image_path, tesseract_path)

    lines: List = tokenize(text)
    # print("\nIdentified Text:\n")
    # print(text.strip().replace("|", ", ").replace("[", ", "))

    table_name: str = input("Enter table name:")

    if len(table_name.strip().split(" ")) != 1 or table_name == "":
        raise TableNameException
    
    commands: List = to_insertion(table_name, lines[1:])

    for i in commands:
        print(i)

    # chk: List = typeEnforce(lines[1:])

    # for i in chk:
    #     print(i)
    if "--typecheck" in sys.argv:
        print("\nChecks:\n")
        typeEnforce(lines[1:])

    if "-o" in sys.argv and "-o" != sys.argv[-1]:
        index: int = sys.argv.index("-o")

        path: str = sys.argv[index + 1]

        write(table_name, commands, path)


def test():
    # pass
    if "--test" in sys.argv:
        pass
    
    INPUT_DIR: List = list(os.walk("tests/tesseract/input"))[0][-1]

    # for i in

if __name__ == "__main__":
    INPUT_PATH: str = "/home/anuran/Desktop/sample sql table 8.png"  # "tests/tesseract/input/works on.png"
    TESSERACT_PATH: str = "/usr/bin/tesseract"

    driver(INPUT_PATH, TESSERACT_PATH)

# Import libraries
import fitz
import re
from pathlib import Path
import pandas as pd
import sys
import os

# set directory path
# dir_path = Path('/Users/Dan/Downloads/') #stored pdf input folder location

# Directory path  for manual input
RedDir = input("\nEnter a directory of PDF files to redact: ")  # manually entered pdf input folder location
dir_path = Path(RedDir)

# list of pdfs in dir
pdf_files = list(dir_path.glob('*.pdf'))  # convert result to a list

# check directory exists
if not os.path.isdir(RedDir):
    sys.exit("\nNo such file or directory")

# if no files found exit
if len(pdf_files) == 0:
    sys.exit("\nNo Files Found")

# output messages of files found
print("\n" + str(len(pdf_files)) + " files found\n\nFile list:\n")
for i in pdf_files:
    print(i)

# Output directory for manual input
OutDir = input("\nEnter an output directory for redacted files: ")  # manually entered output folder location

# check directory exists
if not os.path.isdir(OutDir):
    sys.exit("\nNo such file or directory")

# Search Lists
Pre_determined_words = []
regex_list = []
Manual_words = []
regex_words = []

# Check if users wants to manually import a word/regex file with lists
manual_input_file = input("\nDo you want to import a file of regex and words to exclude (excel only)?(y/n): ")
while manual_input_file != 'y' and manual_input_file != 'n':
    print("Error, input is not valid. Please y or n \n")
    manual_input_file = input("\nDo you want to import a file of regex and words to exclude (excel only)?(y/n): ")

# Manual input for file to redact question
if manual_input_file == 'y':
    # set word list file import
    # word_list = '/Users/Dan/Downloads/Words.xlsx' #stored word/regex file location
    word_list = input(
        "\nEnter Excel file location for words & regex to redact: ")  # manually entered word/regex file location

    # check file exists
    if not os.path.isfile(word_list):
        sys.exit("\nNo such file or directory")

    # check file type is correct
    if ".xlsx" not in word_list:
        sys.exit("\nThis is not an .xlsx file")

    # add file to Pre_determined_words list (column 1: Words)
    df = pd.read_excel(word_list)
    if 'Words' in df.columns:
        word_list = df['Words'].tolist()
        Pre_determined_words = Pre_determined_words + word_list
        # remove null values in list
        Pre_determined_words = [x for x in Pre_determined_words if str(x) != 'nan']
    else:
        sys.exit("\nThe column 'Words' is needed in input sheet 1, please check and retry")

    # add file to Pre_determined_words list (column 2: Regex)
    if 'Regex' in df.columns:
        regex_import_list = df['Regex'].tolist()
        regex_list = regex_list + regex_import_list
        # remove null values in list
        regex_list = [x for x in regex_list if str(x) != 'nan']
    else:
        sys.exit("\nThe column 'Regex' is needed in input sheet 1, please check and retry")

# Check if users wants to manually input a regex
manual_input_regex = input("\nDo you need to manually enter regex to redact?(y/n): ")
while manual_input_regex != 'y' and manual_input_regex != 'n':
    print("Error, input is not valid. Please y or n \n")
    manual_input_regex = input("\nDo you need to manually enter regex to redact?(y/n): ")

# Manual input for regex  to redact
if manual_input_regex == 'y':

    another_regex = 'y'
    while another_regex == 'y':
        manual_regex = input("\nEnter a regex to redact (within brackets):")
        regex_list.append(manual_regex)
        another_regex = input("\nEnter another regex?(y/n): ")
        while another_regex != 'y' and another_regex != 'n':
            print("Error, input is not valid. Please y or n \n")
            another_regex = input("\nEnter another word?(y/n): ")

# Check if users wants to manually input a word
manual_input_word = input("\nDo you need to manually enter words to redact?(y/n): ")
while manual_input_word != 'y' and manual_input_word != 'n':
    print("Error, input is not valid. Please y or n \n")
    manual_input_word = input("\nDo you need to manually enter words to redact?(y/n): ")

# Manual input for words to redact
if manual_input_word == 'y':

    another_word = 'y'
    while another_word == 'y':
        my_word = input("\nEnter a word to redact:")
        Manual_words.append(my_word)
        another_word = input("\nEnter another word?(y/n): ")
        while another_word != 'y' and another_word != 'n':
            print("Error, input is not valid. Please y or n \n")
            another_word = input("\nEnter another word?(y/n): ")

# loop for individual files in dir path

for file in pdf_files:
    # Open current document
    doc = fitz.Document(file)
    # Loop for regex
    for item in regex_list:

        # loop for pages in current document
        for page in doc:
            # Get text from page separated by new line
            redact_data = page.get_text("text").split('\n')

            # loop for searching regex within each line and adding word to a list
            for line in redact_data:
                if re.search(item, line, re.IGNORECASE):
                    reg_search = str(re.search(item, line, re.IGNORECASE))
                    reg_str_individual = re.findall(r"'(.*?)'", reg_search)[0]
                    regex_words.append(reg_str_individual)
        #print(redact_data) - look at if it's not stored as text how can it read text in images.
    # combine added words, added regex to pre-determined lists
    words = Pre_determined_words + Manual_words + regex_words

    # redaction method - search for each word within each page by document
    for page in doc:
        for word in words:
            for instance in page.search_for(word, quads=True):
                areas = page.search_for(word)

                # fill area around the word and colour
                [page.add_redact_annot(area, fill=(0, 0, 0)) for area in areas]
                page.apply_redactions()

    # print file names
    print("\nRedacted: " + str(file))

    # extract incoming file names and save current document as its original name in selected directory
    incoming_file = str(dir_path)
    filename = str(file).replace(incoming_file, "")

    # doc.save("/Users/Dan/Downloads/Python Output"+filename, True) # stored output location
    doc.save(str(OutDir) + filename, True)  # manually entered output location

print("\nSuccessfully redacted " + str(len(pdf_files)) + " files")

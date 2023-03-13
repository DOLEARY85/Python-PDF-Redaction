# Bulk PDF Redaction Python

Looking for an adaptable way to bulk redact PDF’s in Python?

This technical guide should provide basics to get you started.

# Importing the PDF’s
The first step to import the PDF directory:
from pathlib import Path

    RedDir = input("\nEnter a directory of PDF files to redact: ")  # manually entered pdf input folder location
    dir_path = Path(RedDir)

The pathlib library is used to reference the file path. I’ve opted for a manual input to allow the user to enter the directory where the PDF files are located, but it could be adapted to a static location. The manual input is currently a string so I’ve used ‘Path’ to change the input directory to something useable. Having a manual input can lead to various types of user error but I’ll come back to error handling a bit later.
Now you have your directory, you’ll need to search it and produce a list of PDF files contained within it:

    # list of pdfs in dir
    pdf_files = list(dir_path.glob('*.pdf'))  # convert result to a list

The glob function will retrieve files matching a specific pattern, in this case pdf files. 
Next it is a good idea to create an output directory where you will save a copy of the redacted PDF’s, I’ve used the same manual input as with the PDF input directory:

    # Output directory for manual input
    OutDir = input("\nEnter an output directory for redacted files: ")  

Now we should have our list of files, next we need to have a list of what we want to redact. This can be done in a number of ways: you can add them to the script, have users input them directly or bring them in from an input file. In this script we’ll cover all of these options for both words and Regular Expressions. First thing to do is set up your lists, I’ve separated them out for potential future reporting purposes.

# Lists to Redact

    # Search Lists
    Pre_determined_words = []
    regex_list = []
    Manual_words = []
    regex_words = []

    words = Pre_determined_words + Manual_words + regex_words

I have created 5 lists:
•	Pre_determined_words – this will be anything you want to have pre-input into the script
•	regex list – this will contain a list of expressions – either manually entered or from a file
•	Manual_words – this will be a manual input from the user running the script
•	regex_words – this will be a list of the words found using the expressions entered.  
•	Words – this will be a combined list to run through and redact. (this is just for demonstration purposes as we will need to move this later as once we move to looking at Regular Expressions.)

# Applying the Redaction

Starting with just the Pre_determined_words, this requires no additional processing so we will move straight to the redaction section. This is going to run through each word in the list for each document and add a redaction to the open version of the file.
for file in pdf_files:

    # Open current document
    doc = fitz.Document(file)
    for page in doc:
        for word in words:
            for instance in page.search_for(word, quads=True):
                areas = page.search_for(word)

                # fill area around the word and colour
                [page.add_redact_annot(area, fill=(0, 0, 0)) for area in areas]
                page.apply_redactions()

This is done by using fitz from the PyMuPDF library to open the PDF files, (You’ll need to import this library), the for loops will run every word declared in combined list words, then through each page of every file previously declared in the pdf_files list. 
The redaction routine then searches word by word and creates an area around the word then applies the redaction to completely black out the area.

# Saving the File

After this each file will need to be saved:

    incoming_file = str(dir_path)
    filename = str(file).replace(incoming_file, "")

    doc.save(str(OutDir) + filename, True)  # manually entered output location

I’ve chosen to use the same file name from the original file. For this I’ve converted the input file path to a string and removed that part from the full filename used to open each PDF(leaving only the file name). This is then saved into the output directory previously declared.

# Adding Regular Expressions 

Next we’ll look at Regular Expressions. For this we’ll need to add the expressions to the list ‘regex_list’. You will need to open the PDF file and scan through with each expression, it’s best to place this just after opening the document but before looping through the redaction routine. (You’ll also need to import re for this.)

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

After the document is open we loop through each file page by page to get the text within it. Then it loops rough each Regular Expression in the list and runs through the text line by line to match the pattern of the expression to the text. Once the text has been found the word is added to the list regex_words.
After this section would be the best place to move your final list – words, this ensures each list is updated before the redaction routine runs.
words = Pre_determined_words + Manual_words + regex_words

Now you have a script that can bulk redact PDFs with pre-defined words and Regular Expressions. To make this more interactive we’ll add a user input next.

# Manual Interaction
Starting with a simple input we add the manually entered words to the manual_words list

    my_word = input("\nEnter a word to redact:")
    Manual_words.append(my_word)

We can then wrap this in a while loop to allow the user to select whether they want to enter another word after the first word. This also add some error handling to only allow the user to select ‘y’ or ‘n’.

    another_word = 'y'
    while another_word == 'y':
        my_word = input("\nEnter a word to redact:")
        Manual_words.append(my_word)
        another_word = input("\nEnter another word?(y/n): ")
        while another_word != 'y' and another_word != 'n':
            print("Error, input is not valid. Please y or n \n")
            another_word = input("\nEnter another word?(y/n): ")

This, however, forces the user to enter a word so we’ll add a question before it to select whether the user would like to enter any words manually. 

    manual_input_word = input("\nDo you need to manually enter words to redact?(y/n): ")
    while manual_input_word != 'y' and manual_input_word != 'n':
        print("Error, input is not valid. Please y or n \n")
        manual_input_word = input("\nDo you need to manually enter words to redact?(y/n): ")
    # Manual input for words to redact
    if manual_input_word == 'y':

We can then repeat this process for Regular Expressions:

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

Your redaction tool is now more interactive. This is good but the process could be slow having users potentially entering huge lists of information or mis-entering Regular Expressions. To take this a step further we’ll add functionality that will allow the user to import a spreadsheet with columns of Words or Regular Expressions.

# Importing Lists
To start we’ll use our previous examples to add in a question (complete with error handling) to ask the user whether they would like to import a file of words and Regular Expressions to exclude(for this example I’ve used one spreadsheet with 2 columns on the first sheet, one named ‘Words’ and one named ‘Regex’):

    # Check if users wants to manually import a word/regex file with lists
    manual_input_file = input("\nDo you want to import a file of regex and words to exclude (excel only)?(y/n): ")
    while manual_input_file != 'y' and manual_input_file != 'n':
        print("Error, input is not valid. Please y or n \n")
        manual_input_file = input("\nDo you want to import a file of regex and words to exclude (excel only)?(y/n): ")

Next if the user selects ‘y’ we ask for the user to input the file location.

    # Manual input for file to redact question
    if manual_input_file == 'y':
        # set word list file import
        # word_list = '/Users/Dan/Downloads/Words.xlsx' #stored word/regex file location
        word_list = input(
            "\nEnter Excel file location for words & regex to redact: ")  # manually entered word/regex file location

We then convert the word list to a data frame (remember to import pandas as pd) then convert the items from the Words column to  a list and append them to the Pre_determined_words. There’s also some error handling here to exclude and null values and to check the Words column exists. If the column does not exist, the script exits. (You’ll need to import sys)

    df = pd.read_excel(word_list)
    if 'Words' in df.columns:
        word_list = df['Words'].tolist()
        Pre_determined_words = Pre_determined_words + word_list
        # remove null values in list
        Pre_determined_words = [x for x in Pre_determined_words if str(x) != 'nan']
    else:
        sys.exit("\nThe column 'Words' is needed in input sheet 1, please check and retry")

You can then repeat this process for the Regex column.

    if 'Regex' in df.columns:
        regex_import_list = df['Regex'].tolist()
        regex_list = regex_list + regex_import_list
        # remove null values in list
        regex_list = [x for x in regex_list if str(x) != 'nan']
    else:
        sys.exit("\nThe column 'Regex' is needed in input sheet 1, please check and retry")

The process of redaction is now is now interactive and user friendly. There are still cases where the user could cause an error, for example not selecting an existing directory or file.

# Error Handling
For directories I used the os.path.isdir below, this requires you to import os.

    if not os.path.isdir(RedDir):
        sys.exit("\nNo such file or directory")

For the excel file I very similarly used os.path.isfile and added a check to make sure the file was .xlsx. 

    # check file exists
    if not os.path.isfile(word_list):
        sys.exit("\nNo such file or directory")

    # check file type is correct
    
    if ".xlsx" not in word_list:
        sys.exit("\nThis is not an .xlsx file")

Additionally I added an exit on the input directory if no PDF files were found.

    # if no files found exit
    if len(pdf_files) == 0:
        sys.exit("\nNo Files Found")


# User Messaging
Finally, I added a few messages to update the user on the process:
Printing the files found in the PDF input directory:

    # output messages of files found
    print("\n" + str(len(pdf_files)) + " files found\n\nFile list:\n")
    for i in pdf_files:
        print(i)

Printing each file name as it’s redacted:
    # print file names
    print("\nRedacted: " + str(file))

    Printing a successfully completed message at the end of the script:
    print("\nSuccessfully redacted " + str(len(pdf_files)) + " files")

The full file is available here:

## [Python Bulk PDF Redaction]( https://github.com/DOLEARY85/Python-PDF-Redaction/blob/main/Redaction.py)
+ Authors: [Daniel O’Leary]( https://github.com/DOLEARY85)
+ Created: 10.03.2023


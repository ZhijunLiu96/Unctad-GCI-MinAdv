import glob
import os
import textract
import PyPDF2
import re
import pandas as pd


def clean_text(text):
    text = re.sub("b'", ' ', text)
    text = re.sub(r"\\n|\\\w+\d+|\\\w+", ' ', text)
    # text = re.sub("\W+", ' ', text)
    text = re.sub("^\s|\s$", '', text)
    text = re.sub("\s+", ' ', text)
    text = re.sub("\.+", '.', text)
    return text

def pdf2text_and_numpage(filename):
    pdfFileObj = open(filename,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    num_pages = pdfReader.numPages
    count = 0
    text = ""
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count += 1
        text += pageObj.extractText()

    # if text != "":
    #     if '\n\n\n\n\n\n\n\n\n\n' in text:
    #         return (str(textract.process(filename, method='tesseract')), num_pages, 'text-based-PDF')
    #     else:
    #         return (str(text), num_pages, 'text-based-PDF')
    # else:
    return (str(textract.process(filename, method='tesseract')), num_pages)


if __name__=="__main__":
    current = os.getcwd()
    os.chdir('pdf')
    filenames = [x for x in glob.glob('*')]

    data = pd.DataFrame(columns=['file name', 'page number', 'text'])

    for file in filenames:
        try:
            text, num = pdf2text_and_numpage(file)
            row = row = {"file name": file, "page number": num, "text": clean_text(text)}
        except:
            row = row = {"file name": file, "page number": None, "text": None}
        data = data.append(row, ignore_index=True)

    os.chdir(current)
    data.to_csv("ungc_result.csv")

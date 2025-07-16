import PyPDF2
import re
import pandas as pd

def read_pdf_pypdf2(filepath):
    text = ""
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

# Example usage:
pdf_content = read_pdf_pypdf2(r"C:\Users\thoma\OneDrive\Desktop\Wifi_Plans\B23 May .pdf")
pattern = r'\b6may\d{6}\b'
codes = re.findall(pattern, pdf_content)
lst = []
for code in codes:
    lst.append(code)

final = pd.DataFrame(lst, columns=['Code'])
print(final)
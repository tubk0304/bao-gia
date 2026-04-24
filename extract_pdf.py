import pypdf

file_path = 'e:/duong tan khoa/260409-LL-MEP-JAY HOME.pdf'
out_path = 'e:/duong tan khoa/pdf_extracted.txt'

try:
    reader = pypdf.PdfReader(file_path)
    text = ""
    for i, page in enumerate(reader.pages):
        text += f"--- PAGE {i+1} ---\n"
        text += page.extract_text() + "\n"
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Extraction successful.")
except Exception as e:
    print(f"Error: {e}")

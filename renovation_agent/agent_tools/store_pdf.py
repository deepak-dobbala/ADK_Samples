def store_pdf(pdf_path:str):
    with open(pdf_path,'w') as pdf_file:
        pdf_content = "This is a sample pdf content"
        pdf_file.write(pdf_content)
    
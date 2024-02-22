from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
import tkinter as tk
from tkinter import filedialog
import pdfplumber
import fitz
import pytesseract
from PIL import Image
from extra_functions import get_completion

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
        return text

    except Exception as e:
        return "Error reading the PDF: " + str(e)


def extract_text_from_scanned_pdf(pdf_file):
    # Open the PDF file using PyMuPDF (Fitz)
    pdf_document = fitz.open(pdf_file)

    # Initialize an empty string to store the extracted text
    extracted_text = ''

    # Iterate through each page of the PDF
    for page_number in range(pdf_document.page_count):
        # Get the current page
        page = pdf_document.load_page(page_number)

        # Convert the page to an image
        image = page.get_pixmap()
        image = Image.frombytes("RGB", [image.width, image.height], image.samples)

        # Use pytesseract to do OCR on the image
        page_text = pytesseract.image_to_string(image, lang='eng')

        # Append the extracted text from the page to the overall extracted text
        extracted_text += page_text

    # Close the PDF document
    pdf_document.close()

    return extracted_text

def get_lab_results():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

    if file_path:
        with pdfplumber.open(file_path) as pdf:
            if any(page.extract_text() for page in pdf.pages):
                text = extract_text_from_pdf(file_path)
                print("Text-based PDF. Extracted text:")
            else:
                text = extract_text_from_scanned_pdf(file_path)
                print("Scanned PDF. OCR may be needed.")
    extracted_text = text.encode('utf-8').decode('utf-8')

    schema = {
        "properties": {
            "patient_name": {"type": "string"},
            "Write the date on which the lab were conducted.": {"type": "string"},
            "HbA1c": {"type": "string"},
            "Albumin": {"type": "string"},
            "Creatinine": {"type": "string"},
            "GFR": {"type": "string"},
            "Lipid_Panel": {"type": "string"},
            "Urine_Drug_Screen": {"type": "string"},
            "Buprenorphine_and_UDS": {"type": "string"},
            "Buprenorphine_and_Metabolite": {"type": "string"},
            "Monitoring_Drug_Profile": {"type": "string"},
            "Vitamin_D": {"type": "string"},
            "PSA": {"type": "string"},
            "Occult_Blood_Fecal": {"type": "string"},
            "Tuberculosis_Test": {"type": "string"},
            "Hepatitis_Panel": {"type": "string"},
            "Thyroid_Panel": {"type": "string"},
            "STD_Panel": {"type": "string"},
            "Thyroxin_T3_and_T4": {"type": "string"},
            "Neisseria_Gonorrhoeae_NAA": {"type": "string"},
            "Chlamydia_Trachomatis_NAA": {"type": "string"},
            "HSV1_HSV2_IgG_M_w_Reflex": {"type": "string"},
            "HIV_1_0_2_Screen_w_WB1": {"type": "string"},
            "Hepatitis_A_B_and_C": {"type": "string"},
            "Iron": {"type": "string"},
            "TIBC": {"type": "string"},
            "Alkaline_Phosphatase": {"type": "string"},
            "AST_SGOT": {"type": "string"},
            "ALT_SGPT": {"type": "string"},
            "Rheumatoid_Arthritis_Qn_Fluid": {"type": "string"},
            "Pap_Smear": {"type": "string"},
            "Testosterone_Total": {"type": "string"}
        },
        "required": ["Write the date on which the lab were conducted."],
    }
    inp = str(extracted_text)
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    chain = create_extraction_chain(schema, llm)
    final_1 = chain.run(inp)
    print(final_1)
    delimiter = "####"
    messages_1 = [
        {
            "role": "system",
            "content": f"""Your job is to write a history of illness based on the extracted text that i will provide. Lets think step by step:
        First, you have to read the currant results with flags and than find the values that are not in the normal range or if the results are positive. The reference intervals are available in the text.
        At the end write these results in one line. The words should n't be exceed from 100 words.
        Don't write values that are not in reference interval or range.
        Don't write the patient details or additional data.
        Don't write the reference intervals in the output.
        Don't write the Indications.
        Don't suggest any potential issue based on findings.
        Make sure nothing is missed in the output """
        },
        {
            "role": "user",
            "content": "Your job is to write a history of illness based on the lab report.Don't add the results in \
                       the future outputs."

        },
        {
            "role": "assistant",
            "content": "The lab results indicate that the patient, Elizabeth Mitchell, has a few values that are outside the normal range. These include a low albumin level (3.7 g/dL)."
        },
        {
            "role": "user",
            "content": f"{delimiter}{text}{delimiter}"}]

    response_1 = get_completion(messages_1)
    print(response_1)

    prompt = f"""
        You are a medical assistant. Your job is to write the patient labs readings in the form of paragraph. You have to remove the duplicate reading.
        The abnormal readings are delimited by triple backticks. 
        '''{response_1}'''
        And the other readings are delimited by triple hashtags.
        ###{final_1}###

    """
    messages_2 = [
        {
            "role": "system",
            "content": f"""    
        You are a medical assistant. Your job is to rearrange the patient labs readings. You have to remove the duplicate reading.
        The output should be in the form of paragraph.

    """
        },
        {
            "role": "user",
            "content": "Remove the duplicates lab results. Firt write the abnormal readings and than write the other readings"

        },
        {
            "role": "assistant",
            "content": "The lab results indicate that the patient, Elizabeth Mitchell, has a few values that are \
            outside the normal range. These include a low albumin level (3.7 g/dL). Other normal readings are albumin \
            4.5 and GFR 69"
        },
        {
            "role": "user",
            "content": f"{delimiter}{prompt}{delimiter}"}]

    response_2 = get_completion(messages_2)
    print(response_2)

    return response_2



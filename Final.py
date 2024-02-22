from http.server import BaseHTTPRequestHandler, HTTPServer
import tkinter as tk
from tkinter import Checkbutton
import openai
from extra_functions import extract_text, get_completion,get_dictation
from hpi import get_templates
from labs_radiology import get_lab_results



class RequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')  # Allow POST and OPTIONS methods
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    def _send_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self._send_cors_headers()  # Send CORS headers
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()  # Send CORS headers for preflight request
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        print(f"Received text: {post_data}")

        response = ""
        if "Task 1:" in post_data:
            instance = histroy_of_illness(openai.api_key, post_data)
            response = instance.result
        elif "Task 2:" in post_data:
            instance = plan_of_care(post_data)
            response = instance.result
        elif "Task 3:" in post_data:
            instance = cpt_code(openai.api_key, post_data)
            response = instance.result
        elif "Task 4:" in post_data:
            instance = physical_exam(post_data)
            response = instance.result
        elif "Task 5:" in post_data:
            instance = review_of_system(post_data)
            response = instance.result
        else:
            response = "Task is not justified"

        self._send_response(response)
        print("Sent response:", response)

    def _send_response(self, response_text):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response_text.encode('utf-8'))


class cpt_code:
    def __init__(self, key, post_date, delimiter="####"):
        self.key = key
        self.post_data = post_date
        self.delimiter = delimiter
        result = self.final()  # Call the final() method and store the result
        self.result = result  # Store the result as an attribute

    def final(self):
        prompt = """You are a medical assistant. Your job is to make the python dictionary based on the text that I will provide.
         The sequence of the keys are if available:
         "Systolic:"
         "Diastolic:"
         "BMI:"
         If the mentioned keys are not available than return the key "nothing" with the value "nothing". 
        """
        user_1 = """You are a medical assistant. Your job is to make the python dictionary based on the text that I will provide.
         The sequence of the keys are if available:
         "Systolic:"
         "Diastolic:"
         "BMI:"
         If the mentioned keys are not available than return the key "nothing" with the value "nothing". 
         """
        result_1 = """
        {'Systolic':'120', 'Diastolic':'80', 'BMI':'36.5'}
        """
        result_2 = """
        {'nothing':'nothing'}
        """
        user_text = f"""
        You are a medical assistant. Your job is to make the python dictionary based on the text delimited by triple backticks.
             '''{self.post_data}'''
         The sequence of the keys are if available:
         "Systolic:"
         "Diastolic:"
         "BMI:"
         If the mentioned keys are not available than return the key "nothing" with the value "nothing". 
        """
        messages = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f"{self.delimiter}{user_1}{self.delimiter}"},
            {'role': 'assistant', 'content': f"{result_1}"},
            {'role': 'user', 'content': f"{self.delimiter}{user_1}{self.delimiter}"},
            {'role': 'assistant', 'content': f"{result_2}"},
            {'role': 'user', 'content': f"{self.delimiter}{user_text}"}
        ]
        result = get_completion(messages)

        return result
class histroy_of_illness:
    def __init__(self, key, post_date, delimiter="####"):
        self.key = key
        self.post_data = post_date
        self.delimiter = delimiter
        result = self.final()  # Call the final() method and store the result
        self.result = result  # Store the result as an attribute

    def get_basic_information(self):
        system_0 = """
        Remove all the disease or disorders mentioned from the text delimited by triple backticks and rearrange the remaining text.
        The headings should be:
        1) Patient demographics.
        2) Type of Visit.
        3) Medications.
        Note: Write only medication name and Sig in this heading. Don't write the Qty, Start Date:, Prescribe Date:  and End Date:
        4) Doctor Dictation.
        Note: Pick the doctor dictation that is after the "Doctor Dictation:" in the provided text.
            """
        prompt_0 = f"""
        Remove all the disease or disorders mentioned from the text delimited by triple backticks and rearrange the remaining text.
        ```{self.post_data}```
        """
        messages_0 = [
            {'role': 'system', 'content': system_0},
            {'role': 'user', 'content': f"{self.delimiter}{prompt_0}{self.delimiter}"}
        ]
        basic_info = get_completion(messages_0)
        return basic_info

    def get_histroy(self):

        system_1 = f"""
        As a medical assistant, your task is to check for the presence of a doctor's dictation section, typically located\
        after the heading "doctor dictation."

        If the "doctor dictation" and medications are available, focus on extracting diseases or disorders that are directly related \
        to "doctor dictation" and related to mentioned medications. In cases where the doctor's dictation is absent, rely solely \
        on mentioned medications. It is mandatory to write the reason of extraction.

        Don't extract the disease or disorder if no medication mentioned directly related to this disorder.

        If the "doctor dictation" and any medication is not mentioned in the provided text than extract only first five 
        disease or disorders. In this case the sentence should be start from "The previous history of the patient is "

        Don't add the BMI in the output.

        Write the short form of disease or disorders. Don't write the complete name.

        Don't extract the disease or disorder on the base of causes of medications.

        Don't add the word "unspecified" in the output

        Return "Noting" if no "doctor dictation" and medications are related to disease or disorder.

        At the end it is necessary to write the related disease or disorders in one line.

      """
        prompt_1 = f"""

        Based on the doctor's dictation and mentioned medications, Choose the diseases or disorders that are directly\
        related to the doctor's dictation and mentioned medications from the text 
        delimited by triple backticks.
        Don't add the BMI in the output.
        At the end it is necessary to write the related disease or disorders in one line.

        ```{self.post_data}```
    """

        few_shot_user_1 = """
        Based on the doctor's dictation and mentioned medications, Choose the diseases or disorders that are directly\
        related to the doctor's dictation and mentioned medications from the text 
        delimited by triple backticks.
        Don't add the BMI in the output.
        At the end it is necessary to write the related disease or disorders in one line.
            """

        few_shot_assistant_1 = """ 
        1) Sleep deprivation - related to the medication hydroxyzine HCl which is used for allergies and sleep.
        2) Insomnia - related to the medication hydroxyzine HCl which is used for sleep.
        3) Angina pectoris - related to the medication Klonopin which is used for anxiety and panic disorders.
        4) Chronic cough and Dysphonia - related to the medication Cepacol Sore Throat which is used for sore throat.

        The patient has a history of sleep deprivation, insomnia, angina pectoris, Anxiety, chronic cough and dysphonia.
         """
        few_shot_user_2 = """
        Based on the doctor's dictation and mentioned medications, Choose the diseases or disorders that are directly\
        related to the doctor's dictation and mentioned medications from the text 
        delimited by triple backticks.
        Don't add the BMI in the output.
        At the end it is necessary to write the related disease or disorders in one line.
            """

        few_shot_assistant_2 = """ 
        1) Anxiety disorder- related to the doctor's dictation which is mentioned in the text. 

        The patient disease or disorder is Anxiety.
         """

        messages_1 = [
            {'role': 'system', 'content': system_1},
            {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
            {'role': 'assistant', 'content': f"{few_shot_assistant_1}"},
            {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_2}{self.delimiter}"},
            {'role': 'assistant', 'content': f"{few_shot_assistant_2}"},
            {'role': 'user', 'content': f"{self.delimiter}{prompt_1}"}
        ]
        response = get_completion(messages_1)
        print(response)

        # Split the text into lines
        lines = response.split('\n')

        # Extract the last line
        history = lines[-1].strip()

        return history

    def combine_the_text(self, basic_data, history, template):

        system_2 = f"""
        You are a medical assistant and you job is to write a history of illness of the patient.
        The text contains the patient demographics, History of  disease or disorder, Medications and Doctor dictation.
        Please write a History of illness based on the text delimited by the triple backticks.lets think step by step.
        First line contains the patient demographics and provided 'history line'. Don't add the medications in this line.
        Second line contains the patient current complains with prescribe medication if available.
        Write the follow up information of disease or disorder in a line separately with only related medications.
        It is necessary to concluded with "**No other medical concerns in today's appointment**".
        Don't add the headings.
        Don't repeat the medical history.
        Utilize double asterisks for name, type of visit and medication.
        Make sure all the provided text is added in the output, 
        and nothing is missed in the output.
        
    """
        prompt_2 = f"""
                Please write a History of illness in based on the text delimited by the triple backticks,\
                ```{basic_data}```
                the the patient history is delimited by triple dashes,
                ---{history}---
                other text is delimited by triple brackets.
                {{{template}}}
                and concluded with "No other medical concerns in today's appointment".
                """
        few_shot_1 = """Write a history of illness of the patient based on the text that I will provide"""
        result_1 = """\
        Calvin Mcrae, a 71-year-old male, came in for a follow-up visit. He has a medical history of Hypertension (HTN), Hypothyroidism, and a history of cellulitis of the face.\n \

        Patient is following up on hypertension and hypothyroidism. He denies symptoms such as headaches, dizziness, diaphoresis, nausea/vomiting, fatigue, weakness, palpitations, leg cramps, peripheral edema, vision changes, chest pain, and shortness of breath. Mr. Mcrae is compliant with his medications which include Vitamin D2 1,250 mcg (50,000 unit) capsule, amlodipine 5 mg tablet, levothyroxine 50 mcg tablet, and cefadroxil 500 mg capsule. He denies any untoward side effects from these medications. He requested a medication refill during this visit.\n \
        
        He is following up on diabetes. She denies experiencing symptoms such as polydipsia, polyphagia, and polyuria. There are also no reports of peripheral edema, vision changes, diaphoresis, tingling or numbness of the limbs, lesions on the feet, palpitations, chest pain, and shortness of breath. She is compliant with her medications which include OneTouch Ultra Test strips, OneTouch UltraSoft Lancets, metformin 500 mg tablet.\n \

        He reported that he had a sexual encounter and his wife developed a yeast infection, which caused him concern. He is an occasional smoker. He also reported having a pimple or infected cyst, which may have developed after a sexual encounter. An EKG was performed and the records were noted.\n \

        He had an infection of the upper lip and experienced irregular heartbeats. His conditions of importance include hypertension and hypothyroidism.\n \

        **No other medical concerns in today's appointment**.\n \
        """

        messages_2 = [{'role': 'system', 'content': system_2},
                      {'role': 'user', 'content': f"{self.delimiter}{few_shot_1}{self.delimiter}"},
                      {'role': 'assistant', 'content': result_1},
                      {'role': 'user', 'content': f"{self.delimiter}{prompt_2}{self.delimiter}"}]

        response = get_completion(messages_2)
        return response

    def final(self):
        providers_1 = [
            "provider_ka_name: Ahmad, S. Syed, MD",
            "provider_ka_name: Castillo, Kendie, NP",
            "provider_ka_name: Chavez, Hazel, NP",
            "provider_ka_name: Diaz, Johannelda, NP",
            "provider_ka_name: Serzanin, M. Coleen, RN, MSN, Pmhnp-bc",
            "provider_ka_name: Oluwagbamila, Geralda, NP"
        ]
        providers_2 = [
            "provider_ka_name: Brown, Harold, MD",
            "provider_ka_name: Chowdhury, Bhanwarlal, M.D.",
            "provider_ka_name: Dipietropolo, Lisa, PMHNP-BC",
            "provider_ka_name: Viaje, Mabrigida, NP",
            "provider_ka_name: Gupta, Rajendra, MD",
            "provider_ka_name: Huynh-nguyen, P. Anh, NP"
        ]
        providers_3 = [
            "provider_ka_name: Albana, S. Fouad, MD",
            "provider_ka_name: Asiamah-asare, Vida-lynn, NP",
            "provider_ka_name: Atieh, Virginia, APN",
            "provider_ka_name: Khan, Basma, MD",
            "provider_ka_name: Younus, W. Mohammad, MD",
            "provider_ka_name: Huq, U. Irfan",
            "provider_ka_name: Matthews-brown, R. Spring, MD",
            "provider_ka_name: Nadeem, Shahzinah, MD",
            "provider_ka_name: Newsome, J. La-toya, NP",
            "provider_ka_name: Raza, Rubina",
            "provider_ka_name: Sheikh, U. Selim, MD",
            "provider_ka_name: Chaudry, A. Ghazali, M.D.",
            "provider_ka_name: Bresch, David, MD"
        ]
        found_match_1 = False
        found_match_2 = False
        found_match_3 = False

        for provider in providers_1:
            if provider in self.post_data:
                found_match_1 = True
                break  # Exit the loop once a match is found in the first list

        for provider in providers_2:
            if provider in self.post_data:
                found_match_2 = True
                break  # Exit the loop once a match is found in the second list

        for provider in providers_3:
            if provider in self.post_data:
                found_match_3 = True
                break  # Exit the loop once a match is found in the second list
        if found_match_1:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                basic_data = self.get_basic_information()

                history = self.get_histroy()

                template = get_templates(basic_data)

                general = self.combine_the_text(basic_data, history, template)
                lab = get_lab_results()
                final_response = f"{general}. {lab}"

                few_shot_2 = """Write a history of illness of the patient based on the text that I will provide"""
                result_2 = """\
                This is a 42-year-old male who presented today for a follow-up on opioid dependence, ADHD, depression, anxiety, and Lab review.\n \
    
                The patient is following up on Anxiety and continues on (Alprazolam 1mg) which is helping him with his symptoms. He can function and perform his ADL. He states he takes his medications regularly. He denies fatigue, body aches, n/v/d, and constipation. He denies chest pain and shortness of breath. He denies hallucinations, panic attacks, suicidal ideations, and dangerous ideations. He has a good appetite and sleep. The patient is following up on attention deficit disorder and continues on Adderall 5mg in combination with Adderall 20mg. Per the patient, Adderall is helping him to focus and concentrate while reading and doing other tasks. Denies headache or dizziness. Requesting for a prescription renewal.\n \
    
                He is also following up on Lab review results show that Glucose is 100, WBC count 2.9, Absolute 986,\n \
                eGFR is 110, Creatinine is 0.88, WHITE BLOOD CELL COUNT 2.9 HEMOGLOBIN A1c 5.1\n \
    
                **No other medical concerns in today's appointment**.\n \
                """

                system_1 = (f""" You are a medical assistant and you job is to write a history of illness of the patient.
                The text contains the patient demographics, History of  disease or disorder, Medications and Doctor dictation.
                Please write a History of illness based on the text delimited by the triple backticks.lets think step by step.
                First line contains the patient demographics and provided 'history line'. Don't add the medications in this line.
                Second line contains the patient current complains with prescribe medication if available.
                Write the follow up information of disease or disorder in a line separately with only related medications.
                It is necessary to concluded with "**No other medical concerns in today's appointment**".
                Don't add the headings.
                Don't repeat the lines.
                Utilize double asterisks for name, type of visit and medication.
                Make sure all the provided text is added in the output.
                and nothing is missed in the output.
                            """)
                messages_4 = [{'role': 'system', 'content': system_1},
                              {'role': 'user', 'content': f"{self.delimiter}{few_shot_2}{self.delimiter}"},
                              {'role': 'assistant', 'content': result_2},
                              {'role': 'user', 'content': f"{self.delimiter}{final_response}{self.delimiter}"}]
                response = get_completion(messages_4)
                return response
            else:
                basic_data = self.get_basic_information()

                history = self.get_histroy()

                template = get_templates(basic_data)

                general = self.combine_the_text(basic_data, history, template)
                return general
        if found_match_2:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                basic_data = self.get_basic_information()

                history = self.get_histroy()

                template = "Nothing"
                general = self.combine_the_text(basic_data, history, template)
                lab = get_lab_results()
                final_response = f"{general}. {lab}"

                few_shot_2 = """Write a history of illness of the patient based on the text that I will provide"""
                result_2 = """\
                This is a 42-year-old male who presented today for a follow-up on opioid dependence, ADHD, depression, anxiety, and Lab review.\n \

                The patient is following up on Anxiety and continues on (Alprazolam 1mg) which is helping him with his symptoms. He can function and perform his ADL. He states he takes his medications regularly. He denies fatigue, body aches, n/v/d, and constipation. He denies chest pain and shortness of breath. He denies hallucinations, panic attacks, suicidal ideations, and dangerous ideations. He has a good appetite and sleep. The patient is following up on attention deficit disorder and continues on Adderall 5mg in combination with Adderall 20mg. Per the patient, Adderall is helping him to focus and concentrate while reading and doing other tasks. Denies headache or dizziness. Requesting for a prescription renewal.\n \

                He is also following up on Lab review results show that Glucose is 100, WBC count 2.9, Absolute 986,\n \
                eGFR is 110, Creatinine is 0.88, WHITE BLOOD CELL COUNT 2.9 HEMOGLOBIN A1c 5.1\n \

                **No other medical concerns in today's appointment**.\n \
                """

                system_1 = (f""" You are a medical assistant and you job is to write a history of illness of the patient.
                The text contains the patient demographics, History of  disease or disorder, Medications and Doctor dictation.
                Please write a History of illness based on the text delimited by the triple backticks.lets think step by step.
                First line contains the patient demographics and provided 'history line'. Don't add the medications in this line.
                Second line contains the patient current complains with prescribe medication if available.
                Write the follow up information of disease or disorder in a line separately with only related medications.
                It is necessary to concluded with "**No other medical concerns in today's appointment**".
                Don't add the headings.
                Don't repeat the lines.
                Utilize double asterisks for name, type of visit and medication.
                Make sure all the provided text is added in the output, 
                and nothing is missed in the output.
                            """)
                messages_4 = [{'role': 'system', 'content': system_1},
                              {'role': 'user', 'content': f"{self.delimiter}{few_shot_2}{self.delimiter}"},
                              {'role': 'assistant', 'content': result_2},
                              {'role': 'user', 'content': f"{self.delimiter}{final_response}{self.delimiter}"}]
                response = get_completion(messages_4)
                return response
            else:
                basic_data = self.get_basic_information()
                history = self.get_histroy()
                template = "Nothing"
                general = self.combine_the_text(basic_data, history, template)
                return general
        if found_match_3:
            basic_data = self.get_basic_information()

            history = self.get_histroy()

            template = "Nothing"
            system_2 = f"""
                    You are a medical assistant and you job is to write a history of illness of the patient.
                    The text contains the patient demographics, History of  disease or disorder, Medications and Doctor dictation.
                    Please write a History of illness based on the text delimited by the triple backticks.lets think step by step.
                    First line contains the patient demographics and provided 'history line'. Don't add the medications in this line.
                    Second line contains the patient current complains.
                    It is necessary to concluded with "**No other medical concerns in today's appointment**".
                    Don't add the headings.
                    Don't repeat the lines.
                    Don't write more than 4 lines.
                    Write lines separately.
                """
            prompt_2 = f"""
                            Please write a History of illness in based on the text delimited by the triple backticks,\
                            ```{basic_data}```
                            the the patient history is delimited by triple dashes,
                            ---{history}---
                            other text is delimited by triple brackets.
                            {{{template}}}
                            and concluded with "No other medical concerns in today's appointment".
                            """
            few_shot_1 = """Write a history of illness of the patient based on the text that I will provide"""
            result_1 = """\
                    Calvin Mcrae, a 71-year-old male, came in for a follow-up visit. \n \
                    He has a medical history of Hypertension (HTN), Hypothyroidism, and a history of cellulitis of the face.\n \
                    He complains of the upper lip infection.\n \
                    **No other medical concerns in today's appointment**.\n \
                    """
            messages_2 = [{'role': 'system', 'content': system_2},
                          {'role': 'user', 'content': f"{self.delimiter}{few_shot_1}{self.delimiter}"},
                          {'role': 'assistant', 'content': result_1},
                          {'role': 'user', 'content': f"{self.delimiter}{prompt_2}{self.delimiter}"}]

            response = get_completion(messages_2)
            return response
        else:
            qwe = "Change the provider name"
            return qwe
class plan_of_care:
    def __init__(self, post_date, delimiter="####"):
        self.post_data = post_date
        self.delimiter = delimiter
        medication_start = post_date.find("cutformhere:") + len("cutformhere:")
        medication_end = post_date.find("Doctor dictation")
        self.medications_text = post_date[medication_start:medication_end].strip()
        dictation_start = post_date.find("Doctor dictation:") + len("Doctor dictation:")
        doctor_semi = post_date[dictation_start:].strip()
        self.diagnosis = extract_text(doctor_semi)
        self.dictation_final = get_dictation(doctor_semi)
        print(self.dictation_final)
        result = self.final()
        self.result = result
    def template_1(self):
        prompt = f"""
            You are a medical assistant. Your job is to organize the medications with the diseases and disorders mentioned in the text by following the \
            rules listed below. The medications and disease or disorder will be provided. Let’s think step by step.

            Rules for this task:
            1) First extract the one relatable disease or disorder for the medication if mentioned in the provided text, and \
            than organize the medication with the associated disease and disorder mentioned in the provided text.
            2) Only organizes the medication with one disease or disorder. But it is possible that multiple medications \
            organize with one disease or disorder if prescribed for same therapeutic use.
            3) Include only medication names, dosage, and SIG (instructions for use).
            4) Don't add the disease or disorder in the output if no medication is organized with that disease or disorder.
            5) Don't add Start Date, Prescribe Date, End Date and Qty of the medication.
            6) If the disease and disorder is not organize with the medication, than don't add this disease or disorder in the \
            final output
            7) Check If the medication is not grouped with the disease or disorder, then add it to \
            the "Other Medications" section.
            8) At the end add a concise plan of care with 4 to 5 lines for disease or disorder that i will provide.
            9) Utilize double asterisks for all headings.
            10) Utilize double asterisks for all "medications" with their "SIG".
            11) Don't suggest any disease, disorder or symptoms for any medication. 
            12) If the prompt contain "Other medications". please write these medications at the end with the heading.
            13) Don't add heading of "Plan of care:"
            14) Don't add ICD-10 codes.
            15) It is Mandatory to conclude the plan of care with this line "Follow-up as scheduled"

            """
        user_text = f"""
           Write a concise plan of care with 4 to 5 lines for disease or disorder with the medication and the doctor dictation.\
           The disease or disorders are delimited by triple backticks.
           '''{self.diagnosis}'''
              
           The medications are delimited by triple dashes.
           ---{self.medications_text}---
           
           The doctor dictation is delimited by triple hashtags.
           ###{self.dictation_final}###
            """

        few_shot_user_1 = """
         Write a concise plan of care with 4 to 5 lines for disease or disorder if the medication that is the only\
         mentioned in the text delimited by triple backticks is organize with it.
         Don't write the disease or disorder in the output if "no medication is mentioned in the text" for the disease or disorder.
            """
        few_shot_assistant_1 = """
        **Asthma**:
        
            - **Ventolin HFA 90 mcg/actuation aerosol inhaler. Sig: 2 puffs every 6 hours as needed.**
            - **Breo Ellipta 100 mcg-25 mcg/dose powder for inhalation. Sig: 1 puff daily.**
            - Avoid triggers that may worsen cough variant asthma, such as cold air, smoke, and allergens.
            - Use a peak flow meter to monitor lung function and adjust medication use as needed.
            - Follow an asthma action plan provided by healthcare provider.
            - If symptoms persist or worsen, consult with healthcare provider for further evaluation and potential adjustment \
            of treatment plan.

        **Gastro-esophageal reflux disease:

            - **Simethicone 80 mg chewable tablet, Sig: One Tablet Daily q6h.**
            - Avoid trigger foods and beverages that can worsen symptoms, such as spicy foods, citrus fruits, and caffeine.
            - Eat smaller, more frequent meals and avoid lying down immediately after eating.
            - Elevate the head of the bed to reduce nighttime reflux.
            - If symptoms persist or worsen, consult with your healthcare provider for further evaluation and potential \
            alternative treatment options.

        **Other Medications**:

            - **Ascorbic Acid (Vitamin C) 500 mg Tablet\n, Sig: Take 1 tablet (500mg) by oral route once daily.**

        **Follow-up as scheduled**
                    """

        messages = [{'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"}]

        response_5 = get_completion(messages)

        return response_5
    def template_2(self):

        text_0 = get_lab_results()

        text = f"""
        The labs readings of patient is delimited by triple backticks.
        ```{text_0}```
        and the medications are mentioned in the text delimited by triple dashes.
        ---{self.medications_text}---
    """
        messages = [
            {
                "role": "system",
                "content": f"""Your job is to write a plan of care based on the text that i will provide. Lets think step by step:
                    Write the date on which the lab were conducted.
                    First, It is mandatory to write the main headings under double asterisks if added.
                    Than add the readings under the main heading.
                    Don't write the patient details or additional data.
                    Don't write the reference intervals in the output.
                    Don't write the Indications.
                    Don't suggest any potential issue based on findings.
                    Make sure nothing is missed in the output.
                    Also write one line of plan of care below abnormal values of each main heading. 
                    Don't add the heading of "plan of care".
                    Write the mentioned medications in the related test after the advice.
                    Double asterisks the test names.
                    It is Mandatory to conclude with this line "Follow-up as scheduled"
                """
            },
            {
                "role": "user",
                "content": "Your job is to write a plan of care based on the lab report.Don't add the results in the"
                           "future outputs. Only remember the format."
            },
            {
                "role": "assistant",
                "content": f"""

                **Labs done on:** 11/27/2023

                **P14+eGFR:**
                **Glucose** 112 (high). 
                Continue to follow a low carbohydrate diet and monitor blood sugar levels regularly.

                **Lipid Panel:**
                **Triglycerides** 164 (high).
                Maintain a low-fat diet and continue regular exercises.


                **Hemoglobin A1c:**
                **Hemoglobin A1c** 6.6 (high). 
                Continue to monitor blood sugar levels and follows a diabetes management plan.

                **CBC With Differential/Platelet:**
                **MCH** 26.1 (low).
                **MCHC** 31.4 (low).
                **Eos (Absolute)** 0.6 (high).
                Continue taking montelukast 10 mg tablet as prescribed.

                **Vitamin D, 25-Hydroxy:**
                **Vitamin D, 25-Hydroxy** 23.3 (low). 
                Continue taking Vitamin D3 125 mcg (5,000 unit) tablet daily as prescribed.

                **Follow-up as scheduled**
    """
            },
            {
                "role": "user",
                "content": f"{self.delimiter}{text}{self.delimiter}"
            }
        ]

        response = get_completion(messages)

        return response

    def template_3(self):
        text = self.post_data
        extracted_text = ""
        index_of_furthermore = text.find("cutformhere: ")
        if index_of_furthermore != -1:
            extracted_text = text[index_of_furthermore + len("cutformhere: "):]


        messages = [
            {"role": "system", "content": f"""
            Your job is to write a plan of care for the patient based on the patient_doctor conversation that \
              I will provide.Let's think step by step.
              The text also contains the disease or disorders and medications name.
              Make sure all the mentioned medications should be written under the heading of related disease or disorder. Don't \
              suggest the brand name.
              Don't write the separate heading of "Medications", "Referral" and "FollowUp" at the end.
              Don't add the additional headings.
              Don't add the start date and end of medications.
              Make sure all the conversation is added in the output.
              Make sure all the related information is written under one Heading.
              Write the test related text under one heading that is blood work. If the related information is already \
              written in the heading of disease or disorder than don't write it in the heading of blood work.
              Don't repeat the things.
              Utilize double asterisks for all headings.
              Utilize double asterisks for all medications in the output text.
              At the end make sure that the output doesn't contain separate heading of medication. If separate heading of \
              medication is present than it is mandatory to adjust it in the heading of most related disease or disorder, and 
              remove the heading. 
              Write the pharmacy related text also in heading of disease or disorder.
              Don't write the "start Date", "End Date" and the line "The prescription was successfully delivered to the /
              ultimate server.
              It is Mandatory to conclude the plan of care with this line "Follow-up as scheduled"
              Make sure nothing is missed in the output """},

            {"role": "user", "content": "Your job is to write a plan of care for the patient. Don't add the outputs in the\
             future outputs."},
            {"role": "assistant", "content": f"""
            **Anemia**
             None
            **URTI**
            The patient has developed a cold with cough and congestion. Denies body aches. We will call Augmentin 500 mg along with Promathazine to take as directed. Monitor the patient's progress and adjust treatment as necessary.
            **Hypertension**
            The patient's hypertension is relatively well controlled and he is compliant with his medications. Requests for refill which we will do today. Continue current medication regimen and monitor blood pressure regularly. Encourage lifestyle modifications such as a healthy diet and regular exercise.
            **Cervical and Lumbar Herniated Discs**
            The patient has a history of cervical herniated discs with cervical radiculopathy and lumbar herniated discs with sciatica. He is currently under the care of an orthopedic specialist. Ensure the patient continues to follow up with the orthopedic specialist.
            **Osteoarthritis of the Knee**
            The patient has severe osteoarthritis of the knee and has received gel shots twice without significant improvement. If there is no improvement after the third shot, discuss the possibility of total knee replacements bilaterally with the orthopedic specialist.
            **Ambulatory dysfunction/Sciatica/Back pain**
            The patient has a hx of Sciatica and have ambulatory dysfunction, needs a new wheelchair as his current one is broken and non-functional. Renew the referral for a wheelchair to improve his mobility around the house and outside.
            The patient needs refills on all of his medications. Ensure all prescriptions are updated and refilled as necessary.
            F/u as needed."""},
            {"role": "user", "content": f"{self.delimiter}{extracted_text}{self.delimiter}"}]
        response = get_completion(messages)

        return response

    def template_4(self):
        prompt = """
        you are a medical assistant. You job is to write a plan of care by following the mentioned rules. let's think step by step.
            1) First extract the only one associate disease or disorder for each medication if mentioned in the provided text.
            2) And than write all the medications in the first line separated with comma and write associated disease and disorder with lines plan of care and medication mentioned in the provided text.
            3) Write the one name of the disease or disorder as the heading and than write lines of plan of care in the form of paragraph.
            4) Write the short form of disease or disorders
            5) Include only medication names. Don't add dosage, and SIG (instructions for use).
            6) Don't add ICD-10 codes.
            7) Don't add Start Date, Prescribe Date, End Date and Qty of the medication.
            8) If the disease and disorder is not related with the medication, than don't add the disease or disorder in the \
            output.
            9) Add a concise plan of care with 4 to 5 lines for disease or disorder that i will provide.
            10) Utilize double asterisks for all headings.
            11) Utilize double asterisks for all "medications".
            12) Don't suggest any disease, disorder or symptoms for any medication. 
            13) Don't add heading of "Plan of care, Disease or disorder and "Medication".
            14) Don't add the disease or disorder in the output if no medication is mentioned in the provided text.
            15) If no medication is mentioned in the provided text than return these lines and also add at the end of every output if the medication is available.
            "**Compliance** with medications has been stressed.
            Continue other medications.
            Side effects, risks, and complications were clearly explained and the patient verbalized understanding and was given the opportunity to ask questions.
            Relaxation techniques were discussed, stress avoidance was reviewed, and medication and yoga were encouraged."
            16) It is Mandatory to conclude the plan of care with this line "Follow-up as scheduled"
        """

        user_text = f"""
           Write a concise plan of care with 4 to 5 lines for disease or disorder if the related medication and the doctor dication is linked with it.
           It is mandatory to write only one heading of disease or disorder for one mentioned medication.
           Don't add the disease or disorder in the output if no medication is mentioned in the provided text.
           The disease or disorders are delimited by triple backticks.
           '''{self.diagnosis}'''
              
           The medications are delimited by triple dashes.
           ---{self.medications_text}---
           
           The doctor dictation is delimited by triple hashtags.
           ###{self.dictation_final}###

            """
        few_shot_user_1 = """
        Write a plan of care. Don't add the output in the future responses. 
        write only one heading of disease or disorder for one mentioned medication.
        
        """
        few_shot_user_2 = """
        Write a plan of care. Don't add the output in the future responses.
        Write only one heading of disease or disorder for one mentioned medication.

        """
        few_shot_assistant_1 = """
        Continue with metformin and levothyroxine.
        **Hyperlipidemia**: Dietary instruction about hyperlipidemia given to the patient. Eat a diet low in saturated and trans fats. Include lots of fruits, vegetables, beans, nuts, whole grains, and fish regularly into your diet. Stop eating red meat and processed meats like bacon, sausage, and cold cuts. Drink skim or low-fat milk.
        **GERD**: Recommended to eat slowly, chew well every bite for at least 20-25 times before swallowing. Do not talk, read or watch TV while eating. Eat small portions, frequently, at least every 3-h. No large meals. Avoid Tobacco, alcohol, greasy, acidic, or spicy food, coffee, and carbonated beverages. Sip plain water between bites. Avoid eating within 2 hours before bedtime. Walk after the meal.
        Compliance with medications has been stressed. Continue other medications. Side effects, risks, and complications were clearly explained and the patient verbalized understanding and was given the opportunity to ask questions. Relaxation techniques were discussed, stress avoidance was reviewed, medication and yoga were encouraged.
        
        **Follow-up as scheduled**.
        
        """
        few_shot_assistant_2 = """
        "**Compliance** with medications has been stressed.
        Continue other medications.
        Side effects, risks, and complications were clearly explained and the patient verbalized understanding and was given the opportunity to ask questions.
        Relaxation techniques were discussed, stress avoidance was reviewed, and medication and yoga were encouraged."

        **Follow-up as scheduled**.

        """

        messages = [{'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_2}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_2},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"}]

        response = get_completion(messages)

        return response

    def template_5(self):
        class PlanOfCareGUI:
            def __init__(self):
                self.selection_window = None
                self.checkbox_vars = {}
                self.notes = ""

            def submit_notes(self):
                self.notes = self.text_box.get("1.0", "end-1c")  # Get the text from the text box
                print("Health Maintenance:")
                print(self.notes)
                self.window.destroy()  # Close the main window
                self.show_selection_window()

            def cancel_submission(self):
                self.window.destroy()  # Close the main window
                self.show_selection_window()

            def submit_selected_lines(self):
                selected_lines = [line for line, var in self.checkbox_vars.items() if var.get()]
                print("Patient Goals:")
                for line in selected_lines:
                    print(line)
                self.selection_window.destroy()

            def select_all_lines(self):
                for var in self.checkbox_vars.values():
                    var.set(1)

            def cancel_selection(self):
                self.selection_window.destroy()

            def show_selection_window(self):
                self.selection_window = tk.Tk()
                self.selection_window.attributes('-topmost', True)  # Make the file dialog top-level

                self.selection_window.title("Select Lines")

                lines = [
                    "BP systolic less than 130 Diastolic less than 80",
                    "TC less than 180",
                    "Trig less than 100",
                    "HDL Greater than 50",
                    "LDL less than 80",
                    "A1C 6.0% or less"
                ]

                for line in lines:
                    var = tk.BooleanVar()
                    self.checkbox_vars[line] = var
                    checkbox = Checkbutton(self.selection_window, text=line, variable=var)
                    checkbox.pack(anchor=tk.W)

                select_all_button = tk.Button(self.selection_window, text="Select All", command=self.select_all_lines)
                select_all_button.pack()

                submit_button = tk.Button(self.selection_window, text="Submit Selected Lines",
                                          command=self.submit_selected_lines)
                submit_button.pack()

                cancel_button = tk.Button(self.selection_window, text="Cancel Selection", command=self.cancel_selection)
                cancel_button.pack()

                self.selection_window.mainloop()

            def run_main_window(self):
                self.window = tk.Tk()
                self.window.attributes('-topmost', True)  # Make the file dialog top-level
                self.window.title("Note Submission")

                self.text_box = tk.Text(self.window, height=10, width=40)
                self.text_box.pack(pady=10)

                submit_button = tk.Button(self.window, text="Submit Notes", command=self.submit_notes)
                submit_button.pack(side=tk.LEFT, padx=5)

                cancel_button = tk.Button(self.window, text="Cancel", command=self.cancel_submission)
                cancel_button.pack(side=tk.RIGHT, padx=5)

                self.window.mainloop()

        gui = PlanOfCareGUI()
        gui.run_main_window()
        prompt_0 = f"""
         You are expert in calculating dates. Your job is to find the today date from the text delimited by triple \
         backticks and return the medications that patient is taking after comparing with the "start date" and "End date". 
         At the end also return the "Patient Doctor conversation:"
    """
        messages = [{'role': 'system', 'content': prompt_0},
                    {'role': 'user', 'content': f"{self.delimiter}{self.post_data}{self.delimiter}"}]
        response_0 = get_completion(messages)

        prompt = f"""
          write a plan of care for the patient based on the patient_doctor conversation delimited by triple hashtags.
          ###{response_0}### 
          The text delimited by triple dashes contains the "Text". Please write this "text" under the heading of "Health Maintenance"\
          Don't add the headings if no text is available.
            ---{gui.notes}---
          The text delimited by triple backticks contains the lines. Please write these lines in the bullets under the \
          heading of "Patient Goals"
          Don't add the headings if no text is available.
          '''{gui.checkbox_vars.keys()}'''
    """

        messages = [
            {"role": "system", "content": f"""
                Your job is to write a plan of care for the patient based on the patient_doctor conversation that \
                  I will provide.Let's think step by step.
                  The text also contains the disease or disorders and medications name.
                  Make sure all the mentioned medications that patient is taking should be written in the heading of the \
                  disease or disorder. Don't suggest the brand name.
                  Don't add the start and end date and QTY of the medication.
                  Don't add the heading of "Medications", "Referral", "Advice" and "Follow-Up" at the end.
                  Don't add the additional headings.
                  Make sure all the conversation is added in the output under the heading of disease or disorder.
                  Make sure all the related information is written under one Heading.
                  Write the labs and radiology related text under one heading that is "Health Maintenance". If the related information is already \
                  written in the heading of the disease or disorder than don't write it in the heading of blood work.
                  Don't repeat the things.
                  Utilize double asterisks for all headings.
                  It is mandatory to write one line of advice in every heading of disease or disorder in next line.
                  Utilize double asterisks for all medications, vitamins and supplements in the output text.
                  It is Mandatory to conclude the plan of care with this line "Follow-up as scheduled". If the text reflects that\
                  some kind of labs and radiology test has been ordered than conclude with this line "Follow-up as lab done".

                  Make sure nothing is missed in the output """},

            {"role": "user", "content": "Your job is to write a plan of care for the patient. Don't add the previous outputs in the\
                 future outputs."},
            {"role": "assistant", "content": f"""
                **Hypothyroidism:** On levothyroxine 75 mcg daily. Refill given as per pt request. Will check levels

                **HTN**: On lisinopril 20 mg daily, metoprolol 50 mg daily. 
                Advised to monitor BP on daily basis. Refill given

                **Vitamin D**: On vitamin Supplements from his cardiologist. 
                Refill given as per pt request.

                **HLD**: On lipitor. Refill given. Will check the levels.
                Do exercise, take low cholesterol diet, Avoid eating spicy foods

                **Bladder incontinence**: Referral sent to Dr fingermann

                **Health Maintenance**: Had colonoscopy done from hamilton GI in 2021.
                Routine labs ordered

                f/u as labs done

        """},
            {"role": "user", "content": f"{self.delimiter}{prompt}{self.delimiter}"}]

        response = get_completion(messages)

        return response

    def final(self):
        response = None
        if "provider_ka_name: Matthews-brown, R. Spring, MD" in self.post_data:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                response = self.template_2()
            else:
                response = self.template_1()
        elif "provider_ka_name: Diaz, Johannelda, NP" in self.post_data:
            response = self.template_1()
        elif "provider_ka_name: Raza, Rubina" in self.post_data:
            response = self.template_3()
        elif "provider_ka_name: Khan, Basma, MD" in self.post_data:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                response = self.template_2()
            else:
                response = self.template_1()
        elif "provider_ka_name: Huynh-nguyen, P. Anh, NP" in self.post_data:
            response = self.template_4()
        elif "provider_ka_name: Younus, W. Mohammad, MD" in self.post_data:
            response = self.template_1()
        elif "provider_ka_name: Ahmad, S. Syed, MD" in self.post_data:
            response = self.template_4()
        elif "provider_ka_name: Sheikh, U. Selim, MD" in self.post_data:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                response = self.template_2()
            else:
                response = self.template_5()
        elif "provider_ka_name: Castillo, Kendie, NP" in self.post_data:
            response = self.template_4()
        elif "provider_ka_name: Huq, U. Irfan" in self.post_data:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                response = self.template_2()
            else:
                response = self.template_4()
        elif "provider_ka_name: Oluwagbamila, Geralda, NP" in self.post_data:
            response = self.template_4()
        elif "provider_ka_name: Viaje, Mabrigida, NP" in self.post_data:
            response = self.template_4()
        elif "provider_ka_name: Chowdhury, Bhanwarlal, M.D." in self.post_data:
            response = self.template_1()
        elif "provider_ka_name: Brown, Harold, MD" in self.post_data:
            response = self.template_4()
        elif "provider_ka_name: Chavez, Hazel, NP" in self.post_data:
            response = self.template_4()
        elif "provider_ka_name: Asiamah-asare, Vida-lynn, NP" in self.post_data:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                response = self.template_2()
            else:
                response = self.template_4()
        elif "provider_ka_name: Newsome, J. La-toya, NP" in self.post_data:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                response = self.template_2()
            else:
                response = self.template_1()
        elif "provider_ka_name: Nadeem, Shahzinah, MD" in self.post_data:
            if "Type of visit: Lab/Radiology Review" in self.post_data:
                response = self.template_2()
            else:
                response = self.template_1()

        return response

class review_of_system:
    def __init__(self, post_date, delimiter="####"):
        self.post_data = post_date
        self.delimiter = delimiter
        result = self.final()
        self.result = result
    def get_symptoms(self):
        user_text = f"""
                ```{self.post_data}```
                You are a medical assistant. Your job is to identify the symptoms from the provided text delimited by triple backticks\
                Next, extract and compile symptoms from the symptoms_list\
                that are possibly related to the identified symptoms. \
                Don't suggest any symptoms if it is not mentioned in the symptoms_list. \
                Also add the symptoms in the output list that are not in the symptoms_list. \
                It is mandatory that output should be in Python list.
                Return empty list if no symptoms are present in the provided text.
                """
        symptoms_list = """

            Your job is to extract the one symptom from this symptoms_list based on the identified symptoms.

            symptoms_list = [
                "Rashes", "Earache", "Discharge (possibly ear or nose related)",
                "Ringing or decreased hearing", "Sneezing", "Sore throat",
                "Stuffy or runny nose", "Congestion", "Cough", "Shortness of breath",
                "Wheezing", "Mass or lump (possibly in the breast)",
                "Abdominal pain", "Change in bowel habits", "Constipation",
                "Diarrhea", "GERD (Gastro-esophageal Reflux Disease)", "Nausea",
                "Vomiting", "Dysuria (painful urination)",
                "Discharges (possibly genitourinary related)", "Cyanosis", "Edema",
                "Dizziness", "Headache", "Neuropathic pain", "Numbness", "Paralysis",
                "Seizures", "Tremors", "Back pain", "Joint pain", "Joint swelling",
                "Muscle cramps", "Muscle weakness", "Anxiety", "Depression",
                "Insomnia", "Opioid dependence", "Chest pain", "Palpitations",
                "Blurred vision", "Vision loss", "Eye discharge", "Eye itching",
                "Eye pain", "Abnormal bruising", "Bleeding", "Lymphadenopathy (enlarged lymph nodes)",
                "Excessive thirst", "Excessive hunger", "Heat intolerance", "Cold intolerance", "Hypertension",
                "ADHD", "Diabetes Mellitus", "Post-Traumatic Stress Disorder",
                "Asthma", "Urinary Tract Infection", "Migraine (Neurologic)",
                "Convulsions (Neurologic)", "Joint Pain", "Arthritis", "Osteoarthritis",
                "Pain in Hand", "Pain in Foot", "Knee Pain", "Opioid Dependence",
                "Depressive Disorder", "Stress Disorder", "Hyperlipidemia",
                "Hyperthyroidism", "Hypothyroidism"
            ]
        """
        few_shot_user_1 = """
         You are a medical assistant. Your job is to identify the symptoms from the provided text delimited by triple backticks\
                        Next, extract and compile symptoms from the symptoms_list\
                        that is possibly related to the identified symptoms.
        """

        few_shot_assistant_1 = """
        ["Shortness of breath", "Cough"]
        """
        messages = [{'role': 'system', 'content': symptoms_list},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"}]

        response = get_completion(messages)

        return response

    def final(self):
        symptoms = self.get_symptoms()
        patient_data = """
            "**Skin:** Patient denies rashes",
            "**Ear/nose/throat:** Patient denies, Earache or discharge, Ringing or decreased hearing, Sneezing, Sore throat, Stuffy or runny nose",
            "**Lungs:** Patient denies, Congestion, cough, Shortness of breath, Wheezing",
            "**Breast:** Patient denies, Mass or Lump",
            "**Abdomen:** Patient denies, Abdominal pain, change in bowel habits, Constipation, Diarrhea, GERD, Nausea, Vomiting",
            "**GenitoUrinary:** Patient denies, Dysuria, Discharges",
            "**Extremities:** Patient denies, Cyanosis, Edema",
            "**Neurologic:** Patient denies, Dizziness, Headache, Neuropathic pain, Numbness, paralysis, Seizures, Tremors",
            "**Musculoskeletal:** Patient denies, Back pain, Joint pain, Joint swelling, Muscle cramps, Muscle weakness, Breakthrough pain",
            "**Psychiatric:** Patient denies, Anxiety, Depression, Insomnia, Opioid dependence",
            "**Cardiovascular:** Patient denies, Chest pain, Palpitation",
            "**Eyes:** Patient denies, Blurred or vision loss, Discharge itching or eye pain",
            "**Heme/lymphatic:** Patient denies, Abnormal bruising, Bleeding, Lymphadenopathy",
            "**Endocrine:** Patient denies, Excessive thirst or hunger, Heat or cold intolerance, Skin or hair changes, Weight gain or loss",
            "**Dentistry:** Patient denies, Toothache"
        """
        system = """
        you are a medical assistant. Your job is to upgrade the template lines based on the symptoms lines based on the symptoms
        after adding the line "patient complains of "Symptom" at the end of the that line not in the middle.
        Return the template with no changes if no symptoms are given in the provided text.
        Don't add extra text in the output.
        """
        user_text = f"""
         You are a medical assistant. Your job is to rewrite the template lines
         {patient_data} after adding the line "patient complains of "symptom"
         based on the symptoms list delimited by triple backticks.
         '''{symptoms}'''
        Use double asterisks for the heading and the added line.
        Make sure all the provided text is added in the output.
        """
        few_shot_user_1 = """
        You are a medical assistant. Your job is to upgrade the template lines based on the symptoms lines based on the symptoms
        after adding the line "patient complains of "Symptom"
        """
        few_shot_assistant_1 = """
            **Skin:** Patient denies rashes.
            **Ear/nose/throat:** Patient denies, Earache or discharge, Ringing or decreased hearing, Sneezing, Sore throat, Stuffy or runny nose.
            **Lungs:** Patient denies, Congestion, cough, Shortness of breath, Wheezing.
            **Breast:** Patient denies, Mass or Lump".
            **Abdomen:** Patient denies, Abdominal pain, change in bowel habits, Constipation, Diarrhea, GERD, Nausea, Vomiting.
            **GenitoUrinary:** Patient denies, Dysuria, Discharges".
            **Extremities:** Patient denies, Cyanosis, Edema".
            **Neurologic:** Patient denies, Dizziness, Headache, Neuropathic pain, Numbness, paralysis, Seizures, Tremors.
            **Musculoskeletal:** Patient denies, Joint pain, Joint swelling, Muscle cramps, Muscle weakness, Breakthrough pain. **Patient complains of back pain**
            **Psychiatric:** Patient denies, Anxiety, Depression, Insomnia, Opioid dependence.
            **Cardiovascular:** Patient denies, Chest pain, Palpitation.
            **Eyes:** Patient denies, Blurred or vision loss, Discharge itching or eye pain.
            **Heme/lymphatic:** Patient denies, Abnormal bruising, Bleeding, Lymphadenopathy.
            **Endocrine:** Patient denies, Excessive thirst or hunger, Heat or cold intolerance, Skin or hair changes, Weight gain or loss.
            **Dentistry:** Patient denies, Toothache. 
        """
        few_shot_user_2 = """
        You are a medical assistant. Your job is to upgrade the template lines based on the symptoms lines based on the symptoms
        after adding the line "patient complains of "Symptom"
        """
        few_shot_assistant_2 = """
            **Skin:** Patient denies rashes.
            **Ear/nose/throat:** Patient denies, Earache or discharge, Ringing or decreased hearing, Sneezing, Sore throat, Stuffy or runny nose.
            **Lungs:** Patient denies, Congestion, cough, Shortness of breath, Wheezing.
            **Breast:** Patient denies, Mass or Lump".
            **Abdomen:** Patient denies, Abdominal pain, change in bowel habits, Constipation, Diarrhea, GERD, Nausea, Vomiting.
            **GenitoUrinary:** Patient denies, Dysuria, Discharges".
            **Extremities:** Patient denies, Cyanosis, Edema".
            **Neurologic:** Patient denies, Dizziness, Headache, Neuropathic pain, Numbness, paralysis, Seizures, Tremors.
            "**Musculoskeletal:** Patient denies, Back pain, Joint pain, Joint swelling, Muscle cramps, Muscle weakness, Breakthrough pain".
            **Psychiatric:** Patient denies, Anxiety, Depression, Insomnia, Opioid dependence.
            **Cardiovascular:** Patient denies, Chest pain, Palpitation.
            **Eyes:** Patient denies, Blurred or vision loss, Discharge itching or eye pain.
            **Heme/lymphatic:** Patient denies, Abnormal bruising, Bleeding, Lymphadenopathy.
            **Endocrine:** Patient denies, Excessive thirst or hunger, Heat or cold intolerance, Skin or hair changes, Weight gain or loss.
            **Dentistry:** Patient denies, Toothache. 
        """
        messages = [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_2}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_2},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"}]

        response = get_completion(messages)

        return response
class physical_exam:
    def __init__(self, post_date, delimiter="####"):
        self.post_data = post_date
        self.delimiter = delimiter
        result = self.final()
        self.result = result
    def final(self):
        response_1 = ""
        if "Type of visit: Follow Up" in self.post_data:
            response_1 = "Patient is AAO x 3. Not in acute distress. Breathing is non-labored. Normal respiratory effort. The affect is normal and appropriate."
        elif "Type of visit: Office Visit" in self.post_data:
            response_1 = "Well-nourished and well-developed; in no acute distress. Breathing is non-labored, with normal respiratory effort. The affect is normal and appropriate."
        elif "Type of visit: Lab/Radiology Review" in self.post_data:
            response_1 = "Well-nourished and well-developed; in no acute distress. Breathing is non-labored, with normal respiratory effort. The affect is normal and appropriate."
        else:
            "Physical exam for this is not developed"
        return response_1

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Titan is ready for charting!")
    httpd.serve_forever()


if __name__ == '__main__':
    run()

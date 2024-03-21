import openai
from extra_functions import get_completion, clear_lines_above_and_containing, get_cpt_code
from hpi import get_templates


def task(task_string, post_date):
    if "Task 1:" == task_string:
        instance = histroy_of_illness(post_date)
        response = instance.result
    else:
        response = "Task is not justified"
    return response
class histroy_of_illness:
    def __init__(self, post_date, delimiter="####"):
        self.post_date = post_date
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
        ```{self.post_date}```
        """
        messages_0 = [
            {'role': 'system', 'content': system_0},
            {'role': 'user', 'content': f"{self.delimiter}{prompt_0}{self.delimiter}"}
        ]
        basic_info = get_completion(messages_0)
        print(basic_info)
        return basic_info

    def get_history(self):
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
        ```{self.post_date}```
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
        # if "Type of visit: Lab/Radiology Review" in self.post_date:
        #     basic_data = self.get_basic_information()

        #     history = self.get_history()

        #     template = get_templates(basic_data)

        #     general = self.combine_the_text(basic_data, history, template)
        #     lab = get_lab_results()
        #     final_response = f"{general}. {lab}"

        #     few_shot_2 = """Write a history of illness of the patient based on the text that I will provide"""
        #     result_2 = """\
        #     This is a 42-year-old male who presented today for a follow-up on opioid dependence, ADHD, depression, anxiety, and Lab review.\n \

        #     The patient is following up on Anxiety and continues on (Alprazolam 1mg) which is helping him with his symptoms. He can function and perform his ADL. He states he takes his medications regularly. He denies fatigue, body aches, n/v/d, and constipation. He denies chest pain and shortness of breath. He denies hallucinations, panic attacks, suicidal ideations, and dangerous ideations. He has a good appetite and sleep. The patient is following up on attention deficit disorder and continues on Adderall 5mg in combination with Adderall 20mg. Per the patient, Adderall is helping him to focus and concentrate while reading and doing other tasks. Denies headache or dizziness. Requesting for a prescription renewal.\n \

        #     He is also following up on Lab review results show that Glucose is 100, WBC count 2.9, Absolute 986,\n \
        #     eGFR is 110, Creatinine is 0.88, WHITE BLOOD CELL COUNT 2.9 HEMOGLOBIN A1c 5.1\n \

        #     **No other medical concerns in today's appointment**.\n \
        #     """

        #     system_1 = (f""" You are a medical assistant and you job is to write a history of illness of the patient.
        #     The text contains the patient demographics, History of  disease or disorder, Medications and Doctor dictation.
        #     Please write a History of illness based on the text delimited by the triple backticks.lets think step by step.
        #     First line contains the patient demographics and provided 'history line'. Don't add the medications in this line.
        #     Second line contains the patient current complains with prescribe medication if available.
        #     Write the follow up information of disease or disorder in a line separately with only related medications.
        #     It is necessary to concluded with "**No other medical concerns in today's appointment**".
        #     Don't add the headings.
        #     Don't repeat the lines.
        #     Utilize double asterisks for name, type of visit and medication.
        #     Make sure all the provided text is added in the output.
        #     and nothing is missed in the output.
        #                 """)
        #     messages_4 = [{'role': 'system', 'content': system_1},
        #                   {'role': 'user', 'content': f"{self.delimiter}{few_shot_2}{self.delimiter}"},
        #                   {'role': 'assistant', 'content': result_2},
        #                   {'role': 'user', 'content': f"{self.delimiter}{final_response}{self.delimiter}"}]
        #     response = get_completion(messages_4)
        #     return response
        # else:
        basic_data = self.get_basic_information()

        history = self.get_history()

        template = get_templates(basic_data)

        print(template)

        general = self.combine_the_text(basic_data, history, template)
        return general

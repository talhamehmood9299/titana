import openai
from extra_functions import extract_text, get_completion, get_dictation
from labs_radiology import get_lab_results

def task(task_string, post_date):
    if "Task 1:" == task_string:
        instance = histroy_of_illness(post_date)
        response = instance.result
    elif "Task 2:" == task_string:
        instance = plan_of_care(post_date)
        response = instance.result
    elif "Task 3:" == task_string:
        instance = cpt_code(post_date)
        response = instance.result
    elif "Task 4:" == task_string:
        instance = physical_exam(post_date)
        response = instance.result
    elif "Task 5:" == task_string:
        instance = review_of_system(post_date)
        response = instance.result
    else:
        response = "Task is not justified"
    return response


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

    def final(self):
        basic_data = self.get_basic_information()
        history = self.get_history()
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


    def final(self):

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




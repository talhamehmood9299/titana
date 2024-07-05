import openai
from extra_functions import get_completion, clear_lines_above_and_containing, get_cpt_code
from hpi import gather_information


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
    def __init__(self, post_date, delimiter="####"):
        self.post_date = post_date
        self.delimiter = delimiter
        result = self.final()  # Call the final() method and store the result
        self.result = result  # Store the result as an attribute

    def final(self):
        result = get_cpt_code(self.post_date)
        return result


class histroy_of_illness:
    def __init__(self, post_date, delimiter="####"):
        self.post_date = post_date
        self.delimiter = delimiter
        result = self.final()
        self.result = result

    def get_basic_information(self):
        system_0 = """
        Remove all the disease or disorders after the diagnosis heading mentioned from the text delimited by triple backticks and rearrange the remaining text.
        The headings should be:
        1) Patient demographics.
        2) Type of Visit.
        3) Medications.
        Note: Write only medication name in the medication heading. Don't write the Qty, Start Date, Prescribe Date, End Date and Sig.
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
        # few_shot_user_2 = """
        # Based on the doctor's dictation and mentioned medications, Choose the diseases or disorders that are directly\
        # related to the doctor's dictation and mentioned medications from the text delimited by triple backticks.
        # Don't add the BMI in the output.
        # At the end it is necessary to write the related disease or disorders in one line.
        #     """
        #
        # few_shot_assistant_2 = """
        # 1) Anxiety disorder- related to the doctor's dictation which is mentioned in the text.
        # The patient disease or disorder is Anxiety.
        #  """

        messages_1 = [
            {'role': 'system', 'content': system_1},
            {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
            {'role': 'assistant', 'content': f"{few_shot_assistant_1}"},
            # {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_2}{self.delimiter}"},
            # {'role': 'assistant', 'content': f"{few_shot_assistant_2}"},
            {'role': 'user', 'content': f"{self.delimiter}{prompt_1}"}
        ]
        response = get_completion(messages_1)
        print(response)

        # Split the text into lines
        lines = response.split('\n')

        # Extract the last line
        history = lines[-1].strip()

        return history

    def combine_the_text(self, basic_data, history, complication_past_information):
        system_2 = f"""
        You are a medical assistant and you job is to write a history of illness of the patient.
        The text contains the patient demographics, History of  disease or disorder, Medications and Doctor dictation.
        Please write a History of illness based on the text delimited by the triple backticks.lets think step by step.
        First line contains the patient demographics and provided 'history line'. Don't add the medications in this line.
        Second line contains the patient current complains with medication if available.
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
                {{{complication_past_information}}}
                and concluded with "No other medical concerns in today's appointment".
                """
        few_shot_1 = """Write a history of illness of the patient based on the text that I will provide"""
        result_1 = """\
            **Paiz, Maritza** is 65 year-old female, last seen on April 03, 2024. Not seen in June,\n
            2024 visit as advised for BP check. She is out of her medications for almost a week.\n
            Weight is the same as last visit 187lbs.\n \
        """
        few_shot_2 = """Write a history of illness of the patient based on the text that I will provide"""
        result_2 = """\
            **Watson, Dennis** is 64 year-old male, presented today complaining of constipation.
            He was in the hospital and recently got discharged last week. As per patient he took
            his medications on regular basis except for today. Advised to spread out the
            medication over the entire day and not to take all the medications at one time.
        """
        few_shot_3 = """Write a history of illness of the patient based on the text that I will provide"""
        result_3 = """\
            **Koznowicz, Elizabe** is 57 year-old female who was seen at ER on June 5th, 2024\n
            for upper abdominal pain. Labs ordered. CBC, CMP and LFTs normal. UA\n
            (+) WBC and inflammatory cells,\n
            CAD scan of abdomen showed;\n
            Cholecystectomy\n
            Diverticulitis\n
            Post surgical changes of anterior abdominal wall\n
            LS degenerative disc disease\n
            EKG and US of abdomen normal except for cholecystectomy.\n
            No mammogram.
        """

        messages_2 = [{'role': 'system', 'content': system_2},
                      {'role': 'user', 'content': f"{self.delimiter}{few_shot_1}{self.delimiter}"},
                      {'role': 'assistant', 'content': result_1},
                      {'role': 'user', 'content': f"{self.delimiter}{few_shot_2}{self.delimiter}"},
                      {'role': 'assistant', 'content': result_2},
                      {'role': 'user', 'content': f"{self.delimiter}{few_shot_3}{self.delimiter}"},
                      {'role': 'assistant', 'content': result_3},
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

        complication_past_information = gather_information(basic_data)

        print(complication_past_information)

        general = self.combine_the_text(basic_data, history, complication_past_information)
        return general


class plan_of_care:
    def __init__(self, post_date, delimiter="####"):
        self.post_date = post_date
        self.delimiter = delimiter
        result0 = self.filter_diagnosis()
        result1 = self.lab_results()
        result2 = self.current_medication()
        result3 = self.template()
        result = f"{result0}\n{result1}\n{result2}\n{result3}"
        print(result)
        self.result = result

    def filter_diagnosis(self):
        system = f"""
        You are a medical assistant. Your job is to filter out the disease or disorders from the provided text.lets think step by step.
        First write the heading of "**Impression and Plan:**" in double astrikes.
        Than extract the first 10 patient disease or disorder with their ICD-10 codes form the provided text, 
        and write it in bullets under the heading of "Impression and plan". 
        If the disease or disorder is less than 10 than return all the disease or disorders with their ICD-10 codes 
        form the provided text, and write it in bullets under the heading of "Impression and plan".
        """
        prompt = f"""
        You are a medical assistant. Your job is to filter out the disease or disorders from the text delimited by 
        triple backticks and write under the heading of "**Impression and Plan:**" in double astrikes.
        
        ```{self.post_date}```
        """

        user_text = """"
        You are a medical assistant. Your job is to filter out the disease or disorders from the text delimited by 
        triple backticks and write under the heading of "**Impression and Plan:**" in double astrikes.
        
        """

        assistant_text_1 = """
        R11.0, Nausea 
        R19.7, Diarrhea
        R10.819, Abdominal tenderness
        R11.10, Vomiting
        K52.9, Noninfective gastroenteritis and colitis
        G47.00, Insomnia
        E78.5, Hyperlipidemia
        I16.0, Hypertensive urgency
        R51.9, Headache, unspecified
        E78.2, Mixed hyperlipidemia
        E66.8, Other obesity
        """

        assistant_text_2 = """
        N20.9, Urinary calculus
        M94.0, Chondrocostal junction syndrome [tietze]
        M51.36, Other intervertebral disc degeneration
        N13.30, Unspecified hydronephrosis
        """

        messages = [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"},
                    {'role': 'assistant', 'content': assistant_text_1},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"},
                    {'role': 'assistant', 'content': assistant_text_2},
                    {'role': 'user', 'content': f"{self.delimiter}{prompt}{self.delimiter}"}]

        response = get_completion(messages)
        return response

    def lab_results(self):
        system = """
        You are a medical assistant. Your job is to extract the labs and radiology results from the provided text. lets think step by step.
        First write the heading of **labs and radiology data:** in double astrikes. 
        Than Find the labs and radiology results with the reading if available from the provided text and write under the 
        heading of "labs and radiology data" in bullets.
        Return "nothing" if not text related to labs are radiology is available in the provided text.
        """

        prompt = f"""
        You are a medical assistant. Your job is to extract the labs and radiology results from the text delimited by triple backticks.
        '''{self.post_date}
        """

        user_text = """
        You are a medical assistant. Your job is to extract the labs and radiology results from the text delimited by triple backticks.
        
        """

        assistant_text_1 = """
        **labs and radiology data:**
        CBC, CMP and LFTs normal
        Chol 218
        Tri 253
        HDL 31
        LDL 136
        HbA1c 6.2
        Vitamin D-25-OH 15
        UA negative
        FOBT negative
        """

        assistant_text_2 = """
        nothing
        """

        messages = [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"},
                    {'role': 'assistant', 'content': assistant_text_1},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"},
                    {'role': 'assistant', 'content': assistant_text_2},
                    {'role': 'user', 'content': f"{self.delimiter}{prompt}{self.delimiter}"}]

        response = get_completion(messages)
        return response

    def template(self):
        template = """
        **Counselling Recommendations:**
        -Smoking cessation
        -Alcohol
        -Diet
        -Exercise
        -Weight loss
        -Medications compliance
        -Mammography
        -Pap-smear
        -Colonoscopy
        -Bone density
        -Podiatry follow up
        -Ophthalmology follow up
        **Follow up in one month or as needed.**        
    """
        return template

    def current_medication(self):
        prompt_0 = f"""
        You are expert in calculating dates. Your job is to return the medications that patient is taking at the visit date after comparing with the "start date", "End date", "QTY" and "Sig" from the text delimited by triple \
        backticks.
        Return "Nothing" if no medication is found.
        Use double asterisks for heading. **Current CNS Medications**.
        Return only Central nervous system therapeutic medications.
        """
        few_shot_user_2 = """
        Effexor XR 37.5 mg capsule,extended release, 1 tab PO daily , Qty: 30, Start Date: 04/21/2024, End Date: 05/21/2024, Prescribe Date: 04/21/2024
        alprazolam 0.5 mg tablet, 1 tab by mouth daily as needed for anxiety , Qty: 15, Start Date: 04/21/2024, End Date: 05/21/2024, Prescribe Date: 04/21/2024
        """
        few_shot_assistant_2 = """
        **Current CNS Medications:**

        No medications 
        """
        few_shot_user_1 = """

        Klonopin 1 mg tablet, 1 tab qHS , Qty: 30, Start Date: 05/23/2024, End Date: 06/22/2024, Prescribe Date: 05/23/2024
        duloxetine 60 mg capsule,delayed release, TAKE 1 CAPSULE BY MOUTH EVERY DAY daily, Qty: 30, Start Date: 04/24/2024, End Date: 05/24/2024, Prescribe Date: 04/24/2024
        promethazine-DM 6.25 mg-15 mg/5 mL oral syrup, 10mL by mouth every 8 hours prn cough , Qty: 300, Start Date: 01/05/2024, Prescribe Date: 01/05/2024,Reconciliation Date: 03/22/2024
        Zithromax Z-Pak 250 mg tablet, 1 dose pk by mouth as directed on dose pack; For 500 mg dose pack: take 500 mg once daily for 3 days , Qty: 6, Start Date: 01/05/2024, Prescribe Date: 01/05/2024,Reconciliation Date: 03/22/2024
        amoxicillin 875 mg tablet, take 1 tablet(875MG) by oral route bid, Qty: 10, Start Date: 12/07/2023, End Date: 12/12/2023, Prescribe Date: 12/07/2023,Reconciliation Date: 03/22/2024

        """

        few_shot_assistant_1 = """
        Current CNS medications:f

        - Klonopin 1 mg tablet
        - Duloxetine 60 mg capsule

        """

        messages = [{'role': 'system', 'content': prompt_0},
                    {'role': 'user', 'content': f"{few_shot_user_1}"},
                    {'role': 'assistant', 'content': f"{few_shot_assistant_1}"},
                    {'role': 'user', 'content': f"{few_shot_user_2}"},
                    {'role': 'assistant', 'content': f"{few_shot_assistant_2}"},
                    {'role': 'user', 'content': f"{self.post_date}"}

                    ]

        response_0 = get_completion(messages)
        return response_0

    def combined_plan_of_care(self):
        result0 = self.filter_diagnosis()
        result1 = self.lab_results()
        result2 = self.current_medication()
        result3 = self.template()
        result = f"{result0}\n{result1}\n{result2}\n{result3}"
        self.result = result


class review_of_system:
    def __init__(self, post_date, delimiter="####"):
        self.post_date = post_date
        self.delimiter = delimiter
        result = self.final()
        self.result = result

    def get_symptoms(self):
        user_text = f"""
                ```{self.post_date}```
                You are a medical assistant. Your job is to identify the symptoms from the provided text delimited by triple backticks\
                Next, extract and compile identified symptoms from the symptoms_list if available.\
                Don't suggest any symptoms if it is not mentioned in the symptoms_list. \
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

    def office_visit(self):

        template_lines = """
        **General Adult Exam Constitutional:**
            General Appearance: healthy-appearing, well-developed.
        **Psychiatric:**
            Insight: good judgement
            Mental Status: active and alert, normal mood, normal affect
            Orientation: to time, to place, to person
            Memory: recent memory normal, remote memory normal
        **Head:**
            Head: normocephalic, atraumatic
        **Eyes:**
            Lids and Conjunctivae: non-injected, no discharge, no pallor
            Pupils: PERRLA
            EOM: EOMI
            Sclerae: non-icteric
        **ENMT:**
            Ears: no lesions on external ear, EACs clear, TMs clear
            Nose: no lesions on external nose, nares patent, nasal passages clear, no sinus
            tenderness, no nasal discharge
        **Neck:**
            Neck: supple, trachea midline, no masses, FROM
            Lymph Nodes: no cervical LAD, no supraclavicular LAD, no axillary LAD, no inguinal LAD
            Thyroid: no enlargement, non-tender, no nodules
        **Lungs:**
            Respiratory effort: no dyspnea
            Auscultation: breath sounds normal, good air movement, CTA except as noted, no
            wheezing, no rales/crackles, no rhonchi
        **Cardiovascular:**
            Heart Auscultation: RRR, normal S1, normal S2, no murmurs, no rubs, no gallops
            Neck vessels: no carotid bruits
        **Abdomen:**
            Bowel Sounds: normal
            Inspection and Palpation: soft, non-distended, no tenderness, no guarding, no rebound
            tenderness, no masses, no CVA tenderness
            Liver: non-tender, no hepatomegaly
            Spleen: non-tender, no splenomegaly
            Hernia: none palpable
        **Musculoskeletal:**
            Motor Strength and Tone: normal, normal tone
            Joints, Bones, and Muscles: normal movement of all extremities, no contractures, no bony
            abnormalities, no malalignment, no tenderness
        **Extremities:**
            No edema
            Pulse palpable
            Motor 5/5
            Normal gait
        **Neurologic:**
            Cranial Nerves: grossly intact
            Reflexes: DTRs 2+ bilaterally throughout
        **Skin:**
            Inspection and palpation: no rash, no lesions, no abnormal nevi, no ulcer, no induration, no
            nodules, good turgor, no jaundice
            Nails: normal
        **Back:**
            Thoracolumbar Appearance: normal curvature        
        """

        system = """You are a medical assistant you have to update the physical exam template based on the Doctor 
        dictation that  I will provide. Ignor the dictation text if it is not related to physical exam of the patient. 
        Return the template with no changes if no symptoms are given in the provided text.
        Don't add extra text in the output.
        """

        few_shot_user_1 = """
        You are a medical assistant you have to update the physical exam template based on the Doctor 
        dictation that  I will provide.
        """
        few_shot_assistant_1 = """
        **General Adult Exam Constitutional:**
            General Appearance: healthy-appearing, well-developed.
        **Psychiatric:**
            Insight: good judgement
            Mental Status: active and alert, normal mood, normal affect
            Orientation: to time, to place, to person
            Memory: recent memory normal, remote memory normal
        **Head:**
            Head: normocephalic, atraumatic
        **Eyes:**
            Lids and Conjunctivae: non-injected, no discharge, no pallor
            Pupils: PERRLA
            EOM: EOMI
            Sclerae: non-icteric
        **ENMT:**
            Ears: no lesions on external ear, EACs clear, TMs clear
            Nose: no lesions on external nose, nares patent, nasal passages clear, no sinus
            tenderness, no nasal discharge
        **Neck:**
            Neck: supple, trachea midline, no masses, FROM
            Lymph Nodes: no cervical LAD, no supraclavicular LAD, no axillary LAD, no inguinal LAD
            Thyroid: no enlargement, non-tender, no nodules
        **Lungs:**
            Respiratory effort: no dyspnea
            Auscultation: breath sounds normal, good air movement, CTA except as noted, no
            wheezing, no rales/crackles, no rhonchi
            Physical exam reveals bronchitis and decreased breath sounds bilaterally
        **Cardiovascular:**
            Heart Auscultation: RRR, normal S1, normal S2, no murmurs, no rubs, no gallops
            Neck vessels: no carotid bruits
        **Abdomen:**
            Bowel Sounds: normal
            Inspection and Palpation: soft, non-distended, no tenderness, no guarding, no rebound
            tenderness, no masses, no CVA tenderness
            Liver: non-tender, no hepatomegaly
            Spleen: non-tender, no splenomegaly
            Hernia: none palpable
        **Musculoskeletal:**
            Motor Strength and Tone: normal, normal tone
            Joints, Bones, and Muscles: normal movement of all extremities, no contractures, no bony
            abnormalities, no malalignment, no tenderness
        **Extremities:**
            No edema
            Pulse palpable
            Motor 5/5
            Normal gait
        **Neurologic:**
            Cranial Nerves: grossly intact
            Reflexes: DTRs 2+ bilaterally throughout
        **Skin:**
            Inspection and palpation: no rash, no lesions, no abnormal nevi, no ulcer, no induration, no
            nodules, good turgor, no jaundice
            Nails: normal
        **Back:**
            Thoracolumbar Appearance: normal curvature     
        """

        few_shot_user_2 = """
        You are a medical assistant you have to update the physical exam template based on the Doctor 
        dictation that  I will provide.
        
        """
        few_shot_assistant_2 = """
        **General Adult Exam Constitutional:**
            General Appearance: healthy-appearing, well-developed.
        **Psychiatric:**
            Insight: good judgement
            Mental Status: active and alert, normal mood, normal affect
            Orientation: to time, to place, to person
            Memory: recent memory normal, remote memory normal
        **Head:**
            Head: normocephalic, atraumatic
        **Eyes:**
            Lids and Conjunctivae: non-injected, no discharge, no pallor
            Pupils: PERRLA
            EOM: EOMI
            Sclerae: non-icteric
        **ENMT:**
            Ears: no lesions on external ear, EACs clear, TMs clear
            Nose: no lesions on external nose, nares patent, nasal passages clear, no sinus
            tenderness, no nasal discharge
        **Neck:**
            Neck: supple, trachea midline, no masses, FROM
            Lymph Nodes: no cervical LAD, no supraclavicular LAD, no axillary LAD, no inguinal LAD
            Thyroid: no enlargement, non-tender, no nodules
        **Lungs:**
            Respiratory effort: no dyspnea
            Auscultation: breath sounds normal, good air movement, CTA except as noted, no
            wheezing, no rales/crackles, no rhonchi
        **Cardiovascular:**
            Heart Auscultation: RRR, normal S1, normal S2, no murmurs, no rubs, no gallops
            Neck vessels: no carotid bruits
        **Abdomen:**
            Bowel Sounds: normal
            Inspection and Palpation: soft, non-distended, no tenderness, no guarding, no rebound
            tenderness, no masses, no CVA tenderness
            Liver: non-tender, no hepatomegaly
            Spleen: non-tender, no splenomegaly
            Hernia: none palpable
        **Musculoskeletal:**
            Motor Strength and Tone: normal, normal tone
            Joints, Bones, and Muscles: normal movement of all extremities, no contractures, no bony
            abnormalities, no malalignment, no tenderness
        **Extremities:**
            No edema
            Pulse palpable
            Motor 5/5
            Normal gait
        **Neurologic:**
            Cranial Nerves: grossly intact
            Reflexes: DTRs 2+ bilaterally throughout
        **Skin:**
            Inspection and palpation: no rash, no lesions, no abnormal nevi, no ulcer, no induration, no
            nodules, good turgor, no jaundice
            Nails: normal
        **Back:**
            Thoracolumbar Appearance: normal curvature        
        """

        prompt = f"""
        You are a medical assistant. Your job is to rewrite the template lines
         {template_lines} 
         based on the doctor dictation delimited by triple backticks.
         '''{self.post_data}'''
        Use double asterisks for the heading and the added line.
        Make sure all the provided text is added in the output.
        
        """
        messages = [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_2}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_2},
                    {'role': 'user', 'content': f"{self.delimiter}{prompt}{self.delimiter}"}]

        response = get_completion(messages)

        return response

    def final(self):
        if "Type of visit: Follow Up" in self.post_data:
            response_1 = "Patient is AAO x 3. Not in acute distress. Breathing is non-labored, Normal respiratory effort. The affect is normal and appropriate."
        elif "Type of visit: Office Visit" in self.post_data:
            response_1 = self.office_visit()
        else:
            response_1 = "Currently I can only provide physical exam for Type of visit: Follow Up"
        return response_1

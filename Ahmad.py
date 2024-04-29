import openai
from extra_functions import get_completion, clear_lines_above_and_containing, get_cpt_code
from hpi import get_templates


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
            response_1 = "Patient is AAO x 3. Not in acute distress. Breathing is non-labored, Normal respiratory effort. The affect is normal and appropriate."
        else:
            response_1 = "Currently I can only provide physical exam for Type of visit: Follow Up"
        return response_1


class plan_of_care:
    def __init__(self, post_date, delimiter="####"):
        self.post_data = post_date
        self.delimiter = delimiter
        result = self.final()
        self.result = result

    def final(self):
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
               The disease or disorders, medications and doctor dictations are delimited by triple backticks.
               '''{self.post_data}'''

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

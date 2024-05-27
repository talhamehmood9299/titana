import openai
from extra_functions import extract_text, get_completion, get_dictation, get_cpt_code
from labs_radiology import get_lab_results
from Template import get_templates


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
        self.post_data = post_date
        self.delimiter = delimiter
        result = self.final()  # Call the final() method and store the result
        self.result = result  # Store the result as an attribute

    def final(self):
        system_2 = f"""
        You are a medical assistant and you job is to write a history of illness of the patient.
        The text contains the patient demographics and Doctor dictation.
        Please write a History of illness based on the text delimited by the triple backticks.lets think step by step.
        First line contains the patient demographics. Don't add the medications in this line.
        Second line contains the patient current complains.
        It is necessary to concluded with "**No other medical concerns in today's appointment**".
        Don't add the headings.
        Ensure that all information is included in the response.
        Don't repeat the lines.
        Use double astrikes for all the patient name and medication.
        Write lines separately.
        """
        prompt_2 = f"""
        Please write a History of illness in based on the text delimited by the triple backticks,\
        ```{self.post_data}```
        and concluded with "No other medical concerns in today's appointment".
        """
        few_shot_1 = """Smith, Dolores, 76 F. pt flwng pain mngnm, nt,, severe lbp, pain mngmnt not much help, anxious restless, \
         not sleepmng, flwng rglrly pain mmngmnt. dfclty sleepng at ni8. 140/85 after repeat bp n taking clonodine."""
        result_1 = """\
        Dolores Smith, a 76-year-old female, presented for an office visit. \n \
        She has been following pain management for severe low back pain, but it hasn't been much help. \n \
        She is anxious, restless, and has difficulty sleeping at night. \n \
        Her blood pressure after repeat and taking clonidine was 140/85. \n \
        **No other medical concerns in today's appointment.**\n \
        """
        few_shot_2 = """Write a history of illness of the patient based on the text that I will provide"""
        result_2 = """\
        Godoy Sergio, a 39-year-old male, presented for a follow-up visit. \n \
        The patient has a history of HTN, and he is taking his BP readings as an outpatient, his recent BP reading was 120/76, his heart rate was 68, and his current weight is 203 pounds. \n \
        He reports his sugar levels are better.\n \
        He is also following for DM, Atherosclerosis heart disease, and Hyperlipidemia.\n \
        **No other medical concerns in today's appointment**.\n 
        """

        messages_2 = [{'role': 'system', 'content': system_2},
                      {'role': 'user', 'content': f"{self.delimiter}{few_shot_1}{self.delimiter}"},
                      {'role': 'assistant', 'content': result_1},
                      {'role': 'user', 'content': f"{self.delimiter}{prompt_2}{self.delimiter}"},
                      {'role': 'system', 'content': system_2},
                      {'role': 'user', 'content': f"{self.delimiter}{few_shot_2}{self.delimiter}"},
                      {'role': 'assistant', 'content': result_2},
                      {'role': 'user', 'content': f"{self.delimiter}{prompt_2}{self.delimiter}"}]

        response = get_completion(messages_2)
        return response


class plan_of_care:

    def __init__(self, post_date, delimiter="####"):
        self.post_data = post_date
        self.delimiter = delimiter
        result = self.final()
        self.result = result

    def final(self):
        template = get_templates(self.post_data)
        system = f""" you are a medical assistant your job is to write the Plan of Care based on the provided text. lets think step by step.\
        1) First write the name of the disease or disorder mentioned in the text as a heading.
        2) Under the heading in second line write the related medication of disease and disorder if mentioned in the provided text. Don't write the start date, \
         prescribed date and end date of the medication.
        3) Do not write any heading of medication.
        4) Then write the other mentioned text in the form of bullets.
        5) Write the labs and radiology text under the 'Health Maintenance' heading if available.
        6) Do not write any extra text and headings.
        7) Ignore the pharmacy related text.
        8) Do not repeat the text.
        9) Use double asteriks for all the headings.
        10) It is mandatory to conclude with "Follow-up as scheduled".
        11) At the end, check if there is a heading of medication in the final response then remove this heading and add the medication in the second line.
         """
        prompt = f"""
        You are a medical assistant your job is to write the plan of care based on this text. Lets think step by step.
        First write the name of the disease or disorder.
        Than write the name of the medication and text that is related to that specific disease or disorder:
        {self.post_data}\n
        Than write these template lines of that specific disease or disorder.
        {template}
        Don't write the additional text.
       """

        delimiter = "###"
        few_shot_user_1 = """
            has c/op lbp since fall,hasnt start pt yet, hand hrts,hstry of strpoke ,askng in pt rehab, contacted she has to saty in hsptl 3 nui8s then 
            will take her, enc to out pt ,trmdl refill,will strt from mon pot. htn-comp wd meds,flwng low salt cardia. cp wd recent fall n lbp leg pain-left pt,
            cnt trmdl. hld-on statin. hm. labs rev 03/01. f/u 4 weeks
           """
        few_shot_assistant_1 = """
           **HTN:**
            - lisinopril 15mg 1 tablet by mouth once daily.
            - She is following a low-salt and cardiac diet
           **Chronic pain:**
            - Tramadol 50mg tablet is refilled
            - It is advised to exercise to Loosen Muscles and get Better Sleep.
            - She will start physical therapy sessions on Monday next week
           **HLD:**
            - She is taking Lipitor 40mg medicine regularly
            - It is advised to eat a diet low in saturated and trans fats. Regularly include fruits, vegetables, beans, nuts, whole grains, and fish.

           **Follow-up as scheduled**.

           """
        few_shot_user_2 = """
            valsartan,metformin, clopidogrel, sal, glimepiride,aspirin, metoprolol. insulin inactive. bw cont A1c. 
            Crustina office. mylanta 2 times a day. f/u friday on call. 
            meal in rest 2 days ago, dvlp nausea diarhea abdmnl dscmfrt,losing apoetite, no fever. p/e mild tndrness epigastrc area. Labs ordrd.
           """
        few_shot_assistant_2 = """
           **HTN:**
            - Metoprolol 50mg tablet is refilled.
            - Valsartan 160mg tablet is refilled.
            - It is advised to eat a Healthy Low-salt Diet.
           **DM:**
            - Glimepiride 4mg tablet is refilled.
            - Metformin 1000mg tablet is refilled.
            - Steglatro 15mg tablet is refilled.
            - Following a consistent low-calorie, low-cholesterol diet, and avoiding concentrated sweets is advised.
           **Heart Disease:**
            - Clopidogrel 75mg tablet is refilled.
            - Aspirin 81mg tablet is refilled.
            - It is advised to follow a cardiac diet.
           Health Maintenance:**
            - A blood work script is sent to LabCorp.
            - Labs ordered.
            - A follow up appointment is scheduled.

           **Follow-up as scheduled**.

           """

        messages = [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_2}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_2},
                    {'role': 'user', 'content': f"{self.delimiter}{prompt}{self.delimiter}"}]

        response = get_completion(messages)

        return response


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
            response_1 = ("Limited physical exam. Not in acute distress. Breathing is non-labored, Normal respiratory "
                          "effort. The effect is normal and appropriate.")
        else:
            response_1 = "Currently I can only provide physical exam for Type of visit: Fllow Up"
        return response_1

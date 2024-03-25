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

    def final(self):
        if "Type of visit: Lab/Radiology Review" in self.post_data:
            response = self.template_2()
        else:
            response = self.template_5()

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




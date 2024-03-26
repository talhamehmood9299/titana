import openai
from extra_functions import extract_text, get_completion, get_dictation
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
                            Dolores Smith, a 76-year-old female, came in for an office visit. \n \
                            She has been following pain management for severe low back pain, but it hasn't been much help. \n \
                            She is anxious, restless, and has difficulty sleeping at night. \n \
                            Her blood pressure after repeat and taking clonidine was 140/85. \n \
                            **No other medical concerns in today's appointment.**\n \
                            """
        few_shot_2 = """Write a history of illness of the patient based on the text that I will provide"""
        result_2 = """\
                            Godoy Sergio, a 39-year-old male, came in for a follow-up visit. \n \
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
        medication_start = post_date.find("cutformhere:") + len("cutformhere:")
        medication_end = post_date.find("Doctor dictation")
        self.medications_text = post_date[medication_start:medication_end].strip()
        dictation_start = post_date.find("Doctor dictation:") + len("Doctor dictation:")
        doctor_semi = post_date[dictation_start:].strip()
        self.diagnosis = extract_text(doctor_semi)
        self.dictation_final = get_dictation(doctor_semi)
        result = self.final()
        self.result = result

    def final(self):
        template = get_templates(self.post_data)
        system = f""" you are a medical assistant your job is to write the Plan of Care based on the provided text. lets think step by step.\
        1) First write the name of the disease or disorder mentioned in the text as a heading.
        2) In the next line write the related medication if mentioned in the provided text. Don't add the heading of medication.
        3) Then write the other mentioned text in the form of bullets.
        4) Do not write any extra text.
        5) Use double asteriks for the headings.
        6) It is mandatory to conclude with "Follow-up as scheduled". """
        prompt = f"""
        You are a medical assistant your job is to write the plan of care based on this text.
        {template}
        {self.post_data}
       """

        delimiter = "###"
        few_shot_user_1 = """
            has c/op lbp since fall,hasnt start pt yet, hand hrts,hstry of strpoke ,askng in pt rehab, contacted she has to saty in hsptl 3 nui8s then 
            will take her, enc to out pt ,trmdl refill,will strt from mon pot. htn-comp wd meds,flwng low salt cardia. cp wd recent fall n lbp leg pain-left pt,
            cnt trmdl. hld-on statin. hm. labs rev 03/01. f/u 4 weeks
           """
        few_shot_assistant_1 = """
           HTN:
            lisinopril 15mg 1 tablet by mouth once daily.
            She is following a low-salt and cardiac diet
           Chronic pain with a recent fall, left leg pain, and back pain:
            Tramadol 50mg tablet is refilled
            It is advised to exercise to Loosen Muscles and get Better Sleep.
            She will start physical therapy sessions on Monday next week
           HLD:
            She is taking Lipitor 40mg medicine regularly
            It is advised to eat a diet low in saturated and trans fats. Regularly include fruits, vegetables, beans, nuts, whole grains, and fish.
           **Follow-up as scheduled**.

           """

        messages = [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': f"{delimiter}{few_shot_user_1}{delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{delimiter}{prompt}{delimiter}"}]

        response = get_completion(messages)

        return response


from openai import OpenAI
from extra_functions import extract_text, get_completion, get_dictation, get_cpt_code
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
        # print(response)
        # for local testing only uncomment the below line of code
        #response = response.content

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
        Next line contains the patient current complains with prescribe medication if available.
        Write the follow up information of disease or disorder in a line separately with only related medications.
        It is necessary to concluded with "**No other medical concerns in today's appointment**".
        Don't add the headings.
        Don't repeat the medical history.
        Don't repeat the same information.
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
        basic_data = self.get_basic_information()

        history = self.get_history()

        template = get_templates(basic_data)

        # print(template)

        general = self.combine_the_text(basic_data, history, template)
        return general


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

    def template_4(self):
        prompt = """
           you are a medical assistant. Your job is to write a plan of care by following the mentioned rules. let's think step by step.
               1) First extract the only one associate disease or disorder for each medication if mentioned in the provided text.
               5) If medications are given in the provided text then Write the name of the disease or disorder as the heading and then write some lines of Plan of Care in the form of paragraph also include the provided medicaiton in the paragraph.
               6) Write the short form of disease or disorders
               8) Don't add ICD-10 codes.
               9) Don't add Start Date, Prescribe Date, End Date and Qty of the medication.
               10) If the disease and disorder is not related with the provided medication, then don't add the disease or disorder in the \
               output.
               11) If medication is not given in the provided text with disease or disorder then it is also necessary to include a concise general plan of care for this disease or disorder by yourself comprising 4 to 5 lines.
               12) Utilize double asterisks for all headings.
               13) Utilize double asterisks for all "medications".
               14) Don't suggest any disease, disorder or symptoms for any medication. 
               15) Don't add heading of "Plan of care, Disease or disorder and "Medication".
               16) Don't add the disease or disorder in the output if no medication is mentioned in the provided text.
               17) It is Mandatory to add these below lines in the end of plan of care in every response:
               "**Compliance** with medications has been stressed.
               Continue other medications.
               Side effects, risks, and complications were clearly explained and the patient verbalized understanding and was given the opportunity to ask questions.
               Relaxation techniques were discussed, stress avoidance was reviewed, and medication and yoga were encouraged."
               18) It is Mandatory to conclude the plan of care with this line "Follow-up appointment as scheduled."

           """

        user_text = f"""
              Write a concise plan of care with 4 to 5 lines for each disease or disorder if the related medication and the doctor dictation is linked with it.
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
           **Hyperlipidemia**: The patient presents with complaints of elevated lipid levels, indicative of hyperlipidemia. The patient is requesting Atorvastatin 20mg tablet. Dietary instruction about hyperlipidemia given to the patient. Eat a diet low in saturated and trans fats. Include lots of fruits, vegetables, beans, nuts, whole grains, and fish regularly into your diet. Stop eating red meat and processed meats like bacon, sausage, and cold cuts. Drink skim or low-fat milk.
           **GERD**: The patient experiences a burning sensation in the chest. The patient is requesting H2 Receptor Antagonists 150mg tablet Recommended to eat slowly, chew well every bite for at least 20-25 times before swallowing. Do not talk, read or watch TV while eating. Eat small portions, frequently, at least every 3-h. No large meals. Avoid Tobacco, alcohol, greasy, acidic, or spicy food, coffee, and carbonated beverages. Sip plain water between bites. Avoid eating within 2 hours before bedtime. Walk after the meal.
           Compliance with medications has been stressed. Continue other medications. Side effects, risks, and complications were clearly explained and the patient verbalized understanding and was given the opportunity to ask questions. Relaxation techniques were discussed, stress avoidance was reviewed, medication and yoga were encouraged.

           **Follow-up appointment as scheduled.**.

           """
        few_shot_assistant_2 = """
           **Compliance** with medications has been stressed.
           Continue other medications.
           Side effects, risks, and complications were clearly explained and the patient verbalized understanding and was given the opportunity to ask questions.
           Relaxation techniques were discussed, stress avoidance was reviewed, and medication and yoga were encouraged."
           **Follow-up appointment as scheduled**.
           """

        messages = [{'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_1}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_1},
                    {'role': 'user', 'content': f"{self.delimiter}{few_shot_user_2}{self.delimiter}"},
                    {'role': 'assistant', 'content': few_shot_assistant_2},
                    {'role': 'user', 'content': f"{self.delimiter}{user_text}{self.delimiter}"}]

        response = get_completion(messages)

        return response

    def final(self):
        response = self.template_4()
        return response

import openai
from extra_functions import extract_text, get_completion, get_dictation
from labs_radiology import get_lab_results

def task(task_string, post_date):
    if "Task 1:" == task_string:
        instance = histroy_of_illness(post_date)
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
                            Don't write more than 4 lines.
                            Write lines separately.
                        """
        prompt_2 = f"""
                                    Please write a History of illness based on the text delimited by the triple backticks,\
                                    ```{self.post_data}```
                                    and concluded with "No other medical concerns in today's appointment".
                                    """
        few_shot_1 = """Write a history of illness of the patient based on the text that I will provide"""
        result_1 = """\
                            Calvin Mcrae, a 71-year-old male, came in for a follow-up visit. \n \
                            He has a medical history of Hypertension (HTN), Hypothyroidism, and a history of cellulitis of the face.\n \
                            He complains of the upper lip infection.\n \
                            **No other medical concerns in today's appointment**.\n \
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




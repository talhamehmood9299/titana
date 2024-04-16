from labs_radiology import get_lab_results
from extra_functions import extract_text, get_completion, get_dictation

def task(post_data):
    if "Task 1:" in post_data:
        instance = history_of_illness(post_data)
        response = instance.result
    elif "Task 2:" in post_data:
        instance = plan_of_care(post_data)
        response = instance.result
    else:
        response = "Task is not justified"
    return response

class history_of_illness():
    def __init__(self, post_date):
        self.post_data = post_date
        result = self.hoi()
        self.result = result
        result1 = self.ros()  # Call the final() method and store the result
        self.result1 = result1  # Store the result as an attribute
        result2 = self.obj()
        self.result2 = result2

    def ros(self):
        ros = """
            Anxiety: Managed,
            Depression: Maneged,
            Mania: Denies symptoms,
            OCD: Denies symptoms,
            Trauma: No History of Trauma,
            Psychosis: Denies symptoms, no symptoms endorsed during interaction,
            Disordered Eating: Denies symptoms,
            ADHD: Not Diagnosed,
            ODD/Conduct/Antisocial: No symptoms evident,
            Personality Disorder Traits: No symptoms evident,
            Sleep: Denies Sleeping difficulty or disturbances
        """

        system = f"""You work as a medical assistant and are tasked with updating a text delimited by triple backticks.
        ```{str(ros)}```
        The list includes medical conditions and their associated symptoms. Your job is to replace any status of symptoms in the list 
        with new ones if related symptoms are mentioned in the provided text. If no related symptoms are mentioned, 
        do not make any changes to the list.
        Write only 2 words of status of symptoms.
        Add the heading of "**Psychiatric ROS** in double astrikes in the output "
        Use double astrikes for all the conditions.
        Don't add the backticks in the output.

        """

        doctor_dictations = ("Your job is to replace any symptoms in the list with new ones if related symptoms are "
                             "mentioned in the provided text")

        few_shot_user_text = " He reports Anxiety attacks due to sleep difficulties and forgetfulness."

        few_shot_assistant_text = ("""
        **Psychiatric ROS**

          **Anxiety**: Reports Anxiety attacks,
          **Depression**: Managed,
          **Mania**: Denies symptoms,
          **OCD**: Denies symptoms,
          **Trauma**: No History of Trauma,
          **Psychosis**: Denies symptoms, no symptoms endorsed during interaction,
          **Disordered Eating**: Denies symptoms,
          **ADHD**: Reports forgetfulness,
          **ODD/Conduct/Antisocial**: No symptoms evident,
          **Personality Disorder Traits**: No symptoms evident,
          **Sleep**: Reports Sleep difficulties
          """)

        messages = [
            {"role": "system", "content": f"{system}"},
            {"role": "user", "content": f"{doctor_dictations}"},
            {"role": "assistant", "content": f"{few_shot_assistant_text}"},
            {"role": "user", "content": f"{post_data}"}]

        result = get_completion(messages)
        print(result.content)
        return result.content

    def hoi(self):
        introduction_line = ("I introduced myself as her Healthcare Provider and the Medical Assistant will be doing "
                             "Medical Documentation accompanying me.")

        system_2 = f"""
            You are a medical assistant. Your job is to write a history of illness based on the text that i will provide.
            The first line contains the patient demographics and than write this sentence without any changes"{introduction_line}".
            The second lines contains the text that patient reports in doctor dictations. 
            The third line must contain this sentence "Denied SI/HI, panic attacks, or AVH. No report of difficulty sleeping or loss of appetite."
            Than write the heading of "Current CNS medications" and write all the mentioned medications with the short sig under this 
            heading in the form of bullets. Use double astrikes for this heading.
            Use double astrikes for patient name.
            Don't add the End date, prescribe date, start date, quantity.
            Don't add the previous responses.
            """

        user_text = "Your job is to write a history of illness based on the text that i will provide."

        assistant_text = """**Diane Kuriloff** is a 67-year-old female patient who has a history of Anxiety. I introduced 
            myself as her Healthcare Provider and the Medical Assistant will be doing Medical Documentation accompanying me.
            She was prescribed Xanax 0.5 Daily PRN Anxiety 10 tabs per month. She reports that medication is working well 
            with the medication.
            Denied SI/HI, panic attacks, or AVH. No report of difficulty sleeping or loss of appetite. 

            **Current CNS medications**:
             - Xanax 0.5 Daily PRN Anxiety
            """

        prompt = f"""
            You are a medical assistant. Your job is to write a history of illness based on the text delimited by triple backticks.
            ```{post_data}```
            """

        messages = [
            {"role": "system", "content": f"{system_2}"},
            {"role": "user", "content": f"{user_text}"},
            {"role": "assistant", "content": f"{assistant_text}"},
            {"role": "user", "content": f"{prompt}"}
        ]

        result = get_completion(messages)
        print(result.content)
        return result.content

    def obj(self):
        objective = """
        **OBJECTIVE**

        - **Behavior**: Appropriate
        - **Concentration**: Intact
        - **Speech**: Normal with normal rate
        - **Mood**: Appropriate
        - **Obsession**: No
        - **Compulsion**: No
        - **Memory**: Normal
        - **Attention**: Focused
        - **Thought Process**: Coherent
        - **Thought Content**: Normal
        - **Cognition/Judgement**: Good
        - **Safety**: Denies SI/HI
        """
        print(objective)
        return objective


class plan_of_care():
    def __init__(self, post_date):
        self.post_data = post_date
        result = self.final()
        self.result = result

    def final(self):
        education = """
            **Education:**

                - Relaxation techniques discussed. Stressors and coping strategies reviewed. Yoga, deep breathing, journaling were 
                encouraged. UDS will be conducted periodically to monitor therapeutic activity, compliance including 
                potential misuse, unauthorized drug use, or diversion.
                - Common side effects of medication were discussed as well as risks, benefits, and alternatives of medications
                including risk of serotonin syndrome with the medications and advised to the procedures to follow if this were to 
                occur
                - The patient has been educated on the risks, benefits, and alternatives of the controlled substances, including but 
                not limited to nausea, vomiting, constipation, sedation, dizziness, addiction, dependency, and tolerance to 
                long-term medication usage.
                - The patient was educated not to drive or operate heavy machinery while on this medication, especially during the 
                initiation and titration of the medication. Emphasis was placed on tolerance, abuse, and dependence.
                - The patient was educated on the proper storage and safekeeping of controlled medications. The patient was educated 
                on the risk of combining opioids with alcohol, sedatives, and illicit substances.
                **"Limit alcohol, caffeine, and sugar consumption"**
            """

        system_3 = f"""
            You are a medical assistant. Your job is to write a plan of care based on the text that i will provide.
            At first write this line in double astrikes "**NJ PMP Aware checked**".
            After that write the heading of medications in double astrikes and under this heading all the mentioned medications.\
            in bullets with their sig and text.
            Don't add the End date, prescribe date, start date, quantity.
            Than add text delimited by triple backticks.
            ```{education}```
            At the end write about the followup visit in double astrikes.
            Don't add the previous responses.
            Don't add the heading of plan of care.
            Don't add the triple backticks in the output.
            """
        prompt = f"""
            You are a medical assistant. Your job is to write the plan of care based on the text delimited by triple backticks.
            ```{post_data}```
            """

        few_shot_user = "You are a medical assistant. Your job is to write a plan of care based on the text"

        few_shot_assistant = """
            **NJ PMP Aware checked**
            **Medications:**

            - Prozac increased to 40 mg OD
            - Klonopin continued(pt has supply, will be due on 04/28/2024)
            - Trazodone continued at the same dose.

            **Education:**

            - Relaxation techniques discussed. Stressors and coping strategies reviewed. Yoga, deep breathing, journaling were 
            encouraged. UDS will be conducted periodically to monitor therapeutic activity, compliance including 
            potential misuse, unauthorized drug use, or diversion.
            - Common side effects of medication were discussed as well as risks, benefits, and alternatives of medications
            including risk of serotonin syndrome with the medications and advised to the procedures to follow if this were to 
            occur
            - The patient has been educated on the risks, benefits, and alternatives of the controlled substances, including but 
            not limited to nausea, vomiting, constipation, sedation, dizziness, addiction, dependency, and tolerance to 
            long-term medication usage.
            - The patient was educated not to drive or operate heavy machinery while on this medication, especially during the 
            initiation and titration of the medication. Emphasis was placed on tolerance, abuse, and dependence.
            - The patient was educated on the proper storage and safekeeping of controlled medications. The patient was educated 
            on the risk of combining opioids with alcohol, sedatives, and illicit substances.
            **"Limit alcohol, caffeine, and sugar consumption"**


            **Follow-up: One Month**
            """
        messages = [
            {"role": "system", "content": f"{system_3}"},
            {"role": "user", "content": f"{few_shot_user}"},
            {"role": "assistant", "content": f"{few_shot_assistant}"},
            {"role": "user", "content": f"{prompt}"}
        ]

        result = get_completion(messages)
        print(result.content)
        return result.content

from labs_radiology import get_lab_results
from extra_functions import extract_text, get_completion, get_dictation

def task(task_string, post_date):
    if "Task 1:" == task_string:
        instance = history_of_illness(post_date)
        response = instance.result
    elif "Task 2:" == task_string:
        instance = plan_of_care(post_date)
        response = instance.result
    else:
        response = "Task is not justified"
    return response

class history_of_illness():
    def __init__(self, post_date):
        self.post_data = post_date
        result0 = self.hoi()
        result1 = self.ros()
        result2 = self.obj()
        result = f"{result0}\n{result1}\n{result2}"
        self.result = result

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
            Sleep: Denies Sleeping difficulty, Reports sleeping issues
        """

        system = f"""You work as a medical assistant and are tasked with updating a text delimited by triple backticks.
        ```{str(ros)}```
        The list includes medical conditions and their associated symptoms. Your job is to replace any symptoms in the list 
        with new ones if related symptoms are mentioned in the provided text. Replace the symptoms by choosing new ones from these provided options only,
		``` Anxiety: Denies symptoms, Managed
		   Depression: Denies symptoms, Managed
		   Mania: Denies symptoms
		   OCD: Denies symptoms 
		   Trauma: No History of Trauma, history of trauma, childhood trauma, sexual abuse, physical abuse
		   Psychosis: Denies symptoms, no symptoms endorsed during interaction 
		   Disordered Eating: Denies symptoms
		   ADHD: Not Diagnosed, Able to focus with medication
		   ODD/Conduct/Antisocial: No symptoms evident, 
		   Personality Disorder Traits: No symptoms evident 
		   Sleep: Denies Sleeping difficulty, Reports sleeping issues ```
		   
		choose the one option by following these rules:
		1) Read the text carefully if the provided symptoms text's meaning is semantically positive then choose the positive option from the above list
		2) Read the text carefully if the provided symptoms text's meaning is semantically negative then choose the negative option from the above list
		
		If no related symptoms are mentioned,
        do not make any changes to the list
        Write only 2 words of status of symptoms
        Add the heading of "**Psychiatric ROS** in double asteriks in the output"
        Use double asteriks for all the conditions
        Don't add the backticks in the output.

        """


        few_shot_user1_text = "Patient seen for follow-up reports current meds are effective in managing symptoms of anxiety and ADHD, reports mood as good, denies any issues with depression, sleep or appetite, refilled medications at current doses at verified pharmacy on file, follow-up in one month."

        few_shot_assistant1_text = ("""
        **Psychiatric ROS**

          **Anxiety**: Managed,
          **Depression**: Managed,
          **Mania**: Denies symptoms,
          **OCD**: Denies symptoms,
          **Trauma**: No History of Trauma,
          **Psychosis**: Denies symptoms,
          **Disordered Eating**: Denies symptoms,
          **ADHD**: Not Diagnosed,
          **ODD/Conduct/Antisocial**: No symptoms evident,
          **Personality Disorder Traits**: No symptoms evident,
          **Sleep**: Denies Sleeping difficulty
          """)

        few_shot_user2_text = "Patient seen for follow-up reports anxiety levels not good at all, Reports that he's had multiple panic attacks over the last 15 days. Reports poor sleep. Reports decreased functioning. Reports some depressive symptoms. Discussed current medications. Reports that he feels that Zoloft is not doing anything for anxiety. Reports higher dose of Zoloft made anxiety worse."

        few_shot_assistant2_text = ("""
                **Psychiatric ROS**

                  **Anxiety**: Managed,
                  **Depression**: Managed,
                  **Mania**: Denies symptoms,
                  **OCD**:  Deniessymptoms,
                  **Trauma**: No History of Trauma,
                  **Psychosis**: Denies symptoms,
                  **Disordered Eating**: Denies symptoms,
                  **ADHD**: Not Diagnosed,
                  **ODD/Conduct/Antisocial**: No symptoms evident,
                  **Personality Disorder Traits**: No symptoms evident,
                  **Sleep**: Reports sleeping issues
                  """)

        messages = [
            {"role": "system", "content": f"{system}"},
            {"role": "user", "content": f"{few_shot_user1_text}"},
            {"role": "assistant", "content": f"{few_shot_assistant1_text}"},
            {"role": "user", "content": f"{few_shot_user2_text}"},
            {"role": "assistant", "content": f"{few_shot_assistant2_text}"},
            {"role": "user", "content": f"{self.post_data}"}]

        result = get_completion(messages)
        return result

    def hoi(self):
        introduction_line = ("I introduced myself as her Healthcare Provider and the Medical Assistant will be doing "
                             "Medical Documentation accompanying me.")

        system_2 = f"""
            You are a medical assistant. Your job is to write a history of illness based on the text that i will provide.
            The first line contains the patient demographics and than write this sentence without any changes"{introduction_line}".
            The second lines contains the text that patient reports in doctor dictations. 
            The third line must contain this sentence "Denied SI/HI, panic attacks, or AVH. No report of difficulty sleeping or loss of appetite."
            Than write the heading of "Current CNS medications" and write all the mentioned medications with the short sig under this 
            heading just write daily, bid, tid etc do not write complete sig. Write this in the form of bullets. Use double asteriks for this heading.
            Use double asteriks for patient name.
            Don't add the End date, prescribe date, start date, quantity.
            Don't add the previous responses.
            """

        user_text1 = "Your job is to write a history of illness based on the text that i will provide."

        assistant_text1 = """**Diane Kuriloff** is a 67-year-old female patient who has a history of Anxiety. I introduced 
            myself as her Healthcare Provider and the Medical Assistant will be doing Medical Documentation accompanying me.
            She was prescribed Xanax 0.5 Daily PRN Anxiety 10 tabs per month. She reports that medication is working well 
            with the medication.
            Denied SI/HI, panic attacks, or AVH. No report of difficulty sleeping or loss of appetite. 

            **Current CNS medications**:
             - Xanax 0.5 Daily PRN Anxiety
            """
        user_text2 = "Your job is to write a history of illness based on the text that i will provide."

        assistant_text2 = """**Diane Kuriloff** is a 67-year-old female patient who has a history of ADHD. I introduced 
                    myself as her Healthcare Provider and the Medical Assistant will be doing Medical Documentation accompanying me.
                    She was prescribed dextroamphetamine-amphetamine 20 mg tablet, Sig: TAKE 1 TABLET BY MOUTH TWICE A DAY bid. She reports that medication is working well 
                    with the medication. 

                    **Current CNS medications**:
                     - dextroamphetamine-amphetamine 20 mg tablet BID
                    """

        prompt = f"""
            You are a medical assistant. Your job is to write a history of illness based on the text delimited by triple backticks.
            ```{self.post_data}```
            """

        messages = [
            {"role": "system", "content": f"{system_2}"},
            {"role": "user", "content": f"{user_text1}"},
            {"role": "assistant", "content": f"{assistant_text1}"},
            {"role": "user", "content": f"{user_text2}"},
            {"role": "assistant", "content": f"{assistant_text2}"},
            {"role": "user", "content": f"{prompt}"}
        ]

        result = get_completion(messages)
        return result

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
            After that write the heading of medications in double astrikes and under this heading write all the mentioned medications with only the short sig under this 
            heading just write Daily, BID, TID OD etc do not write complete sig..\
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
            ```{self.post_data}```
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
        final_response = result
        return final_response

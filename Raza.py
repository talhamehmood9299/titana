import openai
from extra_functions import extract_text, get_completion, get_dictation
from labs_radiology import get_lab_results


def task(task_string, post_date):

    if "Task 2:" == task_string:
        instance = plan_of_care(post_date)
        response = instance.result
    else:
        response = "Task is not justified"
    return response



class plan_of_care:
    def __init__(self, post_date, delimiter="####"):
        self.post_date = post_date 
        self.delimiter = delimiter
        result = self.final()
        self.result = result

    def template_3(self):
        text = self.post_date 

        messages = [
            {"role": "system", "content": f"""
            Your job is to write a plan of care for the patient based on the patient_doctor conversation that \
              I will provide.Let's think step by step.
              The text also contains the disease or disorders and medications name.
              Make sure all the mentioned medications should be written under the heading of related disease or disorder. Don't \
              suggest the brand name.
              Don't write the separate heading of "Medications", "Referral" and "FollowUp" at the end.
              Don't add the additional headings.
              Don't add the start date and end of medications.
              Make sure all the conversation is added in the output.
              Make sure all the related information is written under one Heading.
              Write the test related text under one heading that is blood work. If the related information is already \
              written in the heading of disease or disorder than don't write it in the heading of blood work.
              Don't repeat the things.
              Utilize double asterisks for all headings.
              Utilize double asterisks for all medications in the output text.
              At the end make sure that the output doesn't contain separate heading of medication. If separate heading of \
              medication is present than it is mandatory to adjust it in the heading of most related disease or disorder, and 
              remove the heading. 
              Write the pharmacy related text also in heading of disease or disorder.
              Don't write the "start Date", "End Date" and the line "The prescription was successfully delivered to the /
              ultimate server.
              It is Mandatory to conclude the plan of care with this line "Follow-up as scheduled"
              Make sure nothing is missed in the output """},

            {"role": "user", "content": "Your job is to write a plan of care for the patient. Don't add the outputs in the\
             future outputs."},
            {"role": "assistant", "content": f"""
            **Anemia**
             None
            **URTI**
            The patient has developed a cold with cough and congestion. Denies body aches. We will call Augmentin 500 mg along with Promathazine to take as directed. Monitor the patient's progress and adjust treatment as necessary.
            **Hypertension**
            The patient's hypertension is relatively well controlled and he is compliant with his medications. Requests for refill which we will do today. Continue current medication regimen and monitor blood pressure regularly. Encourage lifestyle modifications such as a healthy diet and regular exercise.
            **Cervical and Lumbar Herniated Discs**
            The patient has a history of cervical herniated discs with cervical radiculopathy and lumbar herniated discs with sciatica. He is currently under the care of an orthopedic specialist. Ensure the patient continues to follow up with the orthopedic specialist.
            **Osteoarthritis of the Knee**
            The patient has severe osteoarthritis of the knee and has received gel shots twice without significant improvement. If there is no improvement after the third shot, discuss the possibility of total knee replacements bilaterally with the orthopedic specialist.
            **Ambulatory dysfunction/Sciatica/Back pain**
            The patient has a hx of Sciatica and have ambulatory dysfunction, needs a new wheelchair as his current one is broken and non-functional. Renew the referral for a wheelchair to improve his mobility around the house and outside.
            The patient needs refills on all of his medications. Ensure all prescriptions are updated and refilled as necessary.
            F/u as needed."""},
            {"role": "user", "content": f"{self.delimiter}{text}{self.delimiter}"}]
        response = get_completion(messages)

        return response

    def final(self):

        response = self.template_3()

        return response


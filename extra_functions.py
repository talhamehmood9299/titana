from langchain.chains import create_extraction_chain
from langchain.chat_models import ChatOpenAI
import openai
import re

delimiter = "###"


def extract_text(input_string):
    pattern = r'\((.*?)\)'
    matches = re.findall(pattern, input_string)

    if matches:
        return matches
    else:
        return None
def clear_lines_above_and_containing(text, specific_text):
    lines = text.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if specific_text in line:
            if i > 0:
                new_lines.pop()  # Remove the line just above the specific text

            i += 1  # Skip the line containing the specific text
        else:
            new_lines.append(line)
            i += 1

    return '\n'.join(new_lines)


def get_dictation(text):

    prompt = f"""
    Given a piece of text, identify and extract sentences written in the present perfect and present perfect continuous tense. Present perfect tense typically involves the use of 'have/has + past participle,' while present perfect continuous tense involves 'have/has + been + present participle (verb + -ing).' Please provide the identified sentences.
    '''{text}'''
    """;''
    messages_1 = [
        {'role': 'user', 'content': f"{delimiter}{prompt}{delimiter}"},
    ]
    response = get_completion(messages_1)

    return response


def get_completion(messages, model="gpt-4", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,  # This is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_cpt_code(docs):

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    schema = {
            "properties": {
                "systolic": {"type": "string"},
                "diastolic": {"type": "string"},
                "bmi": {"type": "string"}

            },
            "required": [""],
        }

    # Chain which is used to extract schema
    chain = create_extraction_chain(schema, model)
    response_1 = chain.run(docs)

    results = []

    for item in response_1:
        if 'systolic' in item:
            systolic_value = item.get('systolic')

            # condition becomes only true when string containes at least one numerical digit
            if systolic_value != '' and re.search(r'\d', systolic_value):
                systolic = int(item['systolic'].split()[0])  # Extract systolic value

                if systolic < 130:
                    results.append("3074F")
                elif 130 <= systolic <= 139:
                    results.append("3075F")
                elif systolic >= 140:
                    results.append("3077F")

        if 'diastolic' in item:
            diastolic_value = item.get('diastolic')
            if diastolic_value != '' and re.search(r'\d', diastolic_value):
                diastolic = int(item['diastolic'].split()[0])  # Extract diastolic value

                if diastolic < 80:
                    results.append("3078F")
                elif 80 <= diastolic <= 89:
                    results.append("3079F")
                elif diastolic >= 90:
                    results.append("3080F")

        if 'bmi' in item:
            bmi_value = item.get('bmi')
            if bmi_value != '' and re.search(r'\d', bmi_value):
                results.append("3008F")

        return(results)

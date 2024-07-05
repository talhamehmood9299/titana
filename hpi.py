import os
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.document_loaders import TextLoader
from extra_functions import get_completion

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def get_templates(basic_data):

    # loader = TextLoader('./hpi.txt')
    loader = TextLoader("/code/hpi_utf8.txt")

    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(documents=chunks, embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY))

    retriever = vectorstore.as_retriever()

    template = """You are a Medical assistant. Your job is to return the disease or disorder with their paragraphs that 
    is related to mentioned medications.
    Don't add the information of provided medication.
    Return "nothing" if no medication is available in the provided text.
    Use the following pieces of retrieved context to answer the question. 
    Question: {question} 
    Context: {context} 
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    template = rag_chain.invoke(basic_data)
    return template


def gather_information(basic_data):
    system = f"""
 You are a medical assistant. your job is to analyze the doctor dictation available in the provided text. lets think step by step.

Focus on the text that is after the heading of doctor dictation and return the past information with present complication. Ignor the remaing text.
"""
    few_shot_user = """
 You are a medical assistant. your job is to analyze the doctor dictation available in the provided text. lets think step by step.

Focus on the text that is after the heading of doctor dictation and return the past information with present complication. Ignor the remaing text.
"""
    few_shot_assistant = """
    Present complication:
        She is having post-menopausal bleeding, needs GYN follow up asap.
        Present symptoms are night sweats and postmenopausal symptoms.

    Past information:
        Patient made an appointment with GYN on July 18, 2024.
        Feeling better since the last visit.
        Symptoms of dry cough, congestion, wheezing and rhonchi resolved.
        Completed Doxycycline, Decadron and Phenergan treatment.
        Last menstruation 03 to 04 months ago, lasted for 01 day, before this last menstruation was 10 years ago.
        Seen by gynecologist 4 to 5 months ago June 18, 2024.
"""

    prompt = f"""

You are a medical assistant. Your job is to extract the patient present complication and patient past information from the text delimited by triple backticks.

'''{basic_data}'''
"""
    messages_4 = [{'role': 'system', 'content': system},
                        {'role': 'user', 'content': f"{few_shot_user}"},
                        {'role': 'assistant', 'content': few_shot_assistant},
                        {'role': 'user', 'content': f"{prompt}"}]
    response = get_completion(messages_4)
    return response
    
    
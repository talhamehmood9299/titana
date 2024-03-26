from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.document_loaders import TextLoader
from openai import OpenAI
import os

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def get_templates(post_data):
    # loader = TextLoader('./hpi.txt')
    loader = TextLoader("Template.txt")

    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(documents=chunks, embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY))

    retriever = vectorstore.as_retriever()

    template = """You are a Medical assistant. Your job is to return the disease or disorder from the context along with their bullets that
    are related to provided text.
    Return "nothing" if no disease or disorder mentioned in the provided text is related to context.
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

    template = rag_chain.invoke(post_data)
    return template
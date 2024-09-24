from langchain_community.document_loaders import TextLoader # Text loader
from langchain.text_splitter import CharacterTextSplitter # Text splitter
from langchain_community.embeddings import OllamaEmbeddings # Ollama embeddings
from langchain.prompts import ChatPromptTemplate # Chat prompt template
from langchain_community.chat_models import ChatOllama # ChatOllma chat model
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser # Output parser
from langchain_community.vectorstores import FAISS # Vector database
import requests


url = "https://arxiv.org/pdf/2005.11401"
res = requests.get(url)
with open("2005.11401.pdf", "wb") as f:
    f.write(res.content)


loader = TextLoader('2005.11401.pdf', encoding='latin-1')
documents = loader.load()


"""
Splitting the Document into Chunks
The document is split into smaller chunks of text. Each chunk is 1000 characters long with an overlap of 100 characters between consecutive chunks. This helps manage the context window limitations of LLMs.
"""

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)


"""
Creating Embeddings and Storing in Vector Database
This step involves:

Generating embeddings for each text chunk using the OllamaEmbeddings model.
Storing these embeddings in a FAISS vector database for efficient retrieval.
"""

vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="llama3")
)


"""
Creating a Retriever
The retriever is created from the vector store. It will use semantic similarity to retrieve relevant chunks of text based on user queries.
"""

retriever = vectorstore.as_retriever()

"""
Defining the LLM Prompt Template
This template defines how the retrieved context and the user query should be formatted before being sent to the LLM. It instructs the assistant to use the context to answer the question and to admit if the answer is not known.
"""


template = """You are an assistant for specific knowledge query tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Question: {question} 
Context: {context} 
Answer:
"""
prompt = ChatPromptTemplate.from_template(template)


"""
Combining Components into a RAG Chain
This chain combines:

The retriever to get relevant context.
The prompt template to format the query and context.
The ChatOllama model to generate a response.
The StrOutputParser to parse the output.
The temperature=0.2 setting makes the LLM's responses more deterministic (lower temperature).

"""

llm = ChatOllama(model="llama3", temperature=0.2)
rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}  # context window
        | prompt
        | llm
        | StrOutputParser()
)

"""
Querying and Getting Feedback
Finally, a query is made to the RAG chain. The system retrieves relevant context from the vector database, formats it with the query, and generates an answer using the LLM. The result is printed out.
"""

query = "What did this paper mainly talk about?"
print(rag_chain.invoke(query))
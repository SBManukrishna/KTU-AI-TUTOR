import os
from langchain_community.document_loaders import PyPDFLoader,PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain

# Setting Up the Environment (Replace with your API key)
os.environ["GOOGLE_API_KEY"]  = os.getenv('GEMINI_API_KEY')

# 1. Load the PDF Document
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # Create an object for generating embeddings
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")              # Create an object to interact with the OpenAI API

pdf_loader = PyPDFDirectoryLoader('./notes')
docs = pdf_loader.load()         # Load the questions from the PDF

# 2. Prepare the Chat Prompt Template
prompt = ChatPromptTemplate.from_template("""
Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

# This template defines the format for prompting the LLM with context and a question.

# 3. Split the Text into Individual Questions
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)

# This step splits the loaded documents (likely containing multiple questions) into separate documents, each containing a single question.

# 4. Create Document Embeddings
vector = FAISS.from_documents(documents, embeddings)

# This line generates dense vector representations (embeddings) for each question. These embeddings capture the semantic meaning of the text and help retrieve relevant questions.

# 5. Build the Retrieval Chain
retriever = vector.as_retriever()
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
# Here, we create two chains:
#   - Retrieval Chain: This retrieves the most relevant question and its context based on the user's input question using the document embeddings.
#   - Document Chain: This chain uses the LLM to answer the user's question based on the retrieved context.

# 6. User Input and Response Generation
def get_rag_completion(message):
    print("reached here", message)
    response = retrieval_chain.invoke(
        {"input": message})
    print(response)
    return response["answer"]

# get_rag_completion(
#     """In the context of a college course on Compiler Design, 
#                         create course text for the topic " The role of Lexical Analyzer , Input Buffering " 
#                         Do not include anything not directly relating to this topic.
#                         Use the content from the given documents given whenever possible with attribution.
#                         Make sure that your output should have at least everything on this topic that the given notes have 
#                         but strip out any credits or non-textual forms not directly relating to the topic. 
#         """
# )

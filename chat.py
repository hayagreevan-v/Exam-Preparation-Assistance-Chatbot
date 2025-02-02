from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM as Ollama


# get Sentence-Transformers embedding model
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

db_chroma = Chroma(
    embedding_function=embeddings,
    persist_directory="./vectordb",  # Where to save data locally, remove if not necessary
)

# ----- Retrieval and Generation Process -----

# define a user question (query)
query = 'What is Blockchain'

# retrieve context - top 5 most relevant chunks to the query vector 
# (by default, LangChain uses cosine distance metric)
docs_chroma = db_chroma.similarity_search_with_score(query, k=5)

# prepare the retrieved context text for the prompt
context_text = "\n\n".join([doc.page_content for doc, _score in docs_chroma])


# define the prompt template
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
Answer the question based on the above context: {question}.
Provide a detailed answer.
Don’t justify your answers.
Don’t give information not mentioned in the CONTEXT INFORMATION.
Do not say "according to the context" or "mentioned in the context" or similar.
"""

# load the retrieved context and user query into the prompt template
prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
prompt = prompt_template.format(context=context_text, question=query)


# call the Llama 3.2 model using LangChain-Ollama to generate the answer
model = Ollama(model="llama3.2")
response_text = model.predict(prompt)

# print the response
print(response_text)

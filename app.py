from flask import Flask
from flask import request, redirect, make_response, jsonify
from flask_cors import CORS 
from flask import render_template
from werkzeug.utils import secure_filename
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM as Ollama
import json

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

CHROMA_PATH = "vectordb"


@app.route("/")
def HelloWorld():
    return render_template("index.html")

@app.route("/<user>")
def Hello(user):
    return f"Welcome! {user}"

@app.route("/post",methods=['GET', 'POST'])
def post():
    if (request.method == "POST"):
        print(request.form["id"])
        return "Hi"
    else:
        return "Hello World"
    

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request.files)
        f = request.files['file']
        f.save(f"./upload/{secure_filename(f.filename)}")
        loadData(secure_filename(f.filename))

        return redirect("/")
    else:
        return render_template("upload.html")
    
@app.route('/clear', methods=['GET'])
def clear_files():
    for f in os.listdir("./upload"):
        os.remove(f"./upload/{f}")
    
    # embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db_chroma = Chroma(
        collection_name="vectordb",
        # embedding_function=embeddings,
        persist_directory=CHROMA_PATH,  # Where to save data locally, remove if not necessary
    )
    db_chroma.delete_collection()

    return redirect("/")

@app.route('/chat',methods=['GET','POST'])
def chat():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400

    query = data['query']
    res = query_llm(query)  # Call to your LLM function
    return jsonify({"output": res})



def loadData(DOC_PATH):
    # ----- Data Indexing Process -----

    # load your pdf document
    loader = PyPDFLoader(f"./upload/{DOC_PATH}")
    pages = loader.load()
    # split the document into smaller chunks, here with a chunk size of 500
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)
    print("\n PDF File got chunked \n")

    # get Sentence-Transformers embedding model
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    print("\nEmbedding Model Added \n")

    # embed the chunks as vectors and load them into the Chroma database
    try:
        db_chroma = Chroma(collection_name="vectordb",embedding_function=embeddings, persist_directory=CHROMA_PATH)
        print(f"\n {type(db_chroma)} \n")
        print(db_chroma.add_documents(chunks))
        print("\n Success \n")
    except Exception as e :
        print(e)



def query_llm(query):
    # get Sentence-Transformers embedding model
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    db_chroma = Chroma(
        collection_name="vectordb",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,  # Where to save data locally, remove if not necessary
    )

    # ----- Retrieval and Generation Process -----

    # # define a user question (query)
    # query = 'What is Blockchain'

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
    model = Ollama(model="llama3:latest")
    #model = Ollama(model="llama3.2:3b")
    response_text = model.predict(prompt)

    # print the response
    print(response_text)

    return response_text

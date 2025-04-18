from flask import Flask # type: ignore
from flask import request, redirect, make_response, jsonify, send_file # type: ignore
from flask_cors import CORS  # type: ignore
from flask import render_template # type: ignore
from werkzeug.utils import secure_filename # type: ignore
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM as Ollama
import json
import time
import torch

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
        start_time = time.perf_counter()

        print(request.files)
        f = request.files['file']
        f.save(f"./upload/{secure_filename(f.filename)}")
        loadData(secure_filename(f.filename))

        end_time = time.perf_counter()
        print(f"Upload time: {end_time - start_time} seconds")
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

chat_history=[]
@app.route('/chat',methods=['GET','POST'])
def chat():
    if (request.method == "GET"):
        print(chat_history)
        return jsonify({"chat":chat_history})
    if (request.method == "POST"):
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        start_time = time.perf_counter()

        query = data['query']
        chat_format= stringify(chat_history)
        print("Chat format: " + chat_format)
        prompt = f"Previous Conversation:\n{chat_format}\n\nCurrent Question: User: {query}\n"
        res = query_llm(prompt)  # Call to your LLM function

        end_time = time.perf_counter()
        print(f"Response time: {end_time - start_time} seconds")

        chat_history.append({"sender": "user", "text": query})
        chat_history.append({"sender": "bot", "text": res})
        return jsonify({"chat":chat_history})

@app.route('/clear-chat')
def clearChat():
    chat_history.clear()
    print(chat_history)
    return jsonify({"chat":chat_history})

@app.route('/show-files', methods = ['GET'])
def showFiles():
    l=[]
    for f in os.listdir("./upload"):
        l.append(f)
    return jsonify(l)

@app.route("/export-chat")
def export_chat():
    f = open("./data/export.json","w")
    f.write(json.dumps({"chat":chat_history,"files": os.listdir("./upload")}))
    f.close()

    return send_file("./data/export.json")

@app.route("/import-chat", methods = ["POST"])
def import_chat():
    f = request.files['file']
    f.save(f"./data/{secure_filename("import.json")}")

    f= open("./data/import.json","r")
    data = f.read()
    msg = json.loads(data)
    chat_history.clear()
    chat_history.extend(msg['chat'])

    return jsonify({"chat":chat_history})


print(torch.cuda.is_available())

# split the document into smaller chunks, here with a chunk size of 500
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# get Sentence-Transformers embedding model
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") # model_kwargs = {"device": "cuda"}
print("\nEmbedding Model Added \n")

# call the Llama 3.2 model using LangChain-Ollama to generate the answer
model = Ollama(model="llama3.2")
print("Llama 3.2 model is ready...!")
        
def loadData(DOC_PATH):
    # ----- Data Indexing Process -----

    # load your pdf document
    loader = PyPDFLoader(f"./upload/{DOC_PATH}")
    pages = loader.load()
    
    chunks = text_splitter.split_documents(pages)
    print("\n PDF File got chunked \n")

    
    # embed the chunks as vectors and load them into the Chroma database
    try:
        db_chroma = Chroma(collection_name="vectordb",embedding_function=embeddings, persist_directory=CHROMA_PATH)
        print(f"\n {type(db_chroma)} \n")
        print(db_chroma.add_documents(chunks))
        print("\n Success \n")
    except Exception as e :
        print(e)



def query_llm(query):

    db_chroma = Chroma(
        collection_name="vectordb",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH, 
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
    Don't justify your answers.
    If no CONTEXT INFORMATION is given, then give output as No related information found.
    Don't give information not mentioned in the CONTEXT INFORMATION.
    Do not say "according to the context" or "mentioned in the context" or similar.
    In Previous Conversation, I'm User and You are Bot.
    Try to maintain the Previous conversation.
    Try to relate with Previous Conversation mostly focus on last conversation between user and bot.
    """
    #   Don't be so dependent on Previous Conversation.

    # load the retrieved context and user query into the prompt template
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query)
    
    #model = Ollama(model="llama3.2:3b")
    response_text = model.predict(prompt)

    # print the response
    print(response_text)

    return response_text

def stringify(chat_hist):
    chat_format = str()
    for i in chat_hist:
        chat_format+= i["sender"]+": "
        chat_format+= i["text"]+"\n"
    return chat_format

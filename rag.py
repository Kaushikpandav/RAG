from flask import Flask, request, jsonify, render_template
from langchain.llms import BaseLLM
from langchain.schema import Generation, LLMResult
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain  # Updated import
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
import requests
from typing import Any, Dict, List
from pydantic import Field
import os
import sqlite3
from datetime import datetime
import uuid
from langchain_huggingface import HuggingFaceEmbeddings



app = Flask(__name__)

# Initialize database
DB_NAME = "rag_app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_application_logs():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_query TEXT,
    gpt_response TEXT,
    model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)',
                 (session_id, user_query, gpt_response, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            HumanMessage(content=row['user_query']),
            AIMessage(content=row['gpt_response'])
        ])
    conn.close()
    return messages

# Gemini LLM Implementation
class Gemini2LLM(BaseLLM):
    api_key: str = Field(..., alias="api_key")

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def _call(self, prompt: str) -> str:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [{
                "parts":[{"text": prompt}]
            }]
        }
        params = {
            "key": self.api_key
        }

        response = requests.post(url, headers=headers, json=data, params=params)

        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def _llm_type(self):
        return "gemini2"

    def _generate(self, prompts: List[str], stop: Any = None) -> LLMResult:
        generations = [
            [Generation(text=self._call(prompt))] for prompt in prompts
        ]
        return LLMResult(generations=generations, llm_output={})

# RAG Setup
class RAGSystem:
    def __init__(self, api_key):
        self.llm = Gemini2LLM(api_key=api_key)
        # self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None
        # Initialize with a default empty Chroma database
        self.vectorstore = Chroma(
            embedding_function=self.embedding_function,
            persist_directory="./chroma_db"
        )
        self.setup_rag_chain()

    def load_documents(self, file_path):
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            splits = text_splitter.split_documents(documents)
            
            # Update the existing vectorstore instead of creating a new one
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embedding_function,
                persist_directory="./chroma_db"
            )
            # Reinitialize the RAG chain with the updated vectorstore
            self.setup_rag_chain()
            return True
        return False

    def setup_rag_chain(self):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
        
        contextualize_q_system_prompt = """
        Given a chat history and the latest user question
        which might reference context in the chat history,
        formulate a standalone question which can be understood
        without the chat history. Do NOT answer the question,
        just reformulate it if needed and otherwise return it as is.
        """

        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
            ("system", "Context: {context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, question_answer_chain)
        
# Initialize RAG system
API_KEY = "AIzaSyBDildpe8ouXivODeTJOF4k-fLbC6eSjfE"  # Your API key
rag_system = RAGSystem(API_KEY)
create_application_logs()

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported"}), 400

    # Save the file temporarily
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)
    
    # Load the document into RAG system
    success = rag_system.load_documents(temp_path)
    
    # Clean up
    os.remove(temp_path)
    
    if success:
        return jsonify({"message": "Document loaded successfully"})
    return jsonify({"error": "Failed to load document"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    session_id = data.get('session_id', str(uuid.uuid4()))
    message = data['message']
    
    if not rag_system.vectorstore:
        return jsonify({"error": "Please upload a document first"}), 400

    chat_history = get_chat_history(session_id)
    
    try:
        response = rag_system.rag_chain.invoke({
            "input": message,
            "chat_history": chat_history
        })
        
        answer = response['answer']
        insert_application_logs(session_id, message, answer, "gemini-1.5-flash")
        
        return jsonify({
            "response": answer,
            "session_id": session_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0',port=5000)
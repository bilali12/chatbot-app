from  flask import  Flask, render_template, request, jsonify, session, redirect, session, flash
import json
import datetime
import os
import pickle
import tempfile
import asyncio
import json
import pyrebase #pip install  pyrebase4
# from langchain.llms import OpenAi
# pip install  python-dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
from langchain.prompts.prompt import PromptTemplate
from dotenv import load_dotenv

app = Flask(__name__)
config = {
    'apiKey': "AIzaSyA8z9lV2xeF9mMzwwqHInSQuCFYKVj2ltk",
    'authDomain': "authenticate-chatbot.firebaseapp.com",
    'projectId': "authenticate-chatbot",
    'storageBucket': "authenticate-chatbot.appspot.com",
    'messagingSenderId': "211101314559",
    'appId': "1:211101314559:web:7ad64ff8be90de7b3e4bca",
    'measurementId': "G-G6BZBB0SW4",
    'databaseURL': ''

}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# info = auth.get_account_info(user["idToken"])
app.secret_key = 'secret'


@app.route('/', methods=['GET', 'POST'])
def index():
    # store_embedding()
    # print(f"File path before pickle dump: {os.path.abspath('data.pkl')}")
    # with open('data.pkl', 'wb') as f:
    #     pickle.dump(vectors, f)
    # print(f"File path after pickle dump: {os.path.abspath('data.pkl')}")
    return redirect('/login')
    # with open(r"data.json", "r") as f:
    #     train = json.load(f)
    # return train

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == "GET":
        if 'user' in session:
            return redirect("/chatbot")

        return render_template("login.html")

    if 'user' in session:
        return redirect("/chatbot")

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return redirect("/chatbot")
        except Exception as e:
            flash("Email ou mot de pass incorrect ! réessayez s'il vous plaît.", "error")
            return redirect("/login")

    

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')



@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "GET":
         if 'user' in session:
            return redirect("/chatbot")
         return render_template("signup.html")

    if request.method == "POST":
        lastName = request.form['lastName']
        firstName = request.form['firstName']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['pwd']

        if not lastName or not firstName or not email or not password or not confirm_password:
            flash("Tous les champs sont obligatoires", "error")
            return redirect("/register")

        if password != confirm_password:
            flash("le mot de pass et la confirmation doivent etre identiques", "error")
            return redirect("/register")

        try:
            user = auth.create_user_with_email_and_password(email, password)

            user_data = {
                "firstName": firstName,
                "lastName": lastName,
            }
            auth.update_user_info(user['idToken'], user_data)
            return redirect('/login')

        except Exception as e:
            flash(f"Erreur de creation de l'utilisateur", "error")
            return redirect("/register")
        


@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == "GET":
        if 'user'in session:
            return render_template('feedback.html')
    

@app.route('/chatbot')
def chatbot_interface():
    if 'user' in session:
        return render_template('chat.html')
    return redirect("/login")


@app.route('/get', methods=['GET', 'POST'])
def chat():
    
    msg = request.form['msg']
    input = msg
    # print(get_chat_response(msg))
    return "ça va?"

load_dotenv()
if os.getenv("OPENAI_API_KEY") is None  or os.getenv("OPENAI_API_KEY") == "":
    print("OPENAI_API_KEY doesn't set...")
    exit(1)
else:
    # try:
    #     # def store_embedding():
    #     #     with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
    #     #         with open('data.csv', 'rb') as f:
    #     #             contents = f.read()
    #     #             tmp_file.write(contents)
    #     #             tmp_file_path = tmp_file.name
    #     #         loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
    #     #         data = loader.load()

    #     #         embeddings = OpenAIEmbeddings()
                        
    #     #         vectors = FAISS.from_documents(data, embeddings)
    #     #         os.remove(tmp_file_path)

    #     #         with open('data' + ".pkl", "wb") as f:
    #     #             pickle.dump(vectors, f)
        
                
    # except:
    #     pass
    pass

def store_embedding():
    try:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            with open('mayo_clinic.csv', 'rb') as f:
                contents = f.read()
                tmp_file.write(contents)
                tmp_file_path = tmp_file.name
            
            loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
            data = loader.load()
            # print(data)
            embeddings = OpenAIEmbeddings()
            vectors = FAISS.from_documents(data, embeddings)
            print(vectors)
            os.remove(tmp_file_path)

            with open('amazon_customer.pkl', 'wb') as f:
                pickle.dump(vectors, f)

    except FileNotFoundError:
        print("Error: CSV file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# def get_chat_response(msg):
#     """
#         fonction qui utilise l'api de openAi
#         pour fournir une reponse a la requette
#         de l'utilisateur
#     """
#     load_dotenv()
#     if os.getenv("OPENAI_API_KEY") is None  or os.getenv("OPENAI_API_KEY") == "":
#         print("OPENAI_API_KEY doesn't set...")
#         exit(1)
#     else:
#         result = ""
#         try:
#             async def storeDocEmbeds():
#                 print('yes')
#                 with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
#                     with open('data.csv', 'rb') as f:
#                         contents = f.read()
#                         tmp_file.write(contents)
#                         tmp_file_path = tmp_file.name

#                 loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
#                 data = loader.load()

#                 embeddings = OpenAIEmbeddings()
                        
#                 vectors = FAISS.from_documents(data, embeddings)
#                 os.remove(tmp_file_path)

#                 with open('data' + ".pkl", "wb") as f:
#                     pickle.dump(vectors, f)


#             async def get_embedding():
#                 if not os.path.isfile('data' + ".pkl"):
#                             # If not, store the vectors using the storeDocEmbeds function
#                     await storeDocEmbeds()

#                     print('No Docs found !!!')
                        
#                     with open('data' + ".pkl", "rb") as f:
#                             #global vectors
#                         vectors = pickle.load(f)
                            
#                     return vectors

#             async def response():
                
#                 query = msg
#                 result = chain({"question": query})
                        
#                         # Add the user's query and the chatbot's response to the chat history
                        
#                         # You can print the chat history for debugging :
#                         #print("Log: ")
#                         #print(st.session_state['history'])
#             print(result)
#             return jsonify(result["answer"])
#         except:
#             print('something is wrong!')

    

if __name__ == '__main__':
    app.run(debug=True)
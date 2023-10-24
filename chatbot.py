from  flask import  Flask, render_template, request, jsonify, session, redirect
# import pyrebase #pip install  pyrebase4
# from langchain.agents import create_csv_agent
# from langchain.llms import OpenAi
#pip install  python-dotenv
# from dotenv import load_dotenv

app = Flask(__name__)
config = {

}
# firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()

# app.secret_key = 'secret'

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    return f'{email} - {password}'
    

@app.route('/chatbot')
def chatbot_interface():
    return render_template('chat.html')

@app.route('/get', methods=['GET', 'POST'])
def chat():
    
    msg = request.form['msg']
    input = msg
    return get_chat_response(input)

def get_chat_response(msg):
    """
        fonction qui utilise l'api de openAi
        pour fournir une reponse a la requette
        de l'utilisateur
    """
    load_dotenv()
    llm = OpenAi(temperature=0)
    agent = create_csv_agent(llm, 'data.csv')

if __name__ == '__main__':
    app.run(debug=True)
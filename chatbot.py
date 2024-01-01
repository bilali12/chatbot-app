from  flask import  Flask, render_template, request, jsonify, session, redirect, session, flash
from flask_mail import Mail, Message
import random
import json
import os
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import pyrebase #pip install  pyrebase4

# from dotenv import load_dotenv

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

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'bilalidiallo96@gmail.com'
app.config['MAIL_PASSWORD'] = 'bjmq ylfd nspx njvi'
app.config['MAIL_DEFAULT_SENDER'] = 'bilalidiallo96@gmail.com'

mail = Mail(app)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# info = auth.get_account_info(user["idToken"])
app.secret_key = 'secret'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/login')
    

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
            flash("Email or password is incorrect.", "error")
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
            flash("All the fields are required", "error")
            return redirect("/register")

        if password != confirm_password:
            flash("password and confirm password cannot be different", "error")
            return redirect("/register")

        try:
            user = auth.create_user_with_email_and_password(email, password)

            # user_data = {
            #     "displayName": f"{firstName} {lastName}",
            # }
            # auth.update_account_info(user['idToken'], user_data)
            return redirect("/login")

        except Exception as e:
            print(f"Error creating user: {e}")
            flash(f"Error to create the user", "error")
            return redirect("/register")
        


@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == "GET":
        if 'user'in session:
            return render_template('feedback.html')
    if request.method == "POST":
        try:
            feedback_text = request.form.get('msg')
            
            subject = 'Feedback from {}'.format(session['user'])  
            recipient = 'bilalidiallo21@gmail.com'  
            body = 'Feedback: {}'.format(feedback_text)
            
            msg = Message(subject=subject, recipients=[recipient], body=body)
            mail.send(msg)
            flash('Feedback sent successfully!', 'success')
            
            return redirect('/feedback')
        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"Error sending feedback email: {e}")
            flash("Error sending feedback email", "error")
            return redirect('/feedback')
    

@app.route('/chatbot')
def chatbot_interface():
    if 'user' in session:
        return render_template('chat.html')
    return redirect("/login")


@app.route('/get', methods=['GET', 'POST'])
def chat():

    msg = request.form['msg']
    input = msg
    
    return get_chat_response(input)

def get_chat_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    print(prob.item())
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    return "I do not understand..."


if __name__ == '__main__':
    app.run(debug=True)


import os,json
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit


#for socketio, monkeypatching is needed. eventlet is reccomended web server for socketio
import eventlet
eventlet.monkey_patch()
 

#set this flag to False when deploying to bluemix
DEBUG = True


#initialise app
app = Flask(__name__)
#port = int(os.getenv('VCAP_APP_PORT', 8080))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#app.debug = DEBUG
app.config['SECRET_KEY'] = 'pythonkey'
app.config['DATABASE'] = 'database/'
socketio = SocketIO(app)

status_file_name = "status.json"
initial_question = ["who are you",
                    "tell me something about yourself",
                    "what is yor name",
                    "what do you do",
                    "what is your job"]
                    
default_answer = ["Sorry I did not understand your question.",
                  "Hi I am chat-bot AI. How may I help you?",
                  "I am AI-Chatbot. I will help of on your queries regarding posts."+
                  "Choose from the following options:: Press"+
                  "1) Know your status"+
                  "2) To know about Our service category"]

try:
    status_file_abs_path = os.path.join(app.config['DATABASE'],status_file_name)
    with open(status_file_abs_path) as datafile:
        status_obj = json.load(datafile)
except Exception as e:
    print("======Exception occured :: ==========",e)
    
#print("========Status Object is=========== :: \n",status_obj)
    
def call_for_service():
    return status_obj["services_metrics"]
    
def call_for_status():
    return status_obj["parcel"]["tracking"]


# The following is the main function that will process the 
def process_request(message):
    print("\n ==========Inside Process Request =========")
    print(message)
    try:
        num = int(message)
        print("Number is = ", num)
        if(num == 1):
            return "Please Enter your Consignment ID :: "
        elif(num == 2):
            return call_for_service()
        else:
            return call_for_status()
    except Exception as e:
        print("Exception in process_request :: \n", e)
   
    return default_answer[0]
    

@app.route('/', methods=['GET'])
def Index():
    if request.method == 'GET':
        return render_template('chat-bot.html')
    else:
        return "Error:: Internal Issue"
        

@socketio.on('message', namespace='/chat')
def chat_message(message):
    if message == '':       
        response = default_answer[2]
        print("SENDING INITIAL RESPONSE:" + response)
        emit('message', {'response': response})
    else:    
        print("GOT A MESSAGE:" + message)      
        response = process_request(message)
       # print("SENDING RESPONSE:" + response)
        emit('message', {'response': response})
        
 
@socketio.on('connect', namespace='/chat')
def test_connect():
    print("A CLIENT IS CONNECTED TO ME")
   

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    print('CLIENT DISCONNECTED')
    emit('message', {'response': "Server got disconnection request"})
        

if __name__ == "__main__":
    socketio.run(app, debug=DEBUG)

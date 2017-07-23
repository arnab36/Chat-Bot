
import os,json
from flask import Flask, render_template, request, Markup, flash, make_response,jsonify,redirect,url_for
from werkzeug import secure_filename

#from flask_socketio import SocketIO, emit


#for socketio, monkeypatching is needed. eventlet is reccomended web server for socketio
#import eventlet
#eventlet.monkey_patch()
 

#set this flag to False when deploying to bluemix
DEBUG = False

#initialise app
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

#app.debug = DEBUG
app.config['SECRET_KEY'] = 'pythonkey'

app.config['DATABASE'] = 'database/'

#socketio = SocketIO(app)
port = int(os.getenv('VCAP_APP_PORT', 5000))

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

status_file_name = "status.json"
initial_question = ["who are you",
                    "tell me something about yourself",
                    "what is yor name",
                    "what do you do",
                    "what is your job"]
                    
default_answer = ["Sorry I did not understand your question.",
                  "Hi I am chat-bot AI. How may I help you?",
                  "I am AI-Chatbot. I will help of on your queries regarding posts."+
                  "Choose from the following options:: Press <li> </li>"+
                  "<li style='padding-left: 2cm;'> 1) Know your status</li>"+
                  "<li style='padding-left: 2cm;'> 2) To know about Our service category </li>"]

try:
    status_file_abs_path = os.path.join(app.config['DATABASE'],status_file_name)
    with open(status_file_abs_path) as datafile:
        status_obj = json.load(datafile)
except Exception as e:
    print("======Exception occured :: ==========",e)
    
#print("========Status Object is=========== :: \n",status_obj)

# The following function returns a list   
def call_for_service():
    print("Inside call for service:: ")
    print(type(status_obj["services_metrics"]))
    return (status_obj["services_metrics"],"LIST")

# The following function returns a service status    
def call_for_status():
    print("Inside call for status:: ")
    print(type(status_obj["parcel"]["tracking"]))
    return (status_obj["parcel"]["tracking"],"DICT")


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
    return (default_answer[0],"STRING")
    
# Starting function 
@app.route('/', methods=['GET'])
def Index():
    if request.method == 'GET':
        return render_template('chat-bot.html')
    else:
        return "Error:: Internal Issue"

       
@app.route('/upload', methods=['GET','POST'])
def upload():
    file = None
    if request.method == 'POST':    
        try :            
            flag = int(str(request.form['flag']))
            print("flag = ",flag)        
            if(flag == 1):  
                print("In 1")      
                file = request.files['files']   
                print("Type = ",type(file))
                print("content = ",file)
            else:
                print("In 2")
                file = request.files['fileUpload']
                print("Type = ",type(file))
                print("content = ",file)
        except Exception as e :
            print("Exception is :: ",e)
        try:
            # Make the filename safe, remove unsupported chars
            filename_1 = secure_filename(file.filename)               
            save_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_1)   
            if(os.path.isfile(save_file_path)):
                 os.unlink(save_file_path)
            file.save(save_file_path)        
            print("file_uploaded")
            return json.dumps("file_uploaded",indent=2) 
        except Exception as e :
            print("2nd level Exception is :: ",e)
            return json.dumps("Upload Failed "+ e,indent=2) 
    

        
@app.route('/mesageRecieve', methods=['GET','POST'])
def mesageRecieve():
    flag = "STRING"
    response = {}
    output = ""
    message = ""
    print("========== Inside mesageRecieve =========")
    if request.method == 'POST': 
        try:
            print("The method is POST")           
            message = json.loads(request.form['param_1'])  
            print("Received message is :: ",message)
            print("Received message type is :: ",type(message))
            if message == '':       
                output = default_answer[2]
                print("SENDING INITIAL RESPONSE:",response)
              #  return (json.dumps(response,indent=2), json.dumps(flag,indent=2))          
            else:    
                print("GOT A MESSAGE:" + message)      
                output, flag = process_request(message)
                print("SENDING RESPONSE FLAG :", flag)
            
            response['flag'] = flag
            response['response'] = output
            return jsonify(response)  
        except Exception as e:
            print("Exception 1 is ", e)          
            return e
           
            
           
# Socket function
#@socketio.on('message', namespace='/chat')
#def chat_message(message):
#    flag = "STRING"
#    if message == '':       
#        response = default_answer[2]
#        print("SENDING INITIAL RESPONSE:" + response)
#        emit('message', {'response': response,
#                         'flag' : flag
#                         })
#    else:    
#        print("GOT A MESSAGE:" + message)      
#        response, flag = process_request(message)
#        print("SENDING RESPONSE FLAG :" + flag)
#        emit('message', { 'response': response,
#                          'flag' : flag
#                         })
#        
# 
#@socketio.on('connect', namespace='/chat')
#def test_connect():
#    print("A CLIENT IS CONNECTED TO ME")
#   
#
#@socketio.on('disconnect', namespace='/chat')
#def test_disconnect():
#    print('CLIENT DISCONNECTED')
#    emit('message', {'response': "Server got disconnection request"})
        

if __name__ == "__main__":
    #socketio.run(app, debug=DEBUG)
    app.run(host='0.0.0.0', port=port)	

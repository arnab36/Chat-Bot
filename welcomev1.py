import os,json
from flask import Flask, request, render_template,jsonify
#for socketio, monkeypatching is needed. eventlet is reccomended web server for socketio
#import eventlet
from pprint import pprint
from chatterbot.conversation import Statement
from chatterbot import comparisons
from bs4 import BeautifulSoup
import re
import nltk

#nltk.download()
nltk.download('stopwords')  
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')

from nltk.corpus import stopwords # Import the stop word list
from collections import defaultdict
import requests
import lxml.html as lh
import geocoder
from werkzeug import secure_filename
from shutil import copyfile

#import query


from chatterbot import ChatBot
import logging

#initialise app
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

app.config['UPLOAD'] = 'static/uploadedImage/'

port = int(os.getenv('VCAP_APP_PORT', 5000))

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#set this flag to False when deploying to bluemix
DEBUG = True

port = int(os.getenv('VCAP_APP_PORT', 5000))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#app.debug = DEBUG
app.config['SECRET_KEY'] = 'pythonkey'
app.config['DATABASE'] = 'database/'
#socketio = SocketIO(app)

#eventlet.monkey_patch()

status_file_name = "status.json"
initial_question = ["who are you",
                    "tell me something about yourself",
                    "what is yor name",
                    "what do you do",
                    "what is your job"]
                    
default_answer = ["Sorry I did not understand your question.",
                  "Hi I am chat-bot AI. How may I help you?",
                  "I am AI-Chatbot. I will help of on your queries regarding posts."+
                  "Choose from the following options:: type in numeric or text <li> </li>"+
                  "<li style='padding-left: 2cm;'> 1) Track your Package</li>"+
                  "<li style='padding-left: 2cm;'> 2) Schedule a Pickup</li>"+
				  "<li style='padding-left: 2cm;'> 3) Get Quote</li>"+
                  "<li style='padding-left: 2cm;'> 4) Send a Post Card</li>"+
				  "<li style='padding-left: 2cm;'> 5) Know More about DHL services like Pacaging guidelines etc.</li>" + 
                  "<li style='padding-left: 2cm;'> 6) Genuine chat with me. I can tell you jokes :P </li>"]


				  
parcel_length = 0
parcel_breadth = 0
parcel_height = 0
parcel_weight = 0
parcel_envelope = -1
parcel_source = []
parcel_destination = []
parcel_quote = 0
parcel_pickup = ""
src_pin = []
dest_pin = []
next = [-1,0]
				  
try:
    status_file_abs_path = os.path.join(app.config['DATABASE'],status_file_name)
    with open(status_file_abs_path) as datafile:
        status_obj = json.load(datafile)
except Exception as e:
    print("======Exception occured :: ==========",e)
	

try:
    status_file_abs_path = os.path.join(app.config['DATABASE'],status_file_name)
    with open(status_file_abs_path) as datafile:
        status_obj = json.load(datafile)
except Exception as e:
    print("======Exception occured :: ==========",e)
	

print(status_obj["parcel"]["tracking"]["updates"])    
#print("========Status Object is=========== :: \n",status_obj)



def review_to_words( raw_review ):
    # Function to convert a raw review to a string of words
    # The input is a single string (a raw movie review), and 
    # the output is a single string (a preprocessed movie review)
    #
    # 1. Remove HTML
    review_text = BeautifulSoup(raw_review).get_text() 
    #
    # 2. Remove non-letters        
    letters_only = re.sub("[^a-zA-Z0-9.)]", " ", review_text) 
    #
    # 3. Convert to lower case, split into individual words
    words = letters_only.lower().split()                             
    #
    # 4. In Python, searching a set is much faster than searching
    #   a list, so convert the stop words to a set
    stops = set(stopwords.words("english"))                  
    # 
    # 5. Remove stop words
    meaningful_words = [w for w in words if not w in stops]   
    #
    # 6. Join the words back into one string separated by space, 
    # and return the result.
    return( " ".join( meaningful_words ))

with open('greetings.corpus1.json') as data_file:    
    data = json.load(data_file)


dbase = data['greetings']
database = defaultdict(lambda:Statement("Sorry!!! I couldn't understand."),{})

for l in dbase:
	database[Statement(l[0])] = Statement(l[1]) 

#get similarity score
def similar_statement(input_statement):
	closest_match = input_statement
	closest_match.confidence = 0
	statement_list = database.keys()
	# Find the closest matching known statement
	for statement in statement_list:
		confidence = (comparisons.levenshtein_distance(input_statement, statement) + comparisons.synset_distance(input_statement,statement)+comparisons.jaccard_similarity(input_statement,statement)+ comparisons.sentiment_comparison(input_statement,statement))*1.0/4	 #comparisons.sentiment_comparison(input_statement,statement)+

		if confidence > closest_match.confidence:
		    statement.confidence = confidence
		    closest_match = statement
	print closest_match.confidence
	return (closest_match.confidence,closest_match)   


def check_parcel_pincode(message):
	sd = message.strip("\r").strip("\n").split(',')
	if len(sd) < 2:
		return (False,[])
	try:
		s = str(sd[0].strip(" "))
		d = str(sd[1].strip(" "))
		return (True,[s,d])
	except:
		return (False,[])


def check_parcel_dimmension(message):
	lbh = message.strip("\r").strip("\n").split(',')
	if len(lbh) < 3:
		return (False,[])
	try:
		l = float(lbh[0].strip(" "))
		b = float(lbh[1].strip(" "))
		h = float(lbh[2].strip(" "))
		if l > 0 and b > 0 and h > 0:
			return (True,[l,b,h])
		else:
			return (False,[])
	except:
		return (False,[])
		
def check_parcel_weight(message):
	w1 = message.strip("\r").strip("\n")
	try:
		w = float(w1.strip(" "))
		if w > 0:
			return (True,w)
		else:
			return (False,"")
	except:
		return (False,"")

		
def call_for_status(message, i = 0):
	if i == 0:
		return (1,1,"Enter the consignment id")
	elif i == 1:
		return (-1,0,status_obj["parcel"]["tracking"]["current_status"])


#same as call for price quote with last step to schedule the pickup. getting price or delivery details from website still needs to be added after 3
#postal code verification at 3 price to be returned for now is a random number

def call_for_Pickup(message,i=0):
	if i == 0:
		return (3,1,"Enter Length, Breadth, Height of the Parcel seperated by comma")
	elif i == 1:
		check = check_parcel_dimmension(message)
		if check[0] == False:
			return (3,1,"Sorry, I couldn't Understand what you have entered. Please enter Length, Breadth, Height of Parcel separated by comma OR Press * to return to main menu")
		else:
			parcel_length = check[1][0]
			parcel_breadth = check[1][1]
			parcel_height = check[1][2]
			return (3, 2, "Thank you. Please enter Weight of the Parcel")
		
	elif i == 2:
		check = check_parcel_weight(message)
		if check[0] == False:
			return (3, 2,"Sorry, I couldn't Understand what you have entered. Please enter Weight of Parcel OR Press * to return to main menu")
		else:
			parcel_weight = check[1]
			return (3,3,"Thank you. Please enter Pincode of the Pickup and Pincode of destination separated by comma")

	elif i == 3:
		check = check_parcel_pincode(message)
		if check[0] == False:
			return (3,3,"Sorry, I couldn't Understand what you have entered. Thank you. Please enter Pincode of the Pickup and Pincode of destination separated by comma OR Press * to return to main menu")
		else:
			parcel_source = check[1][0]
			parcel_destination = check[1][1]
			check_src = getpostalcodes(parcel_source)
			if check_src[0] == False:
				return (3,3,"Sorry, the Source postal code entered is not correct. Press * to return to main menu")
				
			check_dest = getpostalcodes(parcel_destination)
			if check_dest[0] == False:
				return (3,3,"Sorry, the Destination postal code entered is not correct. Press * to return to main menu")
				
			src_pin = check_src[1]
			dest_pin = check_dest[1]
			#for service in serives:
			#	quote = get_quote()				
			return (3,4,"Thank you. Choose the type of service")
	elif i == 4:
		#Display the list of source destination
		index_selected = 0
		src_pin = src_pin[index_selected]
		disp = "You selected "+src_pin
		return (3,5,disp)
			
	elif i == 5:
		#Display the list of source destination
		index_selected = 0
		dest_pin = dest_pin[index_selected]
		disp = "You selected "+dest_pin
		return (3,6,disp)
	
	elif i == 6:
		#COMPUTE THE TYPE OF SERVICE AND SCHEDULE AND COST
		return (-1,0,"Your Pickup has been scheduled.")
		
	elif i == 7:
		return (-1,0,"Your Pickup has been scheduled.")
	


#call for price quote. getting price or delivery details from website still needs to be added after 3
#postal code verification at 3. price to be returned for now is a random number

def call_for_quote(message,i=0):
	if i == 0:
		return (2,1,"Enter Length, Breadth, Height of the Parcel seperated by comma")
	elif i == 1:
		check = check_parcel_dimmension(message)
		if check[0] == False:
			return (2,1,"Sorry, I couldn't Understand what you have entered. Please enter Length, Breadth, Height of Parcel separated by comma OR Press * to return to main menu")
		else:
			parcel_length = check[1][0]
			parcel_breadth = check[1][1]
			parcel_height = check[1][2]
			return (2, 2, "Thank you. Please enter Weight of the Parcel")
		
	elif i == 2:
		check = check_parcel_weight(message)
		if check[0] == False:
			return (2, 2,"Sorry, I couldn't Understand what you have entered. Please enter Weight of Parcel OR Press * to return to main menu")
		else:
			parcel_weight = check[1]
			return (2,3,"Thank you. Please enter Pincode of the Pickup and Pincode of destination separated by comma")

	elif i == 3:
		check = check_parcel_pincode(message)
		if check[0] == False:
			return (2,3,"Sorry, I couldn't Understand what you have entered. Thank you. Please enter Pincode of the Pickup and Pincode of destination separated by comma OR Press * to return to main menu")
		else:
			parcel_source = check[1][0]
			parcel_destination = check[1][1]
			check_src = getpostalcodes(parcel_source)
			if check_src[0] == False:
				return (2,3,"Sorry, the Source postal code entered is not correct. Press * to return to main menu")
				
			check_dest = getpostalcodes(parcel_destination)
			if check_dest[0] == False:
				return (2,3,"Sorry, the Destination postal code entered is not correct. Press * to return to main menu")
				
			src_pin = check_src[1]
			dest_pin = check_dest[1]
			return (-1,0,"Thank you. \t "+src_pin[0]+dest_pin[0])
			#for service in serives:
			#	quote = get_quote()				
			# return (2,4,"Thank you. Choose the type of service")
	# elif i == 4:
		# #Display the list of source destination
		# index_selected = 0
		# src_pin = src_pin[index_selected]
		# disp = "You selected "+src_pin
		# return (2,5,disp)
			
	# elif i == 5:
		# #Display the list of source destination
		# index_selected = 0
		# dest_pin = dest_pin[index_selected]
		# disp = "You selected "+dest_pin
		# return (2,6,disp)
			
	# elif i == 6:
		# #COMPUTE THE TYPE OF SERVICE AND SCHEDULE AND COST
		# return (-1,0,"Your Pickup has been scheduled.")


#call for sending post card. image accepting step needs to be there after 1
def call_for_Postcard(message,i=0):
	print("in postcard i == "+str(i))
	if i == 0:
		return (4,1,"Enter the name of the recipient's Name")
	elif i == 1:
		if message == "":
			return (4,1,"Invalid Name. Please enter Name OR Press * to return to main menu")
		else:
			return (4,2, "Thank you. Please enter the Message")
		
	elif i == 2:
		if message == "":
			return (4,2,"Invalid Message. Please enter Message OR Press * to return to main menu")
		else:
			return (4,3, "Thank you. Please enter the recipient's address")
	elif i == 3:
		if message == "":
			return (4,3,"Invalid Message. Please enter address OR Press * to return to main menu")
		else:
			return (-1,0, "Thank you. Your post card will be posted shortly")

	
# The following is the main function that will process the 

prev_state = -1

#Main Function
def process_request(message):
	print("\n ==========Inside Process Request =========")
	print(message)
	respreturn = ""
	response=""
		
	if message == "*":
		next[0] = -1
		next[1] = 0
		return (default_answer[1],"STRING")
		
	elif next[0] == -1:
		print("\n ==========Inside chatbot =========")
		try:		
			sta = review_to_words(message)
			respreturn = similar_statement(Statement(sta))
			response = database[respreturn[1]].text
		except Exception as e:
			print("error",e)
		
		#print(response.text)	
		#print(database[response].text)
		#print(response)
			
		try:
			num = int(response)
			print("Number is = ", num)
			if num == 1:
				resp = call_for_status(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
			elif num == 2:
				resp = call_for_quote(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
			elif num == 3:
				resp = call_for_Pickup(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
			elif num == 4:
				resp = call_for_Postcard(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
			    
		except Exception as e:
			print("output your request from chatbot :: \n", e)
			#return default_answer[0] + str(response)
			if respreturn < 0.60:
				response = "Did you mean ? : " + respreturn[1].text + "\n" + response.text
			return response,"STRING"
	
	else:
		try:
			num = int(next[0])
			print("Number is = ", num)
			print("Number is = ", next[1])
			if num == 1:
				resp = call_for_status(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
			elif num == 2:
				resp = call_for_quote(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
			elif num == 3:
				resp = call_for_Pickup(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
			elif num == 4:
				resp = call_for_Postcard(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				return resp[2],"STRING"
				
		except Exception as e:
			print("Sorry I couldn't understand your request ::\n", e)
			return default_answer[0] + str(response)

			
def getpostalcodes(postalcode):
	url = 'http://www.geonames.org/postalcode-search.html?q='+postalcode+'&country='
	r = requests.get(url,verify=False)
	response = r
	tree = lh.document_fromstring(response.content)
	text_value = tree.xpath('//tr/td/text()')
	text_value = text_value[13:]	
	print(text_value)
	print(len(text_value))

	if len(text_value) < 7:
		return(False, "")
		
	cols = len(text_value) / 7
	
	options = []
	for i in range(cols):
		index = i*7
		options.append(text_value[index]+","+text_value[index+1]+","+text_value[index+2]+","+text_value[index + 4])
	return (True,options) 
	
	
@app.route('/', methods=['GET'])
def Index():
    if request.method == 'GET':
        return render_template('chat-bot.html')
    else:
        return "Error:: Internal Issue"
        


@app.route('/upload', methods=['GET','POST'])
def upload():
    file = None
    file_1 = None
    if request.method == 'POST':    
        try :            
            flag = int(str(request.form['flag']))
            print("flag = ",flag)        
            if(flag == 1):  
                print("In 1")      
                file = request.files['files']  
                #file_1 = request.files['files']  
                print("Type = ",type(file))
                print("content = ",file)
            else:
                print("In 2")
                file = request.files['fileUpload']
                #file_1 = request.files['fileUpload']
                print("Type = ",type(file))
                print("content = ",file)
        except Exception as e :
            print("Exception is :: ",e)
        try:
            # Make the filename safe, remove unsupported chars
            filename_1 = secure_filename(file.filename)               
            save_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_1)  
            save_file_path_1 = os.path.join(app.config['UPLOAD'], filename_1)  
            if(os.path.isfile(save_file_path)):
                 os.unlink(save_file_path)
            file.save(save_file_path) 
            copyfile(save_file_path,save_file_path_1)
            #file_1.save(save_file_path_1)  			
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

		

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)	
        
 




'''
# Uncomment the following line to enable verbose logging
# logging.basicConfig(level=logging.INFO)

chatbot = ChatBot("AI-bot",
    storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
    logic_adapters=[ "chatterbot.logic.BestMatch"
    ],
    input_adapter="chatterbot.input.TerminalAdapter",
    output_adapter="chatterbot.output.TerminalAdapter",
    database="../database.db",
	trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
) 

# First, lets train our bot with some data
chatbot.train('./greetings.corpus.json')

# Create a new instance of a ChatBot
chatbot = ChatBot("AI-bot",
    storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
    logic_adapters=[ "chatterbot.logic.BestMatch"
    ],
    input_adapter="chatterbot.input.TerminalAdapter",
    output_adapter="chatterbot.output.TerminalAdapter",
    database="../database.db",
	trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
) 

# First, lets train our bot with some data
chatbot.train('./greetings.corpus.json')


'''

import os,json
from flask import Flask, request, render_template,jsonify

from pprint import pprint
from chatterbot.conversation import Statement
from chatterbot import comparisons
from bs4 import BeautifulSoup
import re
import nltk

#nltk.download()
#nltk.download('stopwords')  
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('vader_lexicon')

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

# The following is for getting delivery date
import dateTime
from random import randint

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

local_memory = {}
local_memory["Thank you.The following is your Percel description."] = ""

status_file_name = "status.json"
country_city_file_name = "countriesToCities.json"

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
                  "<li style='padding-left: 2cm;'> 4) Send a Post Card</li>"]


				  
parcel_length = 0
parcel_breadth = 0
parcel_height = 0
parcel_weight = 0
parcel_envelope = -1
parcel_source = ""
parcel_destination = ""
parcel_quote = 0
parcel_pickup = ""
src_pin = []
dest_pin = []
next = [-1,0]
status_obj = ""
country_city_status_obj = ""

				  
#try:
#    status_file_abs_path = os.path.join(app.config['DATABASE'],status_file_name)
#    with open(status_file_abs_path) as datafile:
#        status_obj = json.load(datafile)
#except Exception as e:
#    print("======Exception occured :: ==========",e)
#	

try:
    status_file_abs_path = os.path.join(app.config['DATABASE'],status_file_name)
    with open(status_file_abs_path) as datafile:
        status_obj = json.load(datafile)
except Exception as e:
    print("======Exception occured :: ==========",e)
    
try:
    country_city_abs_path = os.path.join(app.config['DATABASE'],country_city_file_name)
    with open(country_city_abs_path) as datafile:
        country_city_status_obj = json.load(datafile)
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
	sd = message.strip("\r").strip("\n")
	return (True,sd)


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

		
def call_for_status(message, i):
	if i == 0:
		return (1,1,"Enter the consignment id")
	elif i == 1:
         package_status = {}
         city = "Not Found"
         country = "Not Found"
         count = 0
         position = randint(0,len(country_city_status_obj)) 
         for i in country_city_status_obj:             
             if position == count:
                 index = randint(0,len(country_city_status_obj[i]))
                 city = country_city_status_obj[i][index]
                 country = i
                 break
                
             count += 1
        booking_date = dateTime.getBookingDate()
        delivery_date = dateTime.getDeliveryDate()
        package_status["Consignment ID"] = message
        package_status["Booking Date"] = booking_date
        package_status["Current Location"] = city+","+country
        package_status["Delivery Date"] = delivery_date
        package_status["Contact No"] = dateTime.getContactNo()
        return (-1,0,package_status)
  
#         return (-1,0,status_obj["parcel"]["tracking"]["current_status"])


#same as call for price quote with last step to schedule the pickup. getting price or delivery details from website still needs to be added after 3
#postal code verification at 3 price to be returned for now is a random number

def call_for_Pickup(message,i=0):
	if i == 0:
		return (3,1,"Enter Length, Breadth, Height of the Parcel seperated by comma")
	elif i == 1:
		check = check_parcel_dimmension(message)
		if check[0] == False:
			return (3,1,"Sorry, I couldn't Understand what you have entered. Please enter Length, Breadth, Height of Parcel in centimeters separated by comma OR Press * to return to main menu")
		else:
			parcel_length = check[1][0]
			parcel_breadth = check[1][1]
			parcel_height = check[1][2]
			return (3, 2, "Thank you. Please enter Weight of the Parcel in gram")
		
	elif i == 2:
		check = check_parcel_weight(message)
		if check[0] == False:
			return (3, 2,"Sorry, I couldn't Understand what you have entered. Please enter Weight of Parcel OR Press * to return to main menu")
		else:
			parcel_weight = check[1]
			return (3,3,"Thank you. Please enter Pincode of the Pickup")

	elif i == 3:
		global src_pin
		check = check_parcel_pincode(message)
		if check[0] == False:
			return (3,3,"Sorry, I couldn't Understand what you have entered. Thank you. Please enter Pincode of the Pickup OR Press * to return to main menu")
		else:
			
			parcel_source = check[1]
			check_src = getpostalcodes(parcel_source)
			if check_src[0] == False:
				return (3,3,"Sorry, the Source postal code entered is not correct. Press * to return to main menu")
				
			src_pin = check_src[1]
			print(check_src)
			resp = ""
			resp = create_selection_list(src_pin)   
#			resp = "Choose the place from the list "			
#			cindex = 0			
#			for r in src_pin:
#				cindex += 1				
#				resp += resp + str(cindex) + ") " + r + "|| "
			return (3,4,resp)

	elif i == 4:
		check = message
		try:
			selectedoption = int(message) - 1
			print("parcel source+ ",src_pin)
			if len(src_pin) > selectedoption and len(src_pin) >= 0:
				resp = "You selected :: <br>"+ src_pin[selectedoption]  + ".<br> Please enter Pincode of the Destination."
				return (3, 5,resp)
			else:
				resp = "Not correct choice selected1. Please select again."
				
				return (3, 4,resp)	
			
		except Exception as e:
			print("error",e)
			resp = "Not correct choice selected2. Please select again."
			return (3, 4,resp)


	elif i == 5:
		global dest_pin
		check = check_parcel_pincode(message)
		if check[0] == False:
			return (3,5,"Sorry, I couldn't Understand what you have entered. Thank you. Please enter Pincode of destination separated by comma OR Press * to return to main menu")
		else:
			parcel_destination = check[1]
			check_dest = getpostalcodes(parcel_destination)
			if check_dest[0] == False:
				return (3,5,"Sorry, the Destination postal code entered is not correct. Press * to return to main menu")
			dest_pin = check_dest[1]
			print(check_dest)			
			resp = ""
			resp = create_selection_list(dest_pin)   			
#			cindex = 0			
#			for r in dest_pin:
#				cindex += 1
#				resp = resp + str(cindex) + ") " + r + "|| "	
#				if cindex == 5:
#				  break 
			return (3,6,resp)
   
	elif i == 6:
		check = message
		try:
			selectedoption = int(message) - 1
			if len(dest_pin) > selectedoption and len(dest_pin) >= 0:
				resp = "You selected "+ dest_pin[selectedoption]+"<br>"
				#COMPUTE THE TYPE OF SERVICE AND SCHEDULE AND COST
				delivery_date = dateTime.getDeliveryDate()
				resp += ". Your Parcel will be deliverd by :: " + delivery_date+"<br>"
				resp += "Should I schedule a pickup? Please type yes or no." 
				return (3, 7,resp)				
			else:
				resp = "Not correct choice selected. Please select again."
				return (3, 6,resp)	
		except Exception as e:
			print("error",e)
			resp = "Not correct choice selected. Please select again."
			return (3, 6,resp)
	elif i == 7:
		if message.lower() == "yes":
			return (-1,0,"Your Pickup has been scheduled.")
		else:
			return (-1,0,"Your Pickup has been not being scheduled. Please type * to see the main menu")
		
	elif i == 8:
		return (-1,0,"Your Pickup has been scheduled.")
	


#call for price quote. getting price or delivery details from website still needs to be added after 3
#postal code verification at 3. price to be returned for now is a random number

def call_for_quote(message,i=0):
	if i == 0:
		return (2,1,"Enter Length, Breadth, Height of the Parcel seperated by comma")
	elif i == 1:
		check = check_parcel_dimmension(message)
		if check[0] == False:
			return (2,1,"Sorry, I couldn't Understand what you have entered. Please enter Length, Breadth, Height of Parcel in centimeters separated by comma OR Press * to return to main menu")
		else:
			parcel_length = check[1][0]
			parcel_breadth = check[1][1]
			parcel_height = check[1][2]
			return (2, 2, "Thank you. Please enter Weight of the Parcel in gram")
		
	elif i == 2:
		check = check_parcel_weight(message)
		if check[0] == False:
			return (2, 2,"Sorry, I couldn't Understand what you have entered. Please enter Weight of Parcel OR Press * to return to main menu")
		else:
			parcel_weight = check[1]
			return (2,3,"Thank you. Please enter Pincode of the Pickup")

	elif i == 3:
		global src_pin
		check = check_parcel_pincode(message)
		if check[0] == False:
			return (2,3,"Sorry, I couldn't Understand what you have entered. Thank you. Please enter Pincode of the Pickup OR Press * to return to main menu")
		else:
			
			parcel_source = check[1]
			check_src = getpostalcodes(parcel_source)
			if check_src[0] == False:
				return (2,3,"Sorry, the Source postal code entered is not correct. Press * to return to main menu")
				
			src_pin = check_src[1]
			print(check_src)
			resp = ""
			resp = create_selection_list(src_pin)   
#			resp = "Choose the place from the list "			
#			cindex = 0			
#			for r in src_pin:
#				cindex += 1				
#				resp +=  str(cindex) + ") " + r + "|| "
#				if cindex == 5:
#				 break        
			return (2,4,resp)

	elif i == 4:
		check = message
		try:
			selectedoption = int(message) - 1
			print("parcel source+ ",src_pin)
			if len(src_pin) > selectedoption and len(src_pin) >= 0:
				resp = "You selected :: <br> "+ src_pin[selectedoption]  + ". <br>Please enter Pincode of the Destination."
				return (2, 5,resp)
			else:
				resp = "Not correct choice selected1. Please select again."
				
				return (2, 4,resp)	
			
		except Exception as e:
			print("error",e)
			resp = "Not correct choice selected2. Please select again."
			return (2, 4,resp)


	elif i == 5:
		global dest_pin
		check = check_parcel_pincode(message)
		if check[0] == False:
			return (2,5,"Sorry, I couldn't Understand what you have entered. Thank you. Please enter Pincode of destination separated by comma OR Press * to return to main menu")
		else:
			parcel_destination = check[1]
			check_dest = getpostalcodes(parcel_destination)
			if check_dest[0] == False:
				return (2,5,"Sorry, the Destination postal code entered is not correct. Press * to return to main menu")
			dest_pin = check_dest[1]
			print(check_dest)			
			resp = ""
			resp = create_selection_list(dest_pin)   		
#			cindex = 0			
#			for r in dest_pin:
#				cindex += 1
#				resp = resp + str(cindex) + ") " + r + "|| "
				 
			return (2,6,resp)
	elif i == 6:
		check = message
		try:
			selectedoption = int(message) - 1
			if len(dest_pin) > selectedoption and len(dest_pin) >= 0:
				resp = "You selected "+ dest_pin[selectedoption]
				#Compute time and price here	
				delivery_date = dateTime.getDeliveryDate()
				resp += ". Your Parcel will be deliverd by :: " + delivery_date
				return (-1, 0,resp)
			else:
				resp = "Not correct choice selected. Please select again."
				return (2, 6,resp)	
		except Exception as e:
			print("error",e)
			resp = "Not correct choice selected. Please select again."
			return (2, 6,resp)


#call for sending post card. image accepting step needs to be there after 1
def call_for_Postcard(message,i=0):
	print("in postcard i == "+str(i))
	if i == 0:
		return (4,1,"Enter the name of the recipient's Name")
	elif i == 1:
		if message == "":
			return (4,1,"Invalid Name. Please enter Name OR Press * to return to main menu")
		else:
			local_memory["Name"] = message
			return (4,2, "Thank you. Please enter the Message")
		
	elif i == 2:
		if message == "":
			return (4,2,"Invalid Message. Please enter Message OR Press * to return to main menu")
		else:
			local_memory["Message"] = message
			return (4,3, "Thank you. Please enter the recipient's address")
	elif i == 3:
		if message == "":
			return (4,3,"Invalid Message. Please enter address OR Press * to return to main menu")
		else:
			local_memory["Address"] = message	
			local_memory["Delivery Time"] = dateTime.getDeliveryDate()
			#return (-1,0, "Thank you. Your post card will be posted shortly")
			return (-1,0, local_memory)

	
# The following is the main function that will process the 

prev_state = -1

#Main Function
def process_request(message):
	print("\n ==========Inside Process Request =========")
	print(message)
	response = ""
		
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
		
					
		try:
			num = int(response)
			print("Number is = ", num)
			if num == 1:
				resp = call_for_status(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				if (resp[0] == -1 and resp[1] == 0):
				   return resp[2],"DICT"
				else:
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
				if (resp[0] == -1 and resp[1] == 0):
				   return resp[2],"DICT"
				else:
				   return resp[2],"STRING"
			    
		except Exception as e:
			print("output your request from chatbot :: \n", e)
			#return default_answer[0] + str(response)
			if respreturn < 0.60:
				response = "Did you mean ? : " + respreturn[1].text + "\n" + response.text
			return response,"STRING"
		else:
			return default_answer[0],"STRING"
	
	else:
		try:
			num = int(next[0])
			print("Number is = ", num)
			if num == 1:
				resp = call_for_status(message,next[1])
				next[0] = resp[0]
				next[1] = resp[1]
				if (resp[0] == -1 and resp[1] == 0):
				   return resp[2],"DICT"
				else:
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
				if (resp[0] == -1 and resp[1] == 0):
				   return resp[2],"DICT"
				else:
				   return resp[2],"STRING"
			else:
				return default_answer[0]	
		except Exception as e:
			print("Sorry I couldn't understand your request ::\n", e)
			return default_answer[0] + str(response),"STRING"
			
        
def create_selection_list(src_pin):
    resp = "Choose the place from the list <br>"
    print("resp :: ",resp)
    cindex = 0
    for r in src_pin:
        cindex += 1
        resp = resp + '<input type="radio" name="pincode" value="'+str(cindex)+'"> '+r +' <br>' 
        if cindex == 5:
		break 
    return resp

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
 


# Starting function 
@app.route('/', methods=['GET'])
def Index():
    if request.method == 'GET':
        return render_template('chat-bot.html')
    else:
        return "Error:: Internal Issue"
        

       
#@app.route('/upload', methods=['GET','POST'])
#def upload():
#    file = None
#    if request.method == 'POST':    
#        try :            
#            flag = int(str(request.form['flag']))
#            print("flag = ",flag)        
#            if(flag == 1):  
#                print("In 1")      
#                file = request.files['files']   
#                print("Type = ",type(file))
#                print("content = ",file)
#            else:
#                print("In 2")
#                file = request.files['fileUpload']
#                print("Type = ",type(file))
#                print("content = ",file)
#        except Exception as e :
#            print("Exception is :: ",e)
#        try:
#            # Make the filename safe, remove unsupported chars
#            filename_1 = secure_filename(file.filename)               
#            save_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_1)   
#            if(os.path.isfile(save_file_path)):
#                 os.unlink(save_file_path)
#            file.save(save_file_path)        
#            print("file_uploaded")
#            return json.dumps("file_uploaded",indent=2) 
#        except Exception as e :
#            print("2nd level Exception is :: ",e)
#            return json.dumps("Upload Failed "+ e,indent=2) 

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

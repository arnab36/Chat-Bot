	
			var channel = "/chat";
			var initialised = false;
			var uploadFileFlag = false;
			var input_file_name = "";
			var totalLength = 622;
			var maxCharacter = 75;
			var temp;
			var fileUploadTypeFlag = 0;
			var files = null;
			var dropzone = document.getElementById("upload_link");				
			
			ajaxCallForText($.trim($("#messageText").val()));
	 

			$("#sendMessage").on("click", function() {
				if(uploadFileFlag)
					ajaxCallForFile();
				else
					sendMessage();
			});
	 
	 
			$("#messageText").keyup(function(e){
				if(e.keyCode == 13)
				{
					if(uploadFileFlag)
						ajaxCallForFile();
					else
						sendMessage();
				}
			});
	 
						
			function sendMessage() {
				if ( $.trim($("#messageText").val()) ) 
				{
					$("input[type=radio]").attr('disabled', true);
					var dNow = new Date();
					time = dNow.getHours() + ':' + dNow.getMinutes() + ':' + dNow.getSeconds();
					var margin = calculateMargin($("#messageText").val());
					$("#messageList").append( '<ul id="userChat" style="margin-left:'+margin+'px"> '+'<font color="white">'+ $("#messageText").val()+'&nbsp </font>  <font style="float:right"> ' + time + ' </font><img src="static/images/client-icon.png"> <font color="red" style="float:right">You: </font>' +  '</ul>');
					$("#messageList").scrollTop($("#messageList")[0].scrollHeight);
					$("#messageList").removeClass("w3-light-gray");
					//socket.send( $.trim($("#messageText").val()) );
					ajaxCallForText($.trim($("#messageText").val()));
					$("#messageText").val('');
					$("#messageText").prop('disabled', true);
					console.log("sendMessage button was clicked");
				}
				else
					$("#messageText").focus();	 
			}
			
			
			function ajaxCallForText(message){				
				var json_data_1 = JSON.stringify(message);
				console.log("message :: ",message);
				console.log(typeof(message));
				$.ajax({
					url: '/mesageRecieve',
					method: 'POST',
					async: true,
					data:{ 
						param_1: json_data_1 
					},						
					success: function(response) {	
						temp = response;
						processOutput(response);				  
					},
					error: function(xhr, textStatus, errorThrown){								
						console.log(xhr);								
						console.log(errorThrown);	
						processOutput(errorThrown);
					}
				});			
			}
			

			
			$("#btnRefresh").on("click", function() {
				$("#messageText").prop('disabled', true);
				$("#messageList").html('<ul id="list"></ul>');
				$("#messageList").addClass("w3-light-gray");
				console.log("sending empty message ''");
				//socket.send('');
			});

		
		function calculateMargin(strMessage){
			if(strMessage.length > 75){
				return 200;
			}
			var marginLength = parseInt(totalLength - (strMessage.length * 8.3));
			if(marginLength > 250){
				return 250;
			}else 
				return marginLength;
		}
		
		
		function calculatepadding(strMessage) {
			if(strMessage.length < 25) {
				return 100;
			}
			if(strMessage.length >25 &&  strMessage.length < 50 ){
				return 50;
			}else
				return 20;
		}	
	
		
		// The following function will process the output from python.
		/* function processOutput(message) {
			var flag  = message['flag'];
			console.log("Flag is :: ", flag);
			
			var actual_content = message['response'];
			console.log("Actual COntent :: ",actual_content );
			
			var rightPadding = 0;
			var longestString = "";
			
			if(flag == "STRING"){
				rightPadding = calculatepadding(actual_content);
				displayOutput(actual_content,rightPadding);
			}else if(flag == "LIST") {
				var str = "Our options are :: <li></li>";
				var counter = 0;
				for(var i in actual_content){
					counter = parseInt(i) + 1;
					str += '<li style="padding-left: 2cm;"> '+counter +") "+ actual_content[i] + "</li>";
					longestString = actual_content[i].length > longestString.length? actual_content[i]:longestString 
				}
				rightPadding = calculatepadding(longestString);
				displayOutput(str,rightPadding);
			}else if(flag == "DICT"){
				var str = "Your status is :: <li> </li>";
				str += '<li style="padding-left: 3cm;"> <font color="red"> '+"Package No :: </font>"+ actual_content['code'] + "</li>";
				longestString = actual_content['code'].length > longestString.length? actual_content['code']:longestString 
				str += '<li style="padding-left: 3cm;"> <font color="red">'+"Helpline :: </font>"+ actual_content['notification']['text'] + "</li>";
				longestString = actual_content['notification']['text'].length > longestString.length? actual_content['notification']['text']:longestString 
				str += '<li style="padding-left: 3cm;"> <font color="red">'+"Current Status :: </font>"+ actual_content['current_status'] + "</li>";
				longestString = actual_content['current_status'].length > longestString.length? actual_content['current_status']:longestString 
				rightPadding = calculatepadding(longestString);
				displayOutput(str,rightPadding);
				
			}else{
				console.log("Error :: Server has send wrong data. Flag is missing.");
				rightPadding = calculatepadding("Some Technical Fault has occured. Sorry For the inconvenience.");
				displayOutput("Some Technical Fault has occured. Sorry For the inconvenience.",rightPadding)
			}
				
		} */
		
		function processOutput(message) {
			var flag  = message['flag'];
			console.log("Flag is :: ", flag);
			
			var actual_content = message['response'];
			console.log("Actual COntent :: ",actual_content );
			
			var rightPadding = 0;
			var longestString = "";
			
			if(flag == "STRING"){
				rightPadding = calculatepadding(actual_content);
				displayOutput(actual_content,rightPadding);
			}else if(flag == "LIST") {
				var str = "Our options are :: <li></li>";
				var counter = 0;
				for(var i in actual_content){
					counter = parseInt(i) + 1;
					str += '<li style="padding-left: 2cm;"> '+counter +") "+ actual_content[i] + "</li>";
					longestString = actual_content[i].length > longestString.length? actual_content[i]:longestString 
				}
				rightPadding = calculatepadding(longestString);
				displayOutput(str,rightPadding);
			}else if(flag == "DICT"){  
				//var dict = JSON.parse(actual_content); 
				var str = "Your status is :: <li> </li>";
				for(var i in actual_content){
					str += '<li style="padding-left: 3cm;"> <font color="red"> '+i+':: </font>'+ actual_content[i] + '</li>';
					longestString = (i.toString()+"::"+actual_content[i].toString()).length > longestString.length? (i.toString()+"::"+actual_content[i].toString()):longestString 
				}			
				
				rightPadding = calculatepadding(longestString);
				displayOutput(str,rightPadding);
				
			}else{
				console.log("Error :: Server has send wrong data. Flag is missing.");
				rightPadding = calculatepadding("Some Technical Fault has occured. Sorry For the inconvenience.");
				displayOutput("Some Technical Fault has occured. Sorry For the inconvenience.",rightPadding)
			}				
		}
		
		
		// This function will just display a string message in chatBot
		function displayOutput(display_text,padding) {
			var dNow = new Date();
			//var padding = calculatepadding(display_text)
			time = dNow.getHours() + ':' + dNow.getMinutes() + ':' + dNow.getSeconds();
			$("#messageList").append( '<ul id="responseChat" style="padding-right:'+padding+'px"><font color="gray"> ' + time + ' </font><img src="static/images/server_image.jpg"> ' +display_text+ '</ul>');
			$("#messageList").scrollTop($("#messageList")[0].scrollHeight);
			$("#messageList").removeClass("w3-light-gray");
			$("#messageText").prop('disabled', false);
			$("#messageText").focus();
			console.log("message displayed is: " + display_text);
		}
		
		$(document).on('click','#file1',function(e){
		//$('#file1').click(function(e){
			e.preventDefault();
			if(!uploadFileFlag){
				$('#browse').click();
			}else {
				uploadFileFlag = false;
				input_file_name = "";
				$(".attachment").attr('src',"./static/images/Attachment.png");
				document.getElementById('messageText').removeAttribute('readonly');
				$("#messageText").val('');
				$('input[type=file]').val("");
			}					
		});
		
		
		$('input[name="fileUpload"]').change(function(){
			input_file_name = $('input[type=file]').val().split('\\').pop();			
			var ext = input_file_name.substring(input_file_name.lastIndexOf('.'),input_file_name.length);	
			console.log(input_file_name);
			console.log(ext);			
			$('#messageText').val(input_file_name);
			uploadFileFlag = true;
			$(".attachment").attr('src',"./static/images/close.png");
			fileUploadTypeFlag = 2;
			$('#messageText').attr('readonly', 'true');
		});
		
		
		function uploadPictures(){
			if(input_file_name != ""){
				var dNow = new Date();
				time = dNow.getHours() + ':' + dNow.getMinutes() + ':' + dNow.getSeconds();
				var margin = calculateMargin($("#messageText").val());
				var ext = input_file_name.substring(input_file_name.lastIndexOf('.'),input_file_name.length);
				if(ext ==".png" || ext == ".jpg" || ext == ".jpeg"){
					$("#messageList").append('<ul class="userUploadedImage" style="margin-left:'+margin+'px;" ><li><img src="static/uploadedImage/'+input_file_name+'" style="height:150px;width:150px;" ></li></ul>');				
				}
				$("#messageList").append( '<ul id="userChat" style="margin-left:'+margin+'px" ><font color="white"><a href="static/uploadedImage/'+input_file_name+'" target="_blank"><u>' +$("#messageText").val()+ '</u></a> &nbsp</font><font style="float:right"> ' + time + ' </font><img src="static/images/client-icon.png"> <font color="red" style="float:right">You: </font>' +  '</ul>');								
				$("#messageList").scrollTop($("#messageList")[0].scrollHeight);
				$("#messageList").removeClass("w3-light-gray");				
				$("#messageText").prop('disabled', false);
				$("#messageText").val('');
				$(".attachment").attr('src',"./static/images/Attachment.png");
			}			
		}	

		
		 
		function ajaxCallForFile(){
			var formData;
			console.log("input_file_name :: ", input_file_name);
			if(fileUploadTypeFlag == 1) {
				formData = new FormData();
				formData.append("files", files);
				formData.append("flag", fileUploadTypeFlag);
			}else{
				formData = new FormData($("#file_upload_form")[0]);						
				formData.append("flag", fileUploadTypeFlag);
			}
			console.log("formData = ",formData);					
			$.ajax({
				url: '/upload',
				method: 'post',
				data:formData,						
				async: false,
				success: function() {				
					uploadPictures();
					document.getElementById('messageText').removeAttribute('readonly');					
				},
				error: function(xhr, textStatus, errorThrown){								
					console.log(xhr);								
					console.log(errorThrown);	
					processOutput(errorThrown);
					document.getElementById('messageText').removeAttribute('readonly');
				},
				cache: false,
				contentType: false,
				processData: false
			});		
		} 
		
		
		// Code for drag and drop
		dropzone.ondrop = function(e){
			e.preventDefault();	
			e.stopImmediatePropagation();
			this.className = 'drag-panel';
			console.log(typeof(e.dataTransfer.files[0]));	
			console.log(e.dataTransfer.files[0]);	
			
			console.log(typeof(e.dataTransfer.files[0].name));	
			console.log(e.dataTransfer.files[0].name);
			input_file_name = e.dataTransfer.files[0].name;
			files = e.dataTransfer.files[0];
			
			// Checking the extension
			var ext = input_file_name.substring(input_file_name.lastIndexOf('.'),input_file_name.length);			
			if(ext == ".pdf" || ext == ".doc" || ext == ".docx" || ext ==".png" || ext == ".jpg" || ext == ".jpeg"){									
				if(input_file_name!=""){
					fileUploadTypeFlag = 1;
					uploadFileFlag = true;
					$(".attachment").attr('src',"./static/images/close.png");
					console.log("flag changed to :: ", fileUploadTypeFlag);					
					$('#messageText').val(input_file_name);	
					$('#messageText').attr('readonly', 'true');
				}				
			}else {
				input_file_name ="";
				files = "";
				//alert("Only Pdf, Doc, Docx are allowed....");
				//document.getElementById("errormsg").removeAttribute("hidden");
				//$('#errormsg1').text("Only Pdf, Doc, Docx are allowed....");  
				return;
			}											
		}
		
		
		dropzone.ondragover = function(e) {						
			this.className = 'drag-panel';		
			return false;
		} 
		
		dropzone.ondragleave = function() {
			this.className = 'drag-panel';
			return false;
		}			
		
		$(".drag-panel").mouseover(function() {
			$('.drag-panel').css('cursor', 'pointer');
		});		
		
		$(document).on('change','input:radio[name="pincode"]',function(){					
			var op = $('input[name="pincode"]:checked').val();
			$("#messageText").val(op);
		});
		
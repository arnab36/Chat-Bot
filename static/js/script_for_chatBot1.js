	//$(function(){ 

			var channel = "/chat";
			var initialised = false;
			var uploadFileFlag = false;
			var input_file_name = "";
	 
			//connect though websocket method on priority
			var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + channel, {transports:['websocket','polling']});

			console.log('connect to: ' + location.protocol + '//' + document.domain + ':' + location.port + channel);
		   
		   
			socket.on("error", function(data) {
				console.log("connetion error:" + data);
				if (socket.connected){
					console.log("Socket connetion ok");
				}
				else {
					console.log("Socket connetion failed");
				}
			});


			//connect will be triggered only once
			socket.on("connect", function(data) {
				console.log("connect event triggered:" + data);
				if (socket.connected){
					console.log("Socket connetion ok");
				}
				else {
					console.log("Socket connetion failed");
				}
				if (socket.connected && !initialised) {
					initialised = true;
					console.log("sending empty message ''");
					socket.send('');
				}
			});
	 

			socket.on("message", function (message) {
				processOutput(message);				
			});
	 

			$("#sendMessage").on("click", function() {
				if(uploadFileFlag)
					uploadPictures();
				else
					sendMessage();
			});
	 
	 
			$("#messageText").keyup(function(e){
				if(e.keyCode == 13)
				{
					if(uploadFileFlag)
						uploadPictures();
					else
						sendMessage();
				}
			});
	 
			function sendMessage() {
				if ( $.trim($("#messageText").val()) ) 
				{
					var dNow = new Date();
					time = dNow.getHours() + ':' + dNow.getMinutes() + ':' + dNow.getSeconds();
					$("#messageList").append( '<ul id="userChat"><font color="gray"> ' + time + ' </font><img src="static/images/client-icon.png" style="height:22px;width:23px;"> <font color="red">You: </font>' +$("#messageText").val()+ '</ul>');
					$("#messageList").scrollTop($("#messageList")[0].scrollHeight);

					socket.send( $.trim($("#messageText").val()) );
					$("#messageText").val('');
					$("#messageText").prop('disabled', true);
					console.log("sendMessage button was clicked");
				}
				else
					$("#messageText").focus();
	 
			}

			$("#btnRefresh").on("click", function() {
				$("#messageText").prop('disabled', true);
				$("#messageList").html('<ul id="list"></ul>');
				$("#messageList").addClass("w3-light-gray");
				console.log("sending empty message ''");
				socket.send('');
			});

	//	});
		
		// The following function will process the output from python.
		function processOutput(message) {
			var flag  = message['flag'];
			console.log("Flag is :: ", flag);
			
			var actual_content = message['response'];
			console.log("Actual COntent :: ",actual_content );
			
			if(flag == "STRING"){
				displayOutput(actual_content);
			}else if(flag == "LIST") {
				var str = "Our options are :: <li></li>";
				var counter = 0;
				for(var i in actual_content){
					counter = parseInt(i) + 1;
					str += '<li style="padding-left: 2cm;"> '+counter +") "+ actual_content[i] + "</li>";
				}
				displayOutput(str);
			}else if(flag == "DICT"){
				var str = "Your status is :: <li> </li>";
				str += '<li style="padding-left: 3cm;"> <font color="red"> '+"Package No :: </font>"+ actual_content['code'] + "</li>";
				str += '<li style="padding-left: 3cm;"> <font color="red">'+"Helpline :: </font>"+ actual_content['notification']['text'] + "</li>";
				str += '<li style="padding-left: 3cm;"> <font color="red">'+"Current Status :: </font>"+ actual_content['current_status'] + "</li>";
				displayOutput(str);
				
			}else{
				console.log("Error :: Server has send wrong data. Flag is missing.");
				displayOutput("Some Technical Fault has occured. Sorry For the inconvenience.")
			}
				
		}
		
		
		// This function will just display a string message in chatBot
		function displayOutput(display_text) {
			var dNow = new Date();
			time = dNow.getHours() + ':' + dNow.getMinutes() + ':' + dNow.getSeconds();
			$("#messageList").append( '<ul id="responseChat"><font color="gray"> ' + time + ' </font><img src="static/images/server_image.jpg" style="height:22px;width:23px;"> ' +display_text+ '</ul>');
			$("#messageList").scrollTop($("#messageList")[0].scrollHeight);
			$("#messageList").removeClass("w3-light-gray");
			$("#messageText").prop('disabled', false);
			$("#messageText").focus();
			console.log("message displayed is: " + display_text);
		}
		
		
		$('#file1').click(function(e){
			e.preventDefault();
			if(!uploadFileFlag){
				$('#browse').click();
			}else {
				uploadFileFlag = false;
				input_file_name = "";
				$(".attachment").attr('src',"./static/images/Attachment.png");
				$('#messageText').text("");
			}					
			//document.getElementById('browse').click();
		});
		
		
		$('input[name="fileUpload"]').change(function(){
			input_file_name = $('input[type=file]').val().split('\\').pop();			
			var ext = input_file_name.substring(input_file_name.lastIndexOf('.'),input_file_name.length);	
			console.log(input_file_name);
			console.log(ext);			
			$('#messageText').text(input_file_name);
			uploadFileFlag = true;
			$(".attachment").attr('src',"./static/images/close.png");
		});
		
		
		function uploadPictures(){
			if(input_file_name != ""){
				var dNow = new Date();
				time = dNow.getHours() + ':' + dNow.getMinutes() + ':' + dNow.getSeconds();
				$("#messageList").append( '<ul><font color="gray"> ' + time + ' </font><img src="static/images/client-icon.png" style="height:22px;width:23px;">'+
					'<font color="red">You: </font> <a href="static/uploadedImage/'+input_file_name+'"><u>' +$("#messageText").val()+ '</u></a></ul>');
				$("#messageList").scrollTop($("#messageList")[0].scrollHeight);
			}			
		}
		
		
		
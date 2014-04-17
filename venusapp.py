from flask import Flask, request, url_for
app = Flask(__name__)

import urllib, urllib2
import json
import random

API_KEY = ''

def get_latest_value():
  """
  This queries the thingtweet API and returns the most recent
  value and timestamp.
  """
  req = urllib2.Request('https://thingspeak.com/channels/11513/feed.json')
  response = urllib2.urlopen(req)
  blob = response.read()
  data = json.loads(blob)
  last_updated = data["channel"]["updated_at"]
  last_value = data["feeds"][-1]['field1']
  return last_updated, last_value

def get_moisture_msg(last_value):
	if last_value < 300 :
		message = "Dry"
	elif last_value < 350 :
		message = "Fair"
	elif last_value < 400 :
		message = "Moist" 
	elif last_value >= 400 :
	 	message = "Saturated"
	else :
		message = "Error"	
	return message; 


def get_color(last_value):
	if last_value < 300 :
		color = "red"
	elif last_value < 350 :
		color = "yellow"
	elif last_value < 400 :
		color = "blue"
	elif last_value >= 400 :
	 	color = "green"
	else :
		color = "white"
	return color; 
	
def emergency_update(last_value):
	if last_value < 350:
		emergency_message = "@rich_rizzo URGENT! WATER ME, PLEASE." 
		return emergency_message; 
	
	
def random_update(last_value):
	random_value = random.randint(1,5)
	if last_value <= 350:
		if random_value == 1:
			update_message = "So...very... thirsty."
		elif random_value == 2:
			update_message = "A little parched here."
		elif random_value == 3:
			update_message = "I was going to make a joke, but I think it would come off DRY."
		elif random_value == 4:
			update_message = "You're killing me."
		elif random_value == 5:
			update_message = "I knew California was in a drought, but I didn't think it was this bad."
	elif last_value > 350 :
		if random_value == 1: 
			update_message = "If H20 is the formula for water, what is the formula for ice?.. H20 Cubed."
		elif random_value == 2:
			update_message = "What did the sink say to the water faucet? ... You're a real drip." 
		elif random_value == 3: 
			update_message = "How do people swimming in the ocean say hi to ea other? They wave!"
		elif random_value == 4:
			update_message = "Is this soil Duncan Heinz? It's so moist!"
		elif random_value == 5:
			update_message = "Swampy and wet. Just the way I like it." 
	return update_message;
		
@app.route('/twupdate', methods=['POST', 'GET'])
def post_to_twitter():
  # grab latest value, pack into a tweet-sized message
  last_updated, last_value = get_latest_value()
  status = get_moisture_msg(int(last_value))
  random_msg = random_update(int(last_value))
  username = request.args.get('username', None)
  
  if username is not None:
    status = """
	  @{username}: {message}. ({quality}, {moisture} at {measured_time})
	  """.format(username=username, message=random_msg, quality=status,  moisture=last_value, measured_time=last_updated)
  else:
	  status = """
		{message}. ({quality}, {moisture} at {measured_time})
	  """.format(message=random_msg, quality=status,  moisture=last_value, measured_time=last_updated)

  # make POST request to thingtweet API with tweet
  url = 'http://api.thingspeak.com/apps/thingtweet/1/statuses/update'
  data = urllib.urlencode({
  	'api_key':API_KEY,
  	'status':status
  })
  
  # print success value and what was tweeted
  req = urllib2.Request(url, data)
  response = urllib2.urlopen(req)  
  outcome = """
  	Had response type {0}. 
  	
  	Tweeted: {1}
  """.format(response.read(), status)
  return outcome
  
@app.route('/moisture')
def display_moisture():
  last_updated, last_value = get_latest_value()
  last_value = request.args.get('val', None) or last_value
  message = get_moisture_msg(int(last_value))
  color = get_color(int(last_value))

  venus_image = url_for('static', filename='vftgiflol.gif')
  gradient_image = url_for('static', filename='gradient.png')
  
  output_html = """
	<body>
	
	<div>
	<img src = "{venus_image}" alt="vftgiflol.gif"/>
	</div>
	<div style = "font-family: courier new; font-size: 15px;"><p>
	I'm Venus! It's easy eating flies <br>
	But forget to water me and I get <br>
	grumpy! <br>
	<br>
	</p>
	</div>
	<div>
	
	<div style = "font-family: courier new; font-size: 12px;">
	<br>
	My ideal moisture range: 
	</br>
	</div>
	
	<br>&nbsp; <img src = "{gradient_image}" alt="gradient guide"/>
	</br>
	<div>
	<div style = "font-family: courier new; font-size: 10px;" >&nbsp; 120% &nbsp; &nbsp;  &nbsp;  &nbsp;  &nbsp;  &nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 70% </div>
	</div>
	<br>
	</div>
	
	<div>	
		<canvas id="myCanvas" width="310" height="352" style="border:1px solid #d3d3d3;">
		Your browser does not support the HTML5 canvas tag.</canvas>
		
		
		<script type = "text/javascript">
		
			var color1 = "{color}";
			var color2 = "white";
			
		
				function kittykat() {{
				
				}}
		
		
			var moistureVal = {moisture_value};
			var calcPerc = moistureVal * .20;
			var perc = Math.floor(calcPerc);
			
			var c = document.getElementById("myCanvas");
			var ctx = c.getContext("2d");
			var grd = ctx.createLinearGradient(0, 0, 310, 352);
			grd.addColorStop(0, color1);
			grd.addColorStop(1, color2);
			ctx.fillStyle = grd;
			ctx.fillRect(0, 0, 310, 352);
			ctx.font = "54px Courier New";
			ctx.strokeText("{message}",10,75);
			ctx.font = "36px Courier New";
			ctx.strokeText(perc + "%",15,130);
			ctx.font = "16px Courier New";
			ctx.strokeText("{moisture_value}, Updated at {last_updated}", 10, 345);
					  
		</script>
	</div>
	
	<div>
		<form action="/venusapp/twupdate" method="get">
			Twitter Username: <input name="username" type="text" />
			<input value="Tweet to Me" type="submit" />
		</form>
	</div>
	
	<br/>
	
	

	</body>
    
  """.format(moisture_value=last_value, last_updated=last_updated, message=message, color=color,
  	venus_image=venus_image, gradient_image=gradient_image)
  return output_html

if __name__ == '__main__':
  app.run()

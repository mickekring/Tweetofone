import time, random, datetime, locale, os, yaml, tweepy
from gtts import gTTS
from time import strftime
from time import sleep
from tinydb import TinyDB, Query
import RPi.GPIO as GPIO

# GPIO Setting pin in- and outputs 
GPIO.setmode(GPIO.BCM)

light_pin = 25
ring_pin = 17
phone_switch_pin = 24

GPIO.setup(light_pin, GPIO.OUT)
GPIO.setup(ring_pin, GPIO.OUT)
GPIO.setup(phone_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Loading credentials
conf = yaml.safe_load(open("credentials.yml")) # External file with all credentials

# Set database
db = TinyDB('db.json') # Storing message-id's 

### VARIABLES ###

tweetList = []
twtUserName = ""
twtTextWash = ""
global num
num = 1
global num_rings
num_rings = 0

### FUNCTIONS ###

### Lights and Sound ###

def light_on():
	GPIO.output(light_pin, True)

def light_off():
	GPIO.output(light_pin, False)

def ring_on():
	GPIO.output(ring_pin, True)

def ring_off():
	GPIO.output(ring_pin, False)

def ring():
	if num_rings == 0:
		for x in range(2):
			GPIO.output(ring_pin, True)
			time.sleep(0.5)
			GPIO.output(ring_pin, False)
		num_rings = 1
	else:
		pass

### Twitter read mentions ###

def twtReadMentions():
	consumer_key = conf['twitter']['consumer_key']
	consumer_secret = conf['twitter']['consumer_secret']
	access_token = conf['twitter']['access_token']
	access_token_secret = conf['twitter']['access_token_secret']

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth)
	count = 10 # number of latest mentions to be fetched
	public_tweets = api.mentions_timeline(count = count)

	global newTweet
	newTweet = 0

	print("\n>>> Searching your Twitter mentions...\n")
	
	for tweet in public_tweets:
		twtId = tweet.id
		twtUserScreenName = tweet.user.screen_name
		twtUserName = tweet.user.name
		twtText = tweet.text
		twtTextWash = (twtText.replace("@MickeKring", "")) #removing my own twitter handle from message text
		twtUserId = tweet.user.id

		search = twtId
		idSearch = Query()
		res = db.search(idSearch.ID == search)
		
		if res != []:
			resultSearch = (int(res[0]['ID']))
		else:
			resultSearch = 0
			pass

		if twtId != resultSearch:
			print(">>> >>> Mention from: " + twtUserName)
			db.insert({'ID': twtId}) # Stores message id to database
			newTweet += 1
			tweetList.append("Ett nytt meddelande från " + (twtUserName) + "." + (twtTextWash)) #This gets sent to text-to-speech
		else:
			pass

	print("\n>>> Number of new Twitter mentions: " + str(newTweet) + "\n")

### Google Text to Speech gTTS ###

def twtTextToSpeech():
	global tweetList
	global num

	num = 1

	for twt in tweetList:
		print(">>> Tweet mention: " + twt)
		tts = gTTS((twt), lang='sv')
		tts.save(str(num) + '.mp3')
		num += 1

	tweetList = []

### PLay audio files ###

def playMessages():
	for x in range(1, num):
		#os.system("afplay " + str(x) + ".mp3") # OSX Audio player for testing purpose
		os.system("mpg321 " + str(x) + ".mp3") # Raspberry Pi Audio player

#################### MAIN PROGRRAM #################################

def Main():

	try:
		while True:
			twtReadMentions() # Check Twitter for new mentions
			twtTextToSpeech() # If mentions exists, sends to text-to-speech which creates mp3s of the mentions
			
			if GPIO.input(phone_switch_pin) == True and if newTweet > 0: # If phone is ON the hook AND there are new mentions
				print("\n>>> Waiting for phone to be picked up\n")
				
				while GPIO.input(phone_switch_pin) == True: # As long as you don't lift the phone off the hook
					light_on() # Turns the light on
					ring() # Rings the phone
				else: # When you lift the phone off the hook
					time.sleep(2) # Wait before playing tweets
					playMessages() # Plays the created mp3s
					light_off()
					num_rings = 0 # Resets ringing functions
			
			else:
				pass
			
			time.sleep(10) # Wait for X seconds before running the loop again

	finally: 
		print("\n>>> Cleaning up GPIO pins...")
		GPIO.cleanup() # Clean up GPIO pins when quitting program

if __name__ == "__main__":
	Main()

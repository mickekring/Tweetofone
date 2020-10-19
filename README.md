# Tweetofone
 Just tinkering for fun in this totally useless project, using an old phone, a Raspberry Pi and some Python code. The Pi listens for Twitter mentions and when a new one is found, the phone rings. When you pick up the phone it will read you the tweet.
 
## Files

### mainphone.py
This is the actual Python script that runs on your Raspberry Pi. Check the imports at the top and make sure to pip install the libraries that you don't have.

### Credentials.yml
This is where you put your Twitter secrets

### db.json
This is where Twitter message ID:s are being stored

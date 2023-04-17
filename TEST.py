import tweepy
import openai
import re
import os




# Authenticate to Twitter
auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"))
auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))

CONSUMER_KEY = os.getenv("TWITTER_API_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Authenticate to OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create API object
api = tweepy.API(auth)

# Set up stream listener to respond to replies
class ReplyStreamListener(tweepy.Stream):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, target_tweet_id):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.target_tweet_id = target_tweet_id




    def on_status(self, status):
        # If the tweet is a reply to our target tweet
        if status.in_reply_to_status_id == self.target_tweet_id:
            # Get the text of the reply and remove the "@username" mention
            reply_text = re.sub(r"^@\w+\s+", "", status.text)

            # Generate multiple options for what to tweet using GPT-3
            prompt = f"What should I tweet in response to '{reply_text}'?"
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=60,
                n=3,
                stop=None,
                temperature=0.5,
            )

            # Print the generated options
            print(f"Generated options for '{reply_text}':")
            for i, option in enumerate(response.choices):
                print(f"{i+1}. {option.text.strip()}")

            # Ask the user which option they want to tweet
            choice = input("Which option should I tweet? ")

            # If the user chose an option, confirm and tweet it
            if choice.isdigit() and int(choice) <= len(response.choices):
                tweet = response.choices[int(choice)-1].text.strip()
                confirm = input(f"Tweet '{tweet}'? (y/n) ")
                if confirm.lower() == "y":
                    api.update_status(tweet, in_reply_to_status_id=status.id)
                    print(f"Tweeted '{tweet}' in response to '{reply_text}'")

# Start the stream listener
TARGET_TWEET_ID = 1647684175041007616
stream_listener = ReplyStreamListener(target_tweet_id=TARGET_TWEET_ID, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
stream = tweepy.Stream(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
stream.filter(track=[f"@MissAlyKatt"])


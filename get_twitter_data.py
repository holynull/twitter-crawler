import tweepy
import csv
from dotenv import load_dotenv
import pathlib
import sys
import argparse
import os

if getattr(sys, 'frozen', False):
    script_location = pathlib.Path(sys.executable).parent.resolve()
else:
    script_location = pathlib.Path(__file__).parent.resolve()
load_dotenv(dotenv_path=script_location / '.env')

parser = argparse.ArgumentParser(description='Get Twitter data')
parser.add_argument('-u', '--userName',
                    help="Twitter's user name")
args = parser.parse_args()
userName = args.userName


def get_twitter_auth():
    api_key = os.getenv("TWITTER_API_KEY")
    api_key_secret = os.getenv("TWITTER_API_KEY_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth

def get_twitter_client():
    auth = get_twitter_auth()
    client = tweepy.API(auth, wait_on_rate_limit=True)
    return client

def fetch_all_tweets(username):
    client = get_twitter_client()
    all_tweets = []

    # 每次请求最多可以获取200条推文
    for page in tweepy.Cursor(client.user_timeline, screen_name=username, count=200, tweet_mode='extended').pages():
        all_tweets.extend(page)

    return all_tweets

def save_tweets_to_csv(tweets, file_name="tweets.csv"):
    with open(file_name, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["User", "Tweet", "Time","Retweet","Favorite"])

        for tweet in tweets:
            writer.writerow(
                [tweet.user.screen_name, tweet.full_text, tweet.created_at,tweet.retweet_count,tweet.favorite_count])


if __name__ == "__main__":
    all_tweets = fetch_all_tweets(userName)
    save_tweets_to_csv(all_tweets, f"{userName}_tweets.csv")

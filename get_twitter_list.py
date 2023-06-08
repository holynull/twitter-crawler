import tweepy
import csv
from dotenv import load_dotenv
import pathlib
import sys
import argparse
import os
import logging

logging.basicConfig(level=logging.INFO)

if getattr(sys, 'frozen', False):
    script_location = pathlib.Path(sys.executable).parent.resolve()
else:
    script_location = pathlib.Path(__file__).parent.resolve()
load_dotenv(dotenv_path=script_location / '.env')

parser = argparse.ArgumentParser(description='Get Twitter data')
parser.add_argument('-l', '--list_id',
                    help="Twitter list id")
args = parser.parse_args()
list_id = args.list_id


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

def get_members_of_list(list_id: int)->list[any]:
    client = get_twitter_client()
    list_members = []
    for member in tweepy.Cursor(client.get_list_members,count=200, list_id=list_id).pages():
        list_members.extend(member)
    return list_members

def fetch_all_tweets(user_name):
    client = get_twitter_client()
    all_tweets = []

    # 每次请求最多可以获取200条推文
    for page in tweepy.Cursor(client.user_timeline, screen_name=user_name, count=200, tweet_mode='extended').pages():
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
    members=get_members_of_list(list_id=list_id)
    logging.info(f"The list {list_id} has {len(members)} members.")
    for m in members:
        logging.info(f"Start get tweets of user {m.screen_name}")
        all_tweets = fetch_all_tweets(user_name=m.screen_name)
        save_tweets_to_csv(all_tweets, f"{m.screen_name}_tweets.csv")
    

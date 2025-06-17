import os
import requests
import time

TWITTER_USERNAME = "ape_mag"
BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
TELEGRAM_TOPIC_ID = os.environ["TELEGRAM_TOPIC_ID"]
LAST_TWEET_FILE = "last_tweet_id.txt"

def get_latest_tweet_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    user_resp = requests.get(url, headers=headers)
    user_resp.raise_for_status()
    user_id = user_resp.json()["data"]["id"]

    url = f"https://api.twitter.com/2/users/{user_id}/tweets?exclude=retweets,replies&max_results=5&tweet.fields=created_at"
    tweet_resp = requests.get(url, headers=headers)
    tweet_resp.raise_for_status()
    tweets = tweet_resp.json().get("data", [])
    return tweets[0]["id"], tweets[0]["text"] if tweets else (None, None)

def read_last_tweet_id():
    if not os.path.exists(LAST_TWEET_FILE):
        return None
    with open(LAST_TWEET_FILE, "r") as f:
        return f.read().strip()

def write_last_tweet_id(tweet_id):
    with open(LAST_TWEET_FILE, "w") as f:
        f.write(tweet_id)

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "message_thread_id": int(TELEGRAM_TOPIC_ID),
        "text": text,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, data=payload)
    resp.raise_for_status()

def main():
    while True:
        try:
            tweet_id, tweet_text = get_latest_tweet_id(TWITTER_USERNAME)
            last_id = read_last_tweet_id()
            if tweet_id and tweet_id != last_id:
                tweet_url = f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet_id}"
                send_to_telegram(f"New tweet from @{TWITTER_USERNAME}:
{tweet_url}")
                write_last_tweet_id(tweet_id)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
import re
import praw
import json
import pprint
import urllib.request

IMAGE_FORMATS = r'(?i)\.(jpg|png|gif|jpeg)$'

# reads config file
with open('config.json') as fi:
    config = json.load(fi)

# sets up praw instance
praw_instance = praw.Reddit(
    client_id=config['praw_auth']['client_id'],
    client_secret=config['praw_auth']['client_secret'],
    user_agent=config['praw_auth']['user_agent'])

subreddit = praw_instance.subreddit(config['settings']['default_sub'])

for submission in subreddit.hot(limit=config['settings']['cache_size']):
    print(submission.title)
    url = submission.url.rsplit('/',1)[-1]
    if re.search(IMAGE_FORMATS, url): # starts download only for image files
        urllib.request.urlretrieve(submission.url, config['settings']['cache_location'] + url)

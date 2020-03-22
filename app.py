from PIL import Image
import re
import os
import praw #pip install praw
import json
import urllib.request #pip install urllib

IMAGE_FORMATS = r'(?i)\.(jpg|png|gif|jpeg)$'
os.system('clear')
print('Imagine Reddit Image Downloader\n' + "*" * 20 + "\n")

# reads config file
with open('config.json') as fi:
    config = json.load(fi)

if (not os.path.exists(config['settings']['cache_location'])):
    os.system('mkdir ' + config['settings']['cache_location'])

# sets up praw instance
praw_instance = praw.Reddit(
    client_id=config['praw_auth']['client_id'],
    client_secret=config['praw_auth']['client_secret'],
    user_agent=config['praw_auth']['user_agent'])

current_subreddit = config['settings']['default_sub']
subreddit = praw_instance.subreddit(current_subreddit)

cache_set = set()
cache_name = config['settings']['cache_location'] +  "/" + current_subreddit + '.cache'

try:
    with open(cache_name, 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]
            # add item to the list
            cache_set.add(currentPlace)
except FileNotFoundError:
    print("No cache file found, creating new one")

def writeCache():
    with open(cache_name, 'w') as filehandle:
        for listitem in cache_set:
            filehandle.write('%s\n' % listitem)


for submission in subreddit.hot(limit=None):
    url = submission.url.rsplit('/',1)[-1]
    if not(url in cache_set):
        if re.search(IMAGE_FORMATS, url): # starts download only for image files
            print(submission.title)
            image_directory = config['settings']['cache_location'] + url # the directory for each image
            urllib.request.urlretrieve(submission.url, image_directory) # download image
            img = Image.open(image_directory) # create PIL image
            img.show()
            selection = input("Save (s), next (n), quit (q): ")

            if (selection == 's'):
                print('Saved to: ' + image_directory)
            elif (selection == 'n'):
                cache_set.add(url)
                writeCache()
                os.system('rm ' + image_directory)
            elif (selection == 'q'):
                save_fi = input("Save current image (y/n): ")
                if (save_fi == 'n'):
                    os.system('rm ' + image_directory)
                writeCache()
                exit()

            print("*" * 20 + "\n")
        

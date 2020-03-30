import urllib.request #pip install urllib
import praw #pip install praw
import json
import re
import os

IMAGE_FORMATS = r'(?i)\.(jpg|png|tiff|jpeg)$'

class Imagine:
    def __init__(self, config_path):
        self.config = self.readConfig(config_path)
        self.praw_instance = praw.Reddit(
            client_id=self.config['praw_auth']['client_id'],
            client_secret=self.config['praw_auth']['client_secret'],
            user_agent=self.config['praw_auth']['user_agent'])
        if (not os.path.exists(self.config['settings']['cache_location'])):
            os.system('mkdir ' + self.config['settings']['cache_location'])

    def createSubredditInstance(self, current_subreddit=None):
        if (current_subreddit is None):
            current_subreddit = self.config['settings']['default_sub']
        self.subreddit = self.praw_instance.subreddit(current_subreddit)
        self.cache_set = set()
        self.cache_name = (self.config['settings']['cache_location'] +  
            "/" + current_subreddit + '.cache')
        self.readCache(self.cache_name)

    def generateSubmissionIter(self):
        self.submission_iterator = iter(self.subreddit.hot(limit=None))

    def imageSelection(self):
        self.submission = next(self.submission_iterator)
        self.url = self.submission.url.rsplit('/',1)[-1]
        self.image_directory = self.config['settings']['cache_location'] + self.url # the directory for each image
        if not(self.url in self.cache_set) and not(os.path.exists(self.image_directory)):
            if re.search(IMAGE_FORMATS, self.url): # starts download only for image files
                try:
                    urllib.request.urlretrieve(self.submission.url, self.image_directory) # download image
                    return self.image_directory
                except urllib.error.HTTPError:
                    print("Cannot Print Image, forbidden")
                    self.cache_set.add(self.url)
                    self.writeCache()
                    return None
    
    def getSubmissionInfo(self):
        return (self.submission.title, self.submission.author, self.submission.url)
        
    def imageOption(self, selection):
        if (selection == 'pass'):
            return
        elif (selection == 'save'):
            print('Saved to: ' + self.image_directory)
        elif (selection == 'next'):
            self.cache_set.add(self.url)
            self.writeCache()
            os.system('rm ' + self.image_directory)
        elif (selection == 'quit'):
            os.system('rm ' + self.image_directory)
            self.writeCache()
            exit()
        print("*" * 20 + "\n")

    def readConfig(self, config_path):
        with open(config_path) as fi:
            config = json.load(fi)
        return config

    def readCache(self, cache_name):
        try:
            with open(cache_name, 'r') as filehandle:
                for line in filehandle:
                    # remove linebreak which is the last character of the string
                    currentPlace = line[:-1]
                    # add item to the list
                    self.cache_set.add(currentPlace)
        except FileNotFoundError:
            print("No cache file found, creating new one")

    def writeCache(self):
        with open(self.cache_name, 'w') as filehandle:
            for listitem in self.cache_set:
                filehandle.write('%s\n' % listitem)

from PIL import Image
import re
import os
import praw #pip install praw
import json
import urllib.request #pip install urllib

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

    def subredditInstance(self, current_subreddit=None):
        '''
        Initalizes a Subreddit Instance
        '''
        if (current_subreddit is None):
            current_subreddit = self.config['settings']['default_sub']
        self.subreddit = self.praw_instance.subreddit(current_subreddit)
        self.cache_set = set()
        self.cache_name = (self.config['settings']['cache_location'] +  
            "/" + current_subreddit + '.cache')
        self.readCache(self.cache_name)

    def imageCycle(self):
        for submission in self.subreddit.hot(limit=None):
            url = submission.url.rsplit('/',1)[-1]
            image_directory = self.config['settings']['cache_location'] + url # the directory for each image
            if not(url in self.cache_set) and not(os.path.exists(image_directory)):
                if re.search(IMAGE_FORMATS, url): # starts download only for image files
                    print(submission.title)
                    try:
                        urllib.request.urlretrieve(submission.url, image_directory) # download image
                        img = Image.open(image_directory) # create PIL image
                        img.show()
                        selection = input("Save (s), next (n), quit (q): ")

                        if (selection == 's'):
                            print('Saved to: ' + image_directory)
                        elif (selection == 'n'):
                            self.cache_set.add(url)
                            self.writeCache()
                            os.system('rm ' + image_directory)
                        elif (selection == 'q'):
                            save_fi = input("Save current image (y/n): ")
                            if (save_fi == 'n'):
                                os.system('rm ' + image_directory)
                                self.cache_set.add(url)
                            self.writeCache()
                            exit()
                    except urllib.error.HTTPError:
                        print("Cannot Print Image, forbidden")
                        self.cache_set.add(url)
                        self.writeCache()
                
                    print("*" * 20 + "\n")


    def readConfig(self, config_path):
        '''
        Reads configuration folder
        '''
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



        

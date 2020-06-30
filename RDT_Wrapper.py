from sys import exit
import urllib.request
import urllib.error
import praw
import json
import re
import os

IMAGE_FORMATS = r'(?i)\.(jpg|png|tiff|jpeg)$'


def read_config(config_path):
    with open(config_path) as fi:
        config = json.load(fi)
    return config


class RDT_Wrapper:
    def __init__(self, config_path):
        self.config = None
        self.praw_instance = None
        self.subreddit = None
        self.cache_set = None
        self.cache_name = None
        self.submission_iterator = None
        self.submission = None
        self.url = None
        self.image_directory = None

        self.config = read_config(config_path)
        self.praw_instance = praw.Reddit(
            client_id=self.config['praw_auth']['client_id'],
            client_secret=self.config['praw_auth']['client_secret'],
            user_agent=self.config['praw_auth']['user_agent'])
        if not os.path.exists(self.config['settings']['cache_location']):
            os.system('mkdir ' + self.config['settings']['cache_location'])
        print('PRAW instance created')

    def create_subreddit_instance(self, current_subreddit=None):
        if current_subreddit is None:
            current_subreddit = self.config['settings']['default_sub']
        self.subreddit = self.praw_instance.subreddit(current_subreddit)
        self.cache_set = set()
        self.cache_name = (self.config['settings']['cache_location'] +
                           "/" + current_subreddit + '.cache')
        self.read_cache(self.cache_name)

    def generate_submission_iter(self, sort):
        if sort == 'hot':
            self.submission_iterator = iter(self.subreddit.hot(limit=None))
        elif sort == 'new':
            self.submission_iterator = iter(self.subreddit.new(limit=None))
        elif sort == 'rising':
            self.submission_iterator = iter(self.subreddit.rising(limit=None))
        elif sort == 'top (hour)':
            self.submission_iterator = iter(self.subreddit.top(time_filter='hour', limit=None))
        elif sort == 'top (day)':
            self.submission_iterator = iter(self.subreddit.top(time_filter='day', limit=None))
        elif sort == 'top (week)':
            self.submission_iterator = iter(self.subreddit.top(time_filter='week', limit=None))
        elif sort == 'top (month)':
            self.submission_iterator = iter(self.subreddit.top(time_filter='month', limit=None))
        elif sort == 'top (year)':
            self.submission_iterator = iter(self.subreddit.top(time_filter='year', limit=None))
        elif sort == 'top (all time)':
            self.submission_iterator = iter(self.subreddit.top(time_filter='all', limit=None))
        print("sorting by: " + sort)

    def image_selection(self):
        self.submission = next(self.submission_iterator)
        self.url = self.submission.url.rsplit('/', 1)[-1]
        self.image_directory = self.config['settings']['cache_location'] + self.url  # the directory for each image
        if not (self.url in self.cache_set) and not (os.path.exists(self.image_directory)):
            if re.search(IMAGE_FORMATS, self.url):  # starts download only for image files
                try:
                    urllib.request.urlretrieve(self.submission.url, self.image_directory)  # download image
                    return self.image_directory
                except urllib.error.HTTPError:
                    print("Cannot Print Image, forbidden")
                    self.cache_set.add(self.url)
                    self.write_cache()
                    return None

    def get_submission_info(self):
        return self.submission.title, self.submission.author, self.submission.shortlink

    def image_option(self, selection):
        if selection == 'first':
            return
        elif selection == 'pass':
            os.system('rm ' + self.image_directory)
            return
        elif selection == 'save':
            print('Saved to: ' + self.image_directory)
        elif selection == 'next':
            self.cache_set.add(self.url)
            self.write_cache()
            os.system('rm ' + self.image_directory)
        elif selection == 'quit':
            os.system('rm ' + self.image_directory)
            self.write_cache()
            print('quitting program...')
            exit()
        print("*" * 20 + "\n")

    def read_cache(self, cache_name):
        try:
            with open(cache_name, 'r') as fi:
                for line in fi:
                    # remove linebreak which is the last character of the string
                    current_place = line[:-1]
                    # add item to the list
                    self.cache_set.add(current_place)
        except FileNotFoundError:
            print("No cache file found, creating new one")

    def write_cache(self):
        with open(self.cache_name, 'w') as fi:
            for item in self.cache_set:
                fi.write('%s\n' % item)

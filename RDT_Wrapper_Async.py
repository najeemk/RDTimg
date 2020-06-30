from sys import exit
from queue import Queue
import requests
import praw
import json
import re
import os

IMAGE_FORMATS = r'(?i)\.(jpg|png|tiff|jpeg)$'


def read_config(config_path):
    with open(config_path) as fi:
        config = json.load(fi)
    return config


class RDT_Wrapper_Async:
    def __init__(self, config_path):
        self.config = None
        self.praw_instance = None
        self.subreddit = None
        self.cache_set = None
        self.cache_name = None

        self.submission_iterator = None
        self.submission_queue = Queue(maxsize=10)

        self.current_submission_meta = None
        self.current_submission = None
        self.url = None
        self.current_image_directory = None

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

    def queue_images(self):
        if self.submission_queue.empty():
            while not(self.submission_queue.full()):
                submission = next(self.submission_iterator)
                if re.search(IMAGE_FORMATS, submission.url.rsplit('/', 1)[-1]):  # starts download only for image files
                    resp = requests.get(submission.url)
                    print(submission.title)
                    self.submission_queue.put([submission, resp])
                else:
                    print(submission.title + " is not an image")

    def image_selection(self):
        self.queue_images()
        self.current_submission = self.submission_queue.get()
        self.current_submission_meta = self.current_submission[0]
        self.url = self.current_submission_meta.url.rsplit('/', 1)[-1]
        self.current_image_directory = self.config['settings']['cache_location'] + self.url  # the directory for each image
        if not (os.path.exists(self.current_image_directory)):
            print(self.current_image_directory)
            return self.current_submission[1].content, self.current_image_directory
        else:
            print(not (self.url in self.cache_set) )
            print(not (os.path.exists(self.current_image_directory)))
            return None, None

    def write_image(self):
        with open(self.current_image_directory, "wb") as file:
            file.write(self.current_submission[1].content)

    def get_submission_info(self):
        return self.current_submission_meta.title, self.current_submission_meta.author, self.current_submission_meta.shortlink

    def image_option(self, selection):
        if selection == 'first' or selection == 'pass':
            return
        elif selection == 'save':
            self.write_image()
            print('Saved to: ' + self.current_image_directory)
        elif selection == 'next':
            self.cache_set.add(self.url)
            self.write_cache()
        elif selection == 'quit':
            self.write_cache()
            print('quitting program...')
            exit()
        elif selection == "debug":
            import pdb
            pdb.set_trace()
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

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QComboBox 
from PyQt5.QtGui import QPixmap
from imagine_dl import Imagine
import json

CONFIG_PATH = 'config.json'

class ImagineGui(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Imagine Image Downloader'
        self.labelImage = QLabel() # need to create this ahead of time
        self.post_title = QLabel()
        self.post_author = QLabel()

        # loads config file
        with open(CONFIG_PATH) as fi:
            self.config = json.load(fi)

        # sets up Imagine, reddit instance, and the UI
        self.download = Imagine(CONFIG_PATH)
        self.initSubredditInstance()
        self.initUI()

    def initSubredditInstance(self, subreddit=None):
        self.download.createSubredditInstance(subreddit)
        self.download.generateSubmissionIter()
        self.updateImage('pass')

    def initUI(self):
        self.setWindowTitle(self.title)
        
        # create save and next buttons
        self.save_btn = QPushButton('Save')
        self.next_btn = QPushButton('Next')

        self.save_btn.clicked.connect(lambda x: self.updateImage('save'))
        self.next_btn.clicked.connect(lambda x: self.updateImage('next'))

        # create button container and add buttons to it
        button_stack = QHBoxLayout() 
        button_stack.addWidget(self.save_btn)
        button_stack.addWidget(self.next_btn)

        # create subreddit seleciton
        subreddit_picker = QComboBox()
        subreddit_picker.addItems(self.config['settings']['subreddits'])
        subreddit_picker.activated[str].connect(self.initSubredditInstance)

        # create top section
        top_stack = QHBoxLayout()
        top_stack.addWidget(subreddit_picker)
        top_stack.addWidget(self.post_title)
        top_stack.addWidget(self.post_author)

        # create main gui containers
        v_stack = QVBoxLayout()
        v_stack.addLayout(top_stack)
        v_stack.addWidget(self.labelImage)
        v_stack.addLayout(button_stack)
        self.setLayout(v_stack)
        self.show()

    def updateImage(self, opt):
        self.download.imageOption(opt)
        path = None
        while (path is None):
            path = self.download.imageSelection()
        pixmap = QPixmap(path)
        self.labelImage.setPixmap(pixmap.scaledToWidth(640))
        submission_info = self.download.getSubmissionInfo()
        self.post_title.setText(str(submission_info[0]))
        self.post_author.setText(str(submission_info[1]))

app = QApplication([]) # application init
w = ImagineGui()
app.exec_()
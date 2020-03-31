from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QComboBox 
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from imagine_dl import Imagine
import webbrowser
import json

CONFIG_PATH = 'config.json'

class ImagineGui(QWidget):
    def __init__(self):
        super().__init__()
        # loads config file
        with open(CONFIG_PATH) as fi:
            self.config = json.load(fi)

        self.setWindowTitle('Imagine Image Downloader')
        self.window_size = (800, 450)

        # sets up Imagine, reddit instance, and the UI
        self.download = Imagine(CONFIG_PATH)

        # need to create this ahead of time
        self.labelImage = QLabel() 
        self.labelImage.setFixedSize(self.window_size[0], self.window_size[1])
        self.labelImage.setAlignment(Qt.AlignCenter)
        self.post_title = QLabel()
        self.post_author = QLabel()

        # Create the Subreddit Instance and UI
        self.initSubredditInstance()
        self.initUI()
        self.setFixedSize(self.size())

    def initSubredditInstance(self, subreddit=None):
        '''
        Creates the subreddit instance
        '''
        self.download.createSubredditInstance(subreddit)
        self.download.generateSubmissionIter()
        self.initImage('pass')

    def initUI(self):
        '''
        Creates main gui containers
        '''
        v_stack = QVBoxLayout()
        v_stack.addWidget(self.initTopBar()) # top bar
        v_stack.addWidget(self.labelImage) # image
        v_stack.addLayout(self.initBottomBar()) # bottom bar
        self.setLayout(v_stack)
        self.show()

    def initTopBar(self):
        '''
        Must be called from initUI. The stack is the highest layer, and the one returned,
        '''
        # create subreddit seleciton
        subreddit_picker = QComboBox()
        subreddit_picker.addItems(self.config['settings']['subreddits'])
        subreddit_picker.activated[str].connect(self.initSubredditInstance)

        # create sorting selection
        sorting_picker = QComboBox()
        sorting_picker.addItems(['hot', 'new', 'rising', 'top'])

        # selection layout
        selection_layout = QVBoxLayout()
        selection_layout.addWidget(subreddit_picker)
        selection_layout.addWidget(sorting_picker)

        # post information
        post_layout = QVBoxLayout()
        post_layout.addWidget(self.post_title)
        post_layout.addWidget(self.post_author)

        # create top section container
        top_stack = QHBoxLayout()
        top_stack.addLayout(post_layout)
        top_stack.addLayout(selection_layout)

        # layout hack
        sized_top_stack = QWidget()
        sized_top_stack.setLayout(top_stack)
        sized_top_stack.setMaximumWidth(self.window_size[0])

        return sized_top_stack

    def initBottomBar(self):
        '''
        Must be called from initUI
        '''
        # create save and next buttons
        open_btn = QPushButton('Open in Reddit')
        save_btn = QPushButton('Save')
        next_btn = QPushButton('Next')

        open_btn.clicked.connect(lambda x: webbrowser.open(self.submission_info[2]))
        save_btn.clicked.connect(lambda x: self.initImage('save'))
        next_btn.clicked.connect(lambda x: self.initImage('next'))

        # create button container and add buttons to it
        button_stack = QHBoxLayout() 
        button_stack.addWidget(open_btn)
        button_stack.addWidget(save_btn)
        button_stack.addWidget(next_btn)
        return button_stack


    def initImage(self, opt):
        '''
        Initializes and outputs the next image in the list
        opt: save, pass, next, quit
        '''
        self.download.imageOption(opt)
        path = None
        while (path is None):
            path = self.download.imageSelection()
        pixmap = QPixmap(path).scaled(self.window_size[0], self.window_size[1], Qt.KeepAspectRatio)
        self.labelImage.setPixmap(pixmap)
        self.submission_info = self.download.getSubmissionInfo()
        print(self.submission_info[2])
        self.post_title.setText(str(self.submission_info[0]))
        self.post_author.setText(str(self.submission_info[1]))

app = QApplication([]) # application init
w = ImagineGui()
app.exec_()

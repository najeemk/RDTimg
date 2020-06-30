from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from RDT_Wrapper_Async import RDT_Wrapper_Async
import webbrowser
import json
import sys
import os


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    From: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # noinspection PyUnresolvedReferences
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


CONFIG_PATH = resource_path('config/config.json')


# noinspection PyArgumentList
class RDTIMGGui(QWidget):
    def __init__(self):
        super().__init__()
        # loads config file
        with open(CONFIG_PATH) as fi:
            self.config = json.load(fi)

        self.setWindowTitle('RDTIMG Image Downloader')
        self.window_size = (800, 450)

        # sets up RDTIMG, Reddit instance, and the UI
        self.rdt_instance = RDT_Wrapper_Async(CONFIG_PATH)

        # need to create this ahead of time
        self.labelImage = QLabel()
        self.labelImage.setFixedSize(self.window_size[0], self.window_size[1])
        self.labelImage.setAlignment(Qt.AlignCenter)
        self.post_title = QLabel()
        self.post_author = QLabel()
        self.submission_info = None

        # Create the Subreddit Instance and UI
        self.first_run = True
        self.sorting_method = 'hot'
        self.init_subreddit_instance()
        self.init_ui()
        self.setFixedSize(self.size())

    def init_subreddit_instance(self, subreddit=None):
        """
        Creates the subreddit instance
        """
        self.rdt_instance.create_subreddit_instance(subreddit)
        self.init_sorting_instance(self.sorting_method)

    def init_sorting_instance(self, sort):
        self.sorting_method = sort
        self.rdt_instance.generate_submission_iter(sort)
        self.image_cycle('pass')

    def init_ui(self):
        """
        Creates main gui containers
        """
        v_stack = QVBoxLayout()
        v_stack.addWidget(self.init_top_bar())  # top bar
        v_stack.addWidget(self.labelImage)  # image
        v_stack.addLayout(self.init_bottom_bar())  # bottom bar
        self.setLayout(v_stack)
        self.show()

    def init_top_bar(self):
        """
        Must be called from init_ui. The stack is the highest layer, and the one returned,
        """
        # create subreddit seleciton
        subreddit_picker = QComboBox()
        subreddit_picker.addItems(self.config['settings']['subreddits'])
        subreddit_picker.activated[str].connect(self.init_subreddit_instance)

        # create sorting selection
        sorting_picker = QComboBox()
        sorting_picker.addItems(['hot', 'new', 'rising',
                                 'top (hour)', 'top (day)', 'top (week)', 'top (month)', 'top (year)',
                                 'top (all time)'])
        sorting_picker.activated[str].connect(self.init_sorting_instance)

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

    def init_bottom_bar(self):
        """
        Must be called from init_ui
        """
        # create save and next buttons
        open_btn = QPushButton('Open in Reddit')
        save_btn = QPushButton('Save')
        next_btn = QPushButton('Next')
        queue_btn = QPushButton('debug')

        open_btn.clicked.connect(lambda x: webbrowser.open(self.submission_info[2]))
        save_btn.clicked.connect(lambda x: self.image_cycle('save'))
        next_btn.clicked.connect(lambda x: self.image_cycle('next'))
        queue_btn.clicked.connect(lambda x: self.image_cycle('debug'))

        # create button container and add buttons to it
        button_stack = QHBoxLayout()
        button_stack.addWidget(open_btn)
        button_stack.addWidget(save_btn)
        button_stack.addWidget(next_btn)
        button_stack.addWidget(queue_btn)
        return button_stack

    def image_cycle(self, opt):
        """
        Initializes and outputs the next image in the list
        opt: save, first, pass, next, quit
        """
        if self.first_run:
            self.rdt_instance.image_option('first')
            self.first_run = False
        else:
            self.rdt_instance.image_option(opt)
        path = None
        img = None

        while img is None and path is None:
            img, path = self.rdt_instance.image_selection()
            print("Looking for an Image")
        print("Found Image -> Printing to Screen")
        pixmap_raw = QPixmap()
        pixmap_raw.loadFromData(img)
        pixmap = pixmap_raw.scaled(self.window_size[0], self.window_size[1], Qt.KeepAspectRatio)
        self.labelImage.setPixmap(pixmap)
        self.submission_info = self.rdt_instance.get_submission_info()
        print(self.submission_info[2])
        self.post_title.setText(str(self.submission_info[0]))
        self.post_author.setText(str(self.submission_info[1]))

    def closeEvent(self, *args, **kwargs):
        """
        Overrides: PyQt5.QtWidgets.QWidget.QWidget.closeEvent
        Deletes image when closing the event, and writes to cache
        """
        super().closeEvent(*args, **kwargs)
        self.rdt_instance.image_option('quit')


app = QApplication([])  # application init
w = RDTIMGGui()
app.exec_()
